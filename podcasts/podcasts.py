import asyncio
import os
import daemon
from io import BytesIO

from time import sleep

from aiogram import Bot
from aiogram.bot.api import TelegramAPIServer
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import APIC, ID3, TORY
from pydub import AudioSegment
from yandex_music import Client, Track
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_SERVER = os.getenv("TELEGRAM_SERVER", default=None)

if TELEGRAM_SERVER:
    local_server = TelegramAPIServer.from_base(TELEGRAM_SERVER)
    bot = Bot(TOKEN, server=local_server)
else:
    bot = Bot(TOKEN)


client = Client(YANDEX_TOKEN).init()
latest_podcast = None
latest_sent = True
podcasts_listened = []


with daemon.DaemonContext():
    while True:
        try:
            queues = client.queues_list()
            last_queue = client.queue(queues[0].id)

            last_track_id = last_queue.get_current_track()
            last_track: Track = last_track_id.fetch_track()

            if "podcast" in last_track.type:
                if last_track_id not in podcasts_listened:
                    if last_track_id == latest_podcast and not latest_sent:
                        latest_sent = True
                        podcasts_listened.append(last_track_id)

                        title = last_track.title
                        album = last_track.albums[0]
                        url = f"https://music.yandex.ru/track/{last_track.id}"
                        desc = last_track.short_description.split("\n")[0]

                        last_track.download_cover(filename="cover.png")
                        img_path = os.path.abspath("cover.png")

                        last_track.download(filename="file", codec="mp3")
                        orig_path = os.path.abspath("file")
                        path = os.path.abspath("file.mp3")

                        AudioSegment.from_file(orig_path).export(path)
                        os.remove(orig_path)

                        # set music meta
                        tag = MP3(path, ID3=ID3)
                        tag.tags.add(
                            APIC(
                                encoding=3,  # 3 is for utf-8
                                mime="image/png",  # image/jpeg or image/png
                                type=3,  # 3 is for the cover image
                                desc="Cover",
                                data=open(img_path, "rb").read(),
                            )
                        )
                        tag.tags.add(TORY(text=str(album.year)))
                        tag.save()
                        tag = EasyID3(path)

                        tag["title"] = title
                        tag["album"] = album.title

                        tag.save()

                        with open(path, "rb") as tmp:
                            obj = BytesIO(tmp.read())
                            obj.name = f"{title}.mp3"
                            loop = asyncio.get_event_loop()
                            coroutine = bot.send_audio(
                                chat_id=CHAT_ID,
                                audio=obj,
                                caption=f"{title} - {album.title}\n{desc}\n\n{url}",
                                title=title,
                                performer=album.title,
                            )
                            loop.run_until_complete(coroutine)

                    else:
                        latest_podcast = last_track_id
                        latest_sent = False
        except BaseException as e:
            loop = asyncio.get_event_loop()
            coroutine = bot.send_message(CHAT_ID, text=str(e))
            loop.run_until_complete(coroutine)
        sleep(5 * 60)
