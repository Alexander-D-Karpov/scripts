import os
import json
from time import sleep

from quests import quests, notes

import requests

base_url = "https://habitica.com/api/v3/"

r = requests.get(base_url + "status")

if r.status_code == 200:
    data = r.json()["data"]
    if data and "status" in data and data["status"] == "up":
        print("Habitica API is up")
    else:
        print(data)
        raise ValueError
else:
    print("Habitica API is down")
    raise ValueError

HEADERS = {}


def login():
    global HEADERS
    username = input("username: ")
    password = input("password: ")
    r = requests.post(
        base_url + "user/auth/local/login",
        json={"username": username, "password": password},
    )
    if r.status_code != 200:
        print("Incorrect login")
        raise ValueError
    inner_data = r.json()["data"]
    api_id = inner_data["id"]
    api_token = inner_data["apiToken"]
    data = {"id": api_id, "token": api_token}
    with open(".session", "w") as f:
        json.dump(data, f)
    HEADERS = {
        "x-client": data["id"] + " - " + "sanspie's party manager",
        "x-api-user": data["id"],
        "x-api-key": data["token"],
    }


if not os.path.isfile(".session"):
    login()
else:
    with open(".session") as f:
        data = json.load(f)
    HEADERS = {
        "x-client": data["id"] + " - " + "sanspie's party manager",
        "x-api-user": data["id"],
        "x-api-key": data["token"],
    }

r = requests.get(base_url + "user", headers=HEADERS)
if r.status_code != 200:
    print("Incorrect token")
    login()
user = r.json()["data"]
party = user["party"]
if "_id" not in party:
    print("No party found")
    raise ValueError
party_id = party["_id"]

party = requests.get(base_url + f"/groups/{party_id}", headers=HEADERS).json()["data"]
print(f"party: {party['name']}")

usernames = {}


def get_username(id: str):
    if id in usernames:
        return usernames[id]
    r = requests.get(base_url + f"/members/{id}")
    if r.status_code != 200:
        raise ValueError
    username = r.json()["data"]["profile"]["name"]
    usernames[id] = username
    return username


def get_quest_status():
    r = requests.get(base_url + f"/groups/{party_id}", headers=HEADERS)
    if r.status_code != 200:
        raise ValueError
    party = r.json()["data"]
    quest = party["quest"]
    if quest["active"]:
        key = quest["key"]
        note = ""
        if key in notes:
            note = notes[key]
        if key in quests:
            name = quests[key]
        else:
            name = key
        return {
            "key": key,
            "name": name,
            "description": note,
            "members": [
                get_username(x) for x, active in quest["members"].items() if active
            ],
        }


while True:
    print(get_quest_status())
    sleep(1 * 60)
