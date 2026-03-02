import asyncio
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

FRAME_DIR = "frames"
CACHE_FILE = "ascii_frames_cache/ascii_frames.json"
WIDTH = 50
HEIGHT = 20
FPS = 2
DELAY = 0.5
CHARS = " .',:;clodxkO0KXNWM@"

FRAMES = []
active = {}


def extract_frames(video_path):
    os.makedirs(FRAME_DIR, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"fps={FPS},scale={WIDTH}:{HEIGHT}",
        f"{FRAME_DIR}/frame_%05d.png",
    ], check=True, capture_output=True)


def image_to_ascii(path):
    img = Image.open(path).convert("L")
    px = img.load()
    lines = []
    for y in range(img.height):
        line = ""
        for x in range(img.width):
            line += CHARS[px[x, y] * (len(CHARS) - 1) // 255]
        lines.append(line)
    return "\n".join(lines)


def precache_frames():
    video = "bad_apple.mp4"
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            frames = json.load(f)
        print(f"Loaded {len(frames)} cached frames")
        return frames

    if not os.path.exists(video):
        print(f"Download Bad Apple and save as {video}")
        print("e.g.: yt-dlp -o bad_apple.mp4 'https://www.youtube.com/watch?v=FtutLA63Cp8'")
        sys.exit(1)

    print("Extracting frames with ffmpeg...")
    extract_frames(video)

    paths = sorted(Path(FRAME_DIR).glob("frame_*.png"))
    frames = []
    for i, p in enumerate(paths):
        frames.append(image_to_ascii(p))
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(paths)}")

    with open(CACHE_FILE, "w") as f:
        json.dump(frames, f)
    print(f"Generated and cached {len(frames)} frames")
    return frames


RATE_SEM = asyncio.Semaphore(20)

async def send_draft(session, chat_id, draft_id, text):
    for attempt in range(3):
        try:
            async with RATE_SEM:
                async with session.post(f"{API}/sendMessageDraft", json={
                    "chat_id": chat_id,
                    "draft_id": draft_id,
                    "text": text,
                    "parse_mode": "HTML",
                }, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    data = await resp.json()
                    if resp.status == 429:
                        retry_after = data.get("parameters", {}).get("retry_after", 1)
                        print(f"[429] chat={chat_id} retry_after={retry_after}s attempt={attempt+1}")
                        await asyncio.sleep(retry_after)
                        continue
                    if not data.get("ok"):
                        print(f"[ERR] chat={chat_id} draft: {data}")
                    return data
        except asyncio.TimeoutError:
            print(f"[TIMEOUT] chat={chat_id} draft attempt={attempt+1}")
            await asyncio.sleep(0.5)
        except aiohttp.ClientError as e:
            print(f"[NET] chat={chat_id} draft attempt={attempt+1}: {e}")
            await asyncio.sleep(0.5)
    print(f"[FAIL] chat={chat_id} draft gave up after 3 attempts")
    return None



async def send_message(session, chat_id, text):
    for attempt in range(3):
        try:
            async with session.post(f"{API}/sendMessage", json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            }, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json()
                if resp.status == 429:
                    retry_after = data.get("parameters", {}).get("retry_after", 1)
                    print(f"[429] chat={chat_id} msg retry_after={retry_after}s attempt={attempt+1}")
                    await asyncio.sleep(retry_after)
                    continue
                if not data.get("ok"):
                    print(f"[ERR] chat={chat_id} msg: {data}")
                return data
        except asyncio.TimeoutError:
            print(f"[TIMEOUT] chat={chat_id} msg attempt={attempt+1}")
            await asyncio.sleep(0.5)
        except aiohttp.ClientError as e:
            print(f"[NET] chat={chat_id} msg attempt={attempt+1}: {e}")
            await asyncio.sleep(0.5)
    print(f"[FAIL] chat={chat_id} msg gave up after 3 attempts")
    return None


async def play(session, chat_id):
    gen = id(asyncio.current_task())
    active[chat_id] = gen
    draft_id = random.randint(1, 2**31)
    total = len(FRAMES)

    for i, frame in enumerate(FRAMES):
        if active.get(chat_id) != gen:
            return
        progress = f"▶ {i+1}/{total}"
        await send_draft(session, chat_id, draft_id, f"<pre>{frame}\n{progress}</pre>")
        await asyncio.sleep(DELAY)

    if active.get(chat_id) == gen:
        await send_message(session, chat_id, "Bad Apple!! — Fin")
        active.pop(chat_id, None)


async def main():
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        offset = 0
        print(f"Bot started! {len(FRAMES)} frames, {DELAY:.1f}s/frame")

        while True:
            async with session.get(f"{API}/getUpdates", params={
                "offset": offset, "timeout": 30,
            }) as resp:
                data = await resp.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                if msg.get("text") == "/start":
                    asyncio.create_task(play(session, msg["chat"]["id"]))


FRAMES = precache_frames()
asyncio.run(main())