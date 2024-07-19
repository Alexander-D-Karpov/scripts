import asyncio
import os
import tempfile

from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import InputFile
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
    bot = Bot(TOKEN, base_url=local_server.base)
else:
    bot = Bot(TOKEN)

dp = Dispatcher()

client = Client(YANDEX_TOKEN).init()
latest_podcast = None
latest_sent = True
podcasts_listened = []


async def main():
    global latest_podcast, latest_sent

    while True:
        try:

            queues = client.queues_list()  # Ques are now not working
            if not queues:
                print(
                    "No active queues found. Waiting for 60 seconds before checking again."
                )
                await asyncio.sleep(5)
                continue

            last_queue = client.queue(queues[0].id)
            last_track_id = last_queue.get_current_track()

            if last_track_id is None:
                print(
                    "No track currently playing. Waiting for 60 seconds before checking again."
                )
                await asyncio.sleep(60)
                continue

            last_track: Track = last_track_id.fetch_track()

            artists = ", ".join(last_track.artists_name())
            title = last_track.title
            print(f"Currently playing: {artists} - {title}")

            if "podcast" in last_track.type:
                if last_track_id not in podcasts_listened:
                    if last_track_id == latest_podcast and not latest_sent:
                        latest_sent = True
                        podcasts_listened.append(last_track_id)

                        album = last_track.albums[0]
                        url = f"https://music.yandex.ru/track/{last_track.id}"
                        desc = (
                            last_track.short_description.split("\n")[0]
                            if last_track.short_description
                            else ""
                        )

                        with tempfile.TemporaryDirectory() as temp:
                            last_track.download_cover(filename=temp + "cover.png")
                            img_path = os.path.abspath(temp + "cover.png")

                            last_track.download(filename=temp + "file", codec="mp3")
                            orig_path = os.path.abspath(temp + "file")
                            path = os.path.abspath(temp + "file.mp3")

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

                            audio_file = InputFile(path)
                            await bot.send_audio(
                                chat_id=CHAT_ID,
                                audio=audio_file,
                                caption=f"{title} - {album.title}\n{desc}\n\n{url}",
                                title=title,
                                performer=album.title,
                            )

                    else:
                        latest_podcast = last_track_id
                        latest_sent = False
            else:
                print(f"Current track is not a podcast: {artists} - {title}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            await bot.send_message(868474142, text=f"An error occurred: {str(e)}")
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
