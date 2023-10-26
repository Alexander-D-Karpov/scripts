import os.path
import zoneinfo

import requests

from dateutil import parser
from ics import Calendar, Event

token = input("token: ")

params = {
    "date_start": "2023-10-01",
    "date_end": "2023-11-01",
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru",
    # 'Accept-Encoding': 'gzip, deflate, br',
    "Authorization": token,
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://my.itmo.ru/schedule",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}


response = requests.get(
    "https://my.itmo.ru/api/schedule/schedule/personal",
    params=params,
    headers=headers,
)

if response.status_code != 200:
    raise ValueError(response.status_code)

data = response.json()["data"]
c = Calendar()
for d_data in data:
    date = d_data["date"]
    lessons = d_data["lessons"]
    if lessons:
        for lesson in lessons:
            t_from = parser.parse(f'{date}T{lesson["time_start"]}').replace(
                tzinfo=zoneinfo.ZoneInfo("Europe/Moscow")
            )
            t_end = parser.parse(f'{date}T{lesson["time_end"]}').replace(
                tzinfo=zoneinfo.ZoneInfo("Europe/Moscow")
            )
            name = lesson["subject"]
            desc = []

            if lesson["building"]:
                if lesson["room"]:
                    desc.append(lesson["building"] + " " + lesson["room"])
                else:
                    desc.append(lesson["building"])
            elif lesson["room"]:
                desc.append(lesson["room"])

            if lesson["work_type"]:
                desc.append(lesson["work_type"])

            if lesson["note"]:
                desc.append(f"Заметка: {lesson['note']}")
            e = Event()
            e.name = name
            e.begin = t_from
            e.end = t_end

            if lesson["teacher_name"]:
                e.organizer = lesson["teacher_name"]
            if lesson["zoom_url"]:
                url = lesson["zoom_url"]
                if lesson["zoom_password"] and "?pwd" not in url:
                    url += f"?pwd={lesson['zoom_password']}"
                e.url = url

            if lesson["type"]:
                e.categories = [lesson["type"]]

            e.description = "\n".join(desc)
            c.events.add(e)

if os.path.exists("itmo.ics"):
    os.remove("itmo.ics")

with open("itmo.ics", "w") as file:
    file.writelines(c.serialize_iter())
