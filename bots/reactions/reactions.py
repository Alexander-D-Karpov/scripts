import os
import jellyfish

from telethon import TelegramClient

if os.getenv("api_id") is None:
    raise ValueError("please set api_id env variable")

if os.getenv("api_hash") is None:
    raise ValueError("please set api_hash env variable")

api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")

source = input("name, username, link or id: ")
source_type = input("c - channel id, s - search: ")
while source_type not in ["c", "s"]:
    source_type = input("c - channel id, s - search: ")


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


async def run(client: TelegramClient):
    if source_type == "s":
        channels = []
        async for dialog in client.iter_dialogs():
            channels.append((dialog, str(dialog.name)))
        similar_channels = []
        for id, name in channels:
            similar_channels.append(
                (name, id, jellyfish.levenshtein_distance(source.lower(), name.lower()))
            )
        similar_channels.sort(key=lambda x: x[2])
        similar_channels = similar_channels[:10]
        for i, var in enumerate(similar_channels):
            print(f"[{i+1}] - {var[0]}")
        n = int(input("Number: "))
        if n > 10:
            raise ValueError
        entity = similar_channels[n - 1][1]
    else:
        entity = await client.get_entity(source)

    messages = []
    max_id = 0
    async for message in client.iter_messages(entity):
        max_id = message.id
        break

    print("Loading.... This might take a while")
    eid = str(entity.id)
    if eid.startswith("-100"):
        eid = eid[4:]
    async for message in progress_bar(
        client.iter_messages(entity, reverse=True, min_id=0),
        max_id,
        " " * 4 + f"processing {entity.title}:",
    ):
        r = message.reactions
        if r:
            count = sum([x.count for x in r.results])
            messages.append(
                (f"https://t.me/c/{eid}/{message.id} - {message.text}", count)
            )
    messages.sort(key=lambda x: x[1], reverse=True)
    print("done!")
    for message, reactions in messages[:20]:
        print(f"[{reactions}] - {message}")


with TelegramClient("reactions", api_id, api_hash) as client:
    client.loop.run_until_complete(run(client))
