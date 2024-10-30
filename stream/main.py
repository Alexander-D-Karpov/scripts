import os
import random
import subprocess

import requests
import time
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from io import BytesIO
from colorthief import ColorThief
from urllib.parse import urljoin

from qrcode.main import QRCode


class StreamService:
    def __init__(self, api_host, rtmp_url, web_host):
        self.qr_color = None
        self.bg_color = None
        self.api_host = api_host.rstrip("/")
        self.web_host = web_host.rstrip("/")
        self.rtmp_url = rtmp_url
        self.overlay_path = "/tmp/overlay.png"
        self.session = requests.Session()

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

        img.save(self.overlay_path, "PNG")

    def stream_song(self, song_info):
        song_file = self.get_full_url(song_info["file"])
        length = song_info.get("length", None)

        if not length:
            raise ValueError("Song length is required")

        print(f"Processing '{song_info['name']}' with length {length} seconds")

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
            self.rtmp_url,
        ]

        process = subprocess.Popen(cmd)
        process.wait()

        print(f"Finished streaming {song_info['name']}")

    def stream(self):
        while True:
            slugs = self.get_song_slugs()
            if not slugs:
                time.sleep(10)
                continue

            random.shuffle(slugs)

            for slug in slugs:
                try:
                    song_info = self.get_song_info(slug)
                    if not song_info:
                        continue

                    print(f"Starting stream for {song_info['name']}")
                    self.create_overlay(song_info)
                    self.stream_song(song_info)
                    print(f"Finished streaming {song_info['name']}")

                except Exception as e:
                    print(f"Error processing song {slug}: {e}")
                    time.sleep(5)


if __name__ == "__main__":
    API_HOST = os.getenv("API_HOST", "https://new.akarpov.ru")
    WEB_HOST = os.getenv("WEB_HOST", "https://next.akarpov.ru")
    RTMP_URL = os.getenv("RTMP_URL", None)

    if not RTMP_URL:
        print("RTMP_URL environment variable is not set")
        exit(1)

    service = StreamService(API_HOST, RTMP_URL, WEB_HOST)
    service.stream()
