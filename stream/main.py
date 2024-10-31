import asyncio
import atexit
import os
import queue
import random
import signal
import subprocess
import threading
from typing import Optional

import aiohttp
import requests
import time
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from io import BytesIO
from colorthief import ColorThief
from urllib.parse import urljoin

from qrcode.main import QRCode
from telegram import Update
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters,
    CommandHandler,
    Application,
)


class StreamBot:
    def __init__(self, api_host):
        self.api_host = api_host.rstrip("/")
        self.queue = None
        self.admin_ids = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

        # Initialize bot
        self.app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

        # Add handlers
        self.app.add_handler(CommandHandler("next", self.next_song))
        self.app.add_handler(CommandHandler("play", self.play_song))
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.search_song)
        )

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids

    async def start(self, update, context):
        await update.message.reply_text(
            "Welcome to the stream bot. Use /play <song_slug> to play a song."
            " Use /help for more information."
            " Use /next to skip to the next song."
        )

    async def help(self, update, context):
        await update.message.reply_text(
            "Use /play <song_slug> to play a song."
            " Use /next to skip to the next song."
        )

    async def next_song(self, update, context):
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text(
                "You're not authorized to control the stream."
            )
            return

        if self.queue:
            self.queue.put({"action": "next"})
            await update.message.reply_text("Skipping to next song...")

    async def play_song(self, update, context):
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text(
                "You're not authorized to control the stream."
            )
            return

        if not context.args:
            await update.message.reply_text("Usage: /play <song_slug>")
            return

        slug = context.args[0]
        if self.queue:
            self.queue.put({"action": "play", "slug": slug})
            await update.message.reply_text(f"Playing song with slug: {slug}")

    async def search_song(self, update, context):
        query = update.message.text

        try:
            response = requests.get(
                f"{self.api_host}/api/v1/music/song/?search={query}"
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                await update.message.reply_text("No songs found.")
                return

            songs = data["results"][:5]  # Limit to 5 results
            response_text = "Found songs:\n"
            for song in songs:
                authors = ", ".join(a["name"] for a in song["authors"])
                response_text += (
                    f"\n{song['name']} by {authors}\nSlug: {song['slug']}\n"
                )

            response_text += "\nUse /play <slug> to play a song"
            await update.message.reply_text(response_text)
        except Exception as e:
            await update.message.reply_text(f"Error searching for songs: {str(e)}")

    def run(self):
        self.app.run_polling(allowed_updates=True)


def run_stream_service(service):
    """Function to run stream service in a separate thread"""
    try:
        service.stream()
    except Exception as e:
        print(f"Stream service error: {e}")


class StreamService:
    def __init__(self, api_host, rtmp_urls, web_host):
        self.qr_color = None
        self.bg_color = None
        self.api_host = api_host.rstrip("/")
        self.web_host = web_host.rstrip("/")
        self.rtmp_urls = rtmp_urls
        self.overlay_path = "/tmp/overlay.png"
        self.session = requests.Session()
        self.command_queue = queue.Queue()
        self.current_processes = []  # List of current FFmpeg processes
        self.play_random_songs = True  # Flag to control random song playback

        # Automatically find a font that supports Unicode characters
        self.font_path = self.find_font()
        if not self.font_path:
            raise FileNotFoundError("No suitable font file found on the system.")

    def find_font(self):
        possible_paths = [
            "/usr/share/fonts/nerd-fonts-git/TTF/DejaVu Sans Mono Nerd Font Complete Mono.ttf",  # Linux
            "/usr/share/fonts/noto/NotoSans-Regular.ttf",  # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",  # Linux
            "/Library/Fonts/Arial Unicode.ttf",  # macOS
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
            "C:\\Windows\\Fonts\\Arial.ttf",  # Windows alternative
        ]

        for path in possible_paths:
            if os.path.isfile(path):
                return path
        return None

    def get_full_url(self, path):
        if not path:
            return None
        if path.startswith("http"):
            return path
        return urljoin(self.api_host, path)

    def get_song_slugs(self):
        retries = 3
        while retries > 0:
            try:
                response = self.session.get(f"{self.api_host}/api/v1/music/song/slugs/")
                response.raise_for_status()
                return response.json()["songs"]
            except requests.exceptions.RequestException as e:
                print(f"Failed to get slugs: {e}")
                retries -= 1
                time.sleep(5)
        return []

    def get_song_info(self, slug):
        retries = 3
        while retries > 0:
            try:
                response = self.session.get(f"{self.api_host}/api/v1/music/song/{slug}")
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Failed to get song info: HTTP {response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Failed to get song info: {e}")
                retries -= 1
                time.sleep(5)
        raise Exception(f"Failed to get song info after retries: {slug}")

    def get_image_from_url(self, url):
        if not url:
            return None
        full_url = self.get_full_url(url)
        try:
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image from {full_url}: {e}")
            return None
        except UnidentifiedImageError as e:
            print(f"Error opening image from {full_url}: {e}")
            return None

    def get_dominant_colors(self, image):
        try:
            img_file = BytesIO()
            image.save(img_file, "PNG")
            img_file.seek(0)
            color_thief = ColorThief(img_file)
            palette = color_thief.get_palette(color_count=2, quality=1)

            if len(palette) >= 2:
                return palette[0], palette[1]
            elif len(palette) == 1:
                return palette[0], (200, 200, 200)
            else:
                return (30, 30, 30), (200, 200, 200)
        except Exception as e:
            print(f"Error extracting colors: {e}")
            return (30, 30, 30), (200, 200, 200)

    def get_song_image(self, song_info):
        # Try track image -> album image -> author image
        for img_source in [
            song_info.get("image"),
            song_info.get("album", {}).get("image_cropped"),
            song_info.get("authors", [{}])[0].get("image_cropped"),
        ]:
            if img_source:
                img = self.get_image_from_url(img_source)
                if img:
                    return img
        return None

    def create_qr(self, album_slug, song_slug):
        url = f"{self.web_host}/music/albums/{album_slug}#{song_slug}"
        qr = QRCode(version=1, box_size=5, border=2)
        qr.add_data(url)
        qr.make(fit=True)

        return qr.make_image(
            fill_color=f"rgb{self.qr_color}", back_color=f"rgb{self.bg_color}"
        )

    def create_overlay(self, song_info):
        width, height = 1280, 720

        # Get colors from artwork
        self.bg_color = (15, 15, 15)
        text_color = (255, 255, 255, 255)
        secondary_color = (180, 180, 180, 255)
        self.qr_color = (255, 255, 255)

        artwork = None
        for img_source in [
            song_info.get("image"),
            song_info.get("album", {}).get("image_cropped"),
        ]:
            if img_source:
                artwork = self.get_image_from_url(img_source)
                if artwork:
                    try:
                        bg, text = self.get_dominant_colors(artwork)
                        self.bg_color = bg
                        text_color = (*text, 255)
                        self.qr_color = text
                        secondary_color = tuple(int(c * 0.7) for c in text) + (255,)
                        break
                    except Exception as e:
                        print(f"Color extraction failed: {e}")

        img = Image.new("RGBA", (width, height), (*self.bg_color, 255))
        draw = ImageDraw.Draw(img)

        title_font = ImageFont.truetype(self.font_path, size=40)
        artist_font = ImageFont.truetype(self.font_path, size=36)
        info_font = ImageFont.truetype(self.font_path, size=28)

        artwork_size = 400
        padding = 40
        left_margin = 50
        info_x = left_margin + artwork_size + padding * 2
        max_text_width = width - info_x - padding * 3

        # Paste artwork
        if artwork:
            artwork = artwork.resize((artwork_size, artwork_size), Image.LANCZOS)
            img.paste(artwork, (left_margin, (height - artwork_size) // 2))

        y = (height - artwork_size) // 2 + 20

        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current_line = []
            current_width = 0

            for word in words:
                word_width = font.getlength(word + " ")
                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width

            lines.append(" ".join(current_line))
            return lines

        title_lines = wrap_text(song_info["name"], title_font, max_text_width)
        for line in title_lines:
            draw.text((info_x, y), line, fill=text_color, font=title_font)
            y += 50

        y += 10

        authors = song_info.get("authors", [])
        if authors:
            artists = ", ".join(a["name"] for a in authors)
            artist_lines = wrap_text(artists, artist_font, max_text_width)
            for line in artist_lines:
                draw.text((info_x, y), line, fill=text_color, font=artist_font)
                y += 45

        y += 10

        meta = song_info.get("meta", {})
        genre = meta.get("genre", "").title() if meta else ""
        if genre:
            draw.text(
                (info_x, y), f"Genre: {genre}", fill=secondary_color, font=info_font
            )
            y += 40

        album = song_info.get("album")
        if album:
            album_lines = wrap_text(
                f"Album: {album['name']}", info_font, max_text_width
            )
            for line in album_lines:
                draw.text((info_x, y), line, fill=secondary_color, font=info_font)
                y += 40

            release_date = meta.get("release", "").split("T")[0] if meta else ""
            if release_date:
                draw.text(
                    (info_x, y),
                    f"Released: {release_date}",
                    fill=secondary_color,
                    font=info_font,
                )
                y += 40

        if album:
            qr_size = 120
            try:
                qr_img = self.create_qr(album["slug"], song_info.get("slug", ""))
                qr_img = qr_img.resize((qr_size, qr_size))
                qr_pos = (width - qr_size - padding, height - qr_size - padding)
                img.paste(qr_img, qr_pos)
            except Exception as e:
                print(f"QR code generation failed: {e}")

        # Ensure the image is in RGBA mode before saving as PNG
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.save(self.overlay_path, format="PNG")

    def stream_song(self, song_info):
        song_file = self.get_full_url(song_info["file"])
        length = song_info.get("length", None)

        if not length:
            raise ValueError("Song length is required")

        print(f"Processing '{song_info['name']}' with length {length} seconds")

        # Stop any previous FFmpeg processes
        if self.current_processes:
            print("Stopping previous song...")
            for proc in self.current_processes:
                proc.terminate()
            for proc in self.current_processes:
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
            self.current_processes = []

        # Start FFmpeg processes for each RTMP URL
        self.current_processes = []
        for rtmp_url in self.rtmp_urls:
            cmd = [
                "ffmpeg",
                "-re",
                "-i",
                song_file,
                "-stream_loop",
                "-1",
                "-i",
                self.overlay_path,
                "-c:a",
                "aac",
                "-c:v",
                "libx264",
                "-filter:a",
                "volume=0.5",
                "-preset",
                "veryfast",
                "-b:a",
                "192k",
                "-ar",
                "44100",
                "-r",
                "30",
                "-pix_fmt",
                "yuv420p",
                "-t",
                str(length),
                "-y",
                "-f",
                "flv",
                rtmp_url,
            ]
            print(f"Starting FFmpeg process for {rtmp_url}")
            proc = subprocess.Popen(cmd)
            self.current_processes.append(proc)

        start_time = time.time()

        while any(proc.poll() is None for proc in self.current_processes):
            # Check command queue every second
            try:
                cmd = self.command_queue.get_nowait()
                if cmd["action"] in ["next", "play"]:
                    print("Received command during playback, stopping current song...")
                    for proc in self.current_processes:
                        proc.terminate()
                    for proc in self.current_processes:
                        try:
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait()
                    self.current_processes = []
                    return False  # Signal that we were interrupted
            except queue.Empty:
                pass

            time.sleep(1)
            elapsed = time.time() - start_time
            if elapsed >= length:
                break

        # Terminate processes after the song is done
        for proc in self.current_processes:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        self.current_processes = []

        return True  # Signal normal completion

    def stream(self):
        while True:
            try:
                # Check for commands
                try:
                    cmd = self.command_queue.get_nowait()
                    if cmd["action"] == "next":
                        print("Skipping to next song...")
                        if self.current_processes:
                            print("Stopping current song...")
                            for proc in self.current_processes:
                                proc.terminate()
                            for proc in self.current_processes:
                                proc.wait()
                            self.current_processes = []
                        continue
                    elif cmd["action"] == "play":
                        song_info = self.get_song_info(cmd["slug"])
                        if song_info:
                            if song_info.get("meta", {}).get("genre", "").lower() in [
                                "rusrap"
                            ]:
                                print(
                                    f"Skipping {song_info['name']} because of genre 🤮"
                                )
                                continue
                            print(f"Playing requested song: {song_info['name']}")
                            self.play_random_songs = False  # Disable random songs
                            self.create_overlay(song_info)
                            self.stream_song(song_info)
                            self.play_random_songs = True  # Re-enable random songs
                            continue  # Go back to check for commands
                except queue.Empty:
                    pass

                if not self.play_random_songs:
                    time.sleep(5)
                    continue

                slugs = self.get_song_slugs()
                if not slugs:
                    time.sleep(10)
                    continue

                random.shuffle(slugs)

                for slug in slugs:
                    try:
                        # Check for commands again
                        if not self.command_queue.empty():
                            break

                        song_info = self.get_song_info(slug)
                        if not song_info:
                            continue

                        if song_info.get("meta", {}).get("genre", "").lower() in [
                            "rusrap"
                        ]:
                            print(f"Skipping {song_info['name']} because of genre 🤮")
                            continue

                        print(f"Starting stream for {song_info['name']}")
                        self.create_overlay(song_info)
                        if not self.stream_song(song_info):  # If interrupted
                            break
                        print(f"Finished streaming {song_info['name']}")

                    except Exception as e:
                        print(f"Error processing song {slug}: {e}")
                        if self.current_processes:
                            for proc in self.current_processes:
                                proc.terminate()
                                proc.wait()
                            self.current_processes = []
                        time.sleep(5)

            except Exception as e:
                print(f"Stream error: {e}")
                if self.current_processes:
                    for proc in self.current_processes:
                        proc.terminate()
                        proc.wait()
                    self.current_processes = []
                time.sleep(5)

    def cleanup(self):
        if self.current_processes:
            print("Cleaning up stream processes...")
            for proc in self.current_processes:
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    print(f"Force killing process {proc.pid}")
                    proc.kill()
                    proc.wait()
                except Exception as e:
                    print(f"Error killing process: {e}")
            self.current_processes = []


service: Optional[StreamService] = None
bot: Optional[StreamBot] = None
should_exit = threading.Event()


def cleanup_handler():
    """Cleanup handler for both normal exit and signals"""
    print("\nCleaning up...")
    should_exit.set()
    if service:
        service.cleanup()
    # Give processes time to cleanup
    time.sleep(2)


def signal_handler(signum, frame):
    """Handle SIGINT and SIGTERM"""
    if signum in (signal.SIGINT, signal.SIGTERM):
        print(f"\nReceived signal {signum}, initiating shutdown...")
        cleanup_handler()
        os._exit(0)  # Force exit if normal exit fails


if __name__ == "__main__":
    API_HOST = os.getenv("API_HOST", "https://new.akarpov.ru")
    WEB_HOST = os.getenv("WEB_HOST", "https://next.akarpov.ru")
    RTMP_URLS = os.getenv("RTMP_URLS")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_IDS = os.getenv("ADMIN_IDS")

    if not all([RTMP_URLS, TELEGRAM_TOKEN, ADMIN_IDS]):
        print("Missing required environment variables")
        exit(1)

    rtmp_urls = [url.strip() for url in RTMP_URLS.split(",") if url.strip()]
    if not rtmp_urls:
        print("No valid RTMP URLs provided")
        exit(1)

    # Register cleanup handlers
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize services
    service = StreamService(API_HOST, rtmp_urls, WEB_HOST)
    bot = StreamBot(API_HOST)
    bot.queue = service.command_queue

    # Run stream service in separate thread
    service_thread = threading.Thread(target=run_stream_service, args=(service,))
    service_thread.daemon = True
    service_thread.start()

    # Run bot in main thread
    try:
        bot.run()
    except KeyboardInterrupt:
        cleanup_handler()
    except Exception as e:
        print(f"Unexpected error: {e}")
        cleanup_handler()
    finally:
        cleanup_handler()
