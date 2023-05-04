import instaloader


USERNAME = "bebra374782784623"
PASSWORD = "s3PpcB2z9h845te"
if not USERNAME:
    USERNAME = input("username: ")

L = instaloader.Instaloader(dirname_pattern="{profile}/")
if PASSWORD:
    L.login(USERNAME, PASSWORD)
else:
    try:
        L.load_session_from_file(USERNAME, filename=".session")
    except Exception:
        L.interactive_login(USERNAME)
        L.save_session_to_file(".session")
link = input("link: ")
username = link.split(".")[-1].split("/")[1].split("?")[0]


profile = instaloader.Profile.from_username(L.context, username)
print(f"loading profile {profile.username}")

n = 1
posts = reversed([x for x in profile.get_posts()])

for post in posts:
    L.filename_pattern = "post_" + str(n) + "_{date_utc:%d.%m.%Y_%S:%M:%H}/post"
    L.download_post(post, profile)
    n += 1
