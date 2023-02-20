# Podcast loader script

Script to load current listening track from yandex music and send it to telegram chat.

### Configuration
Obtain yandex music token - https://music-yandex-bot.ru/

Obtain telegram api id and hash for local telegram image - https://my.telegram.org/

### Installation 
OPTIONAL: start local telegram bot server for file upload
```shell
$ docker run -d -p 8081:8081 --name=telegram-bot-api --restart=always -v telegram-bot-api-data:/var/lib/telegram-bot-api -e TELEGRAM_API_ID=<api_id> -e TELEGRAM_API_HASH=<api-hash> aiogram/telegram-bot-api:latest
```

```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirement.txt
```

### Run
program runs via python-daemon
```shell
$ python3 podcasts.py
```

Note: can be modified to send all(unique) tracks, just remove ```if "podcast" in last_track.type``` check
