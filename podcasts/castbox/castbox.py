import requests
import json
import os

from urllib.parse import unquote
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import APIC, ID3

url = input("https://castbox.fm/channel/: ")

if not url.startswith("https://castbox.fm/channel/"):
    url = "https://castbox.fm/channel/" + url


def download_file(file_url):
    local_filename = file_url.split("/")[-1]
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


r = requests.get(url)
if r.status_code != 200:
    raise LookupError("Site not found")
inner_data = r.text.splitlines()
data = []
for line in inner_data:
    if "window.__INITIAL_STATE__" in line:
        data.append(line)

if len(data) != 1:
    raise ValueError("Payload not found")

d = json.loads(unquote(data[0].split('"')[1::2][0]))  # type: dict
title = d["ch"]["chInfo"]["title"]
main_image = d["ch"]["chInfo"]["cover_web"]
author = d["ch"]["chInfo"]["author"]
print("Downloading podcast " + title)
episodes = d["ch"]["eps"]
if not os.path.isdir(title):
    os.mkdir(title)
for i, episode in enumerate(episodes):
    print(f"Downloading: {episode['title']}", end="\r")
    if "url" in episode and episode["url"]:
        ep_url = episode["url"]
    else:
        ep_url = episode["urls"][0]
    orig_path = download_file(ep_url)
    n_path = title + "/" + f"{title}.mp3"
    AudioSegment.from_file(orig_path).export(n_path)
    os.remove(orig_path)
    if "cover_url" not in episode or not episode["cover_url"]:
        img_path = download_file(main_image)
    else:
        img_path = download_file(episode["cover_url"])
    if "author" in episode and episode["author"]:
        ep_author = episode["author"]
    else:
        ep_author = author

    tag = MP3(n_path, ID3=ID3)
    tag.tags.add(
        APIC(
            encoding=3,
            mime="image/png",
            type=3,
            desc="Cover",
            data=open(img_path, "rb").read(),
        )
    )
    tag.save()
    tag = EasyID3(n_path)

    tag["title"] = episode["title"]
    tag["album"] = title
    tag["artist"] = ep_author

    tag.save()
    os.remove(img_path)
