# poller

script to load new media from telegram chats

### Installation
get api_id and api_hash at https://my.telegram.org/apps
```shell
$ pip install -r requirements.txt
$ export api_id=123
$ export api_hash=abcdef....
```

### Configuration
modify poller.yaml to change chats
```yaml
channels:
  usernames:
    - https://t.me/sanspie_notes
    - @s4nspie
  ids:
    - 868474142

folders:
  - Users
```

### Run
```shell
$ python3 poller.py
```

files will be downloaded to folders

###### Note: if you want to redownload files delete poller/.offsets.json