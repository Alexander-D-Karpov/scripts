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
FPS = 5
DELAY = 0.2
CHARS = " .,:;+*?%S#@"

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


RATE_SEM = asyncio.Semaphore(25)

async def send_draft(session, chat_id, draft_id, text):
    async with RATE_SEM:
        async with session.post(f"{API}/sendMessageDraft", json={
            "chat_id": chat_id,
            "draft_id": draft_id,
            "text": text,
            "parse_mode": "HTML",
        }) as resp:
            return await resp.json()


async def send_message(session, chat_id, text):
    async with session.post(f"{API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }) as resp:
        return await resp.json()


async def play(session, chat_id):
    gen = id(asyncio.current_task())
    active[chat_id] = gen
    draft_id = random.randint(1, 2**31)
    prev = None
    start = asyncio.get_event_loop().time()

    for i, frame in enumerate(FRAMES):
        if active.get(chat_id) != gen:
            return
        if frame != prev:
            await send_draft(session, chat_id, draft_id, f"<pre>{frame}</pre>")
            prev = frame
        target = start + (i + 1) * DELAY
        now = asyncio.get_event_loop().time()
        if target > now:
            await asyncio.sleep(target - now)

    if active.get(chat_id) == gen:
        await send_message(session, chat_id, f"<pre>{FRAMES[-1]}</pre>\n\n🍎 Bad Apple!! — Fin")
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