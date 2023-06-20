import os
import json
import yaml

from telethon import TelegramClient
from telethon.tl import functions
from telethon.tl.types import (
    MessageMediaDocument,
    MessageMediaPhoto,
    PeerChannel,
    PeerUser,
    PeerChat,
)

if os.getenv("api_id") is None:
    raise ValueError("please set api_id env variable")

if os.getenv("api_hash") is None:
    raise ValueError("please set api_hash env variable")

api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")

if not os.path.isdir("poller"):
    os.mkdir("poller")

if not os.path.isfile("poller.yaml"):
    raise FileNotFoundError("Please create poller.yaml")

with open("poller.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# load offsets
offsets = {}
if not os.path.isfile("poller/.offsets.json"):
    f = open("poller/.offsets.json", "x")
    f.write("{}")
    f.close()
else:
    with open("poller/.offsets.json") as f:
        offsets = json.load(f)


# parse and check config
folders = []
channels = []
if "folders" in config:
    if config["folders"]:
        folders = config["folders"]
        if type(folders) is not list:
            raise TypeError("Folders should be a list(start with - on a new line)")
        if not (all([type(x) is str for x in folders])):
            raise TypeError("Folders should be specified by name")
if "channels" in config:
    if "ids" in config["channels"]:
        ids = config["channels"]["ids"]
        if type(ids) is not list:
            raise TypeError("Ids should be a list(start with - on a new line)")
        if not (all([type(x) is int for x in ids])):
            raise TypeError("Ids should be integers")
        channels += list(map(str, ids))
    if "usernames" in config["channels"]:
        usernames = config["channels"]["usernames"]
        if type(usernames) is not list:
            raise TypeError("Usernames should be a list(start with - on a new line)")
        if not (all([type(x) is str for x in usernames])):
            raise TypeError("Channel's ids should be string")
        channels += [x.replace("@", "") for x in usernames]


async def aenumerate(asequence, start=0):
    """Asynchronously enumerate an async iterator from a given start value"""
    n = start
    async for elem in asequence:
        yield n, elem
        n += 1


async def progress_bar(
    iterable,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    print_end="\r",
):
    # Progress Bar Printing Function
    def print_progress_bar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        print(
            f"\r{prefix} |{bar}| {percent}% ({iteration+1}/{total}) {suffix}",
            end=print_end,
        )

    print_progress_bar(0)
    async for i, item in aenumerate(iterable):
        yield item
        print_progress_bar(item.id)


async def download(client, entity, title, min_id):
    max_id = 0
    async for message in client.iter_messages(entity):
        max_id = message.id
        break

    if max_id <= min_id:
        print(" " * 4 + f"done {title}")
        return
    if not os.path.isdir(f"poller/{title}"):
        os.mkdir(f"poller/{title}")
    if not os.path.isdir(f"poller/{title}/photos/"):
        os.mkdir(f"poller/{title}/photos/")
    if not os.path.isdir(f"poller/{title}/videos/"):
        os.mkdir(f"poller/{title}/videos/")
    if not os.path.isdir(f"poller/{title}/other/"):
        os.mkdir(f"poller/{title}/other/")
    print(" " * 4 + f"downloading {title}", end="\r")
    async for message in progress_bar(
        client.iter_messages(entity, reverse=True, min_id=min_id),
        max_id,
        " " * 4 + f"downloading {title}:",
    ):
        if message.media:
            if type(message.media) == MessageMediaPhoto:
                await message.download_media(file=f"poller/{title}/photos/")
            elif type(message.media) == MessageMediaDocument:
                if message.media.document.mime_type:
                    mime_type = message.media.document.mime_type
                    if mime_type.startswith("image"):
                        await message.download_media(file=f"poller/{title}/photos/")
                    elif mime_type.startswith("video"):
                        await message.download_media(file=f"poller/{title}/videos/")
                    else:
                        await message.download_media(file=f"poller/{title}/other/")
                else:
                    await message.download_media(file=f"poller/{title}/other/")

        offsets[entity.id] = message.id

        if message.id % 10 == 0:
            with open("poller/.offsets.json", "w") as f:
                json.dump(offsets, f, indent=4)
    print(" " * 4 + f"done {title}")
    with open("poller/.offsets.json", "w") as f:
        json.dump(offsets, f, indent=4)


async def download_channel(client, id):
    id = str(id)
    min_id = 0
    if id in offsets:
        min_id = offsets[id]
    try:
        entity = await client.get_entity(PeerChannel(int(id)))
    except ValueError:
        print("channel not found, there is probably somthing broken...")
        return
    await download(client, entity, entity.title, min_id)


async def download_user(client, id):
    id = str(id)
    min_id = 0
    if id in offsets:
        min_id = offsets[id]
    try:
        entity = await client.get_entity(PeerUser(int(id)))
    except ValueError:
        print("user not found, there is probably somthing broken...")
        return
    await download(client, entity, entity.username, min_id)


async def download_chat(client, id):
    id = str(id)
    min_id = 0
    if id in offsets:
        min_id = offsets[id]
    try:
        entity = await client.get_entity(PeerChat(int(id)))
    except ValueError:
        print("chat not found, there is probably somthing broken...")
        return
    await download(client, entity, entity.title, min_id)


async def run(client):
    err = False

    if channels:
        for c in channels:
            try:
                entity = await client.get_entity(c)
                await download_channel(client, entity.id)
            except ValueError:
                err = True
                print(f"Chat {c} not found")
        if err:
            raise ValueError(
                "please check if channel's names or ids in config are correct"
            )

    if folders:
        user_folders = {}
        req = await client(functions.messages.GetDialogFiltersRequest())
        for folder in req:
            d = folder.to_dict()
            if "title" in d:
                if d["title"] in folders:
                    user_folders[d["title"]] = []
                    for el in d["include_peers"]:
                        id = 0
                        for name, val in el.items():
                            if "id" in name:
                                id = str(val)
                        user_folders[d["title"]].append({"_": el["_"], "id": id})

        for el in folders:
            if el not in user_folders:
                err = True
                print(f"folder {el} not found")
        if err:
            raise ValueError("please check if folder's names in config are correct")
        for folder, included_chats in user_folders.items():
            print(f"downloading folder: {folder}")
            for el in included_chats:
                id = el["id"]
                if el["_"] == "InputPeerUser":
                    await download_user(client, id)
                elif el["_"] == "InputPeerChannel":
                    await download_channel(client, id)
                elif el["_"] == "InputPeerChat":
                    await download_chat(client, id)


with TelegramClient("downloader", int(api_id), api_hash) as client:
    client.loop.run_until_complete(run(client))
