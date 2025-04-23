import re

import requests
from bs4 import BeautifulSoup, NavigableString
import time
import random


def get_telegram_channel_info(channel_username):
    channel_username = channel_username.strip('@')
    url = f'https://t.me/s/{channel_username}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://t.me/',
        'Sec-Ch-Ua': '"Google Chrome";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }

    time.sleep(random.uniform(1, 2))

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching channel: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    channel_info = {
        'username': channel_username,
        'url': f'https://t.me/{channel_username}',
        'subscriber_count': 'Unknown',
        'channel_name': 'Unknown',
        'description': 'Unknown',
        'photo_url': None,
        'recent_posts': []
    }

    # Extract channel name
    channel_name_elem = soup.find('div', class_='tgme_channel_info_header_title')
    if channel_name_elem and channel_name_elem.find('span'):
        channel_info['channel_name'] = channel_name_elem.find('span').text.strip()

    # Extract subscriber count
    subscriber_counter = soup.find('div', class_='tgme_channel_info_counter',
                                   string=lambda text: 'subscribers' in text if text else False)
    if subscriber_counter and subscriber_counter.find('span', class_='counter_value'):
        channel_info['subscriber_count'] = subscriber_counter.find('span', class_='counter_value').text.strip()

    # Alternative location for subscriber count
    if channel_info['subscriber_count'] == 'Unknown':
        header_counter = soup.find('div', class_='tgme_header_counter')
        if header_counter:
            channel_info['subscriber_count'] = header_counter.text.strip().replace('subscribers', '').strip()

    # Extract description
    description_elem = soup.find('div', class_='tgme_channel_info_description')
    if description_elem:
        channel_info['description'] = description_elem.text.strip()

    # Extract channel photo
    photo_elem = soup.find('i', class_='tgme_page_photo_image')
    if photo_elem and photo_elem.find('img'):
        channel_info['photo_url'] = photo_elem.find('img').get('src')

    # Extract recent posts
    message_containers = soup.find_all('div', class_='tgme_widget_message')

    for container in message_containers[::-1]:
        post_data = {}

        post_data['id'] = container.get('data-post')

        text_elem = container.find('div', class_='tgme_widget_message_text')
        if text_elem:
            post_data['html_text'] = str(text_elem)

            formatted_text = ""

            def process_node(node):
                nonlocal formatted_text

                if node.name == 'br':
                    formatted_text += '\n'
                elif node.name == 'b':
                    formatted_text += f"<b>{node.get_text()}</b>"
                elif node.name == 'i':
                    formatted_text += f"<i>{node.get_text()}</i>"
                elif node.name == 'a':
                    href = node.get('href', '')
                    formatted_text += f"<a href='{href}'>{node.get_text()}</a>"
                elif node.name == 'pre' or node.name == 'code':
                    formatted_text += f"<code>{node.get_text()}</code>"
                elif node.name == 'tg-emoji':
                    emoji_code = node.find('i', class_='emoji').get_text() if node.find('i', class_='emoji') else ''
                    formatted_text += emoji_code
                elif isinstance(node, NavigableString):
                    formatted_text += str(node)
                else:
                    for child in node.children:
                        process_node(child)

            for child in text_elem.children:
                process_node(child)

            post_data['formatted_text'] = formatted_text
            post_data['plain_text'] = text_elem.get_text(separator=' ', strip=True)
        else:
            post_data['html_text'] = ""
            post_data['formatted_text'] = ""
            post_data['plain_text'] = ""

        # Get message date
        date_elem = container.find('a', class_='tgme_widget_message_date')
        if date_elem and date_elem.find('time'):
            post_data['date'] = date_elem.find('time')['datetime']

        # Get view count
        views_elem = container.find('span', class_='tgme_widget_message_views')
        if views_elem:
            post_data['views'] = views_elem.text.strip()

        # Check for media attachments
        photo_elem = container.find('a', class_='tgme_widget_message_photo_wrap')
        video_elem = container.find('a', class_='tgme_widget_message_video_player')

        if photo_elem:
            post_data['has_photo'] = True
            if 'style' in photo_elem.attrs:
                style = photo_elem['style']
                if 'background-image' in style:
                    url_start = style.find('url(') + 4
                    url_end = style.find(')', url_start)
                    photo_url = style[url_start:url_end].strip("'")
                    post_data['photo_url'] = photo_url.replace('\'', '').replace('"', '')
        else:
            post_data['has_photo'] = False

        if video_elem:
            post_data['has_video'] = True
            video_thumb = video_elem.find('i', class_='tgme_widget_message_video_thumb')
            if video_thumb and 'style' in video_thumb.attrs:
                style = video_thumb['style']
                if 'background-image' in style:
                    url_start = style.find('url(') + 4
                    url_end = style.find(')', url_start)
                    thumbnail_url = style[url_start:url_end].strip("'")
                    post_data['video_thumbnail'] = thumbnail_url.replace('\'', '').replace('"', '')

            # Get video duration
            duration_elem = video_elem.find('time', class_='message_video_duration')
            if duration_elem:
                post_data['video_duration'] = duration_elem.text.strip()
        else:
            post_data['has_video'] = False

        # Add post to list
        channel_info['recent_posts'].append(post_data)

    return channel_info


def print_channel_info(channel_info):
    if not channel_info:
        print("Could not retrieve channel information.")
        return

    print(f"TELEGRAM CHANNEL: @{channel_info['username']}")
    print(f"Name:        {channel_info['channel_name']}")
    print(f"Subscribers: {channel_info['subscriber_count']}")
    print(f"URL:         {channel_info['url']}")

    print("\nDescription:")
    print(channel_info['description'])

    print(f"\nRecent Posts ({len(channel_info['recent_posts'])} found):")
    for i, post in enumerate(channel_info['recent_posts'], 1):
        print(f"\nPost {i}:")
        print(f"  Date:    {post.get('date', 'Unknown')}")
        print(f"  Views:   {post.get('views', 'Unknown')}")

        media_types = []
        if post.get('has_photo'):
            media_types.append("Photo")
        if post.get('has_video'):
            media_types.append("Video")

        media_str = ", ".join(media_types) if media_types else "None"
        print(f"  Media:   {media_str}")

        formatted_text = post.get('formatted_text', '')
        if formatted_text:
            formatted_text = re.sub(r'<br\s*/?>', '\n', formatted_text)
            formatted_text = re.sub(r'\n+', '\n', formatted_text)

            if len(formatted_text) > 150:
                preview = formatted_text[:150] + "..."
            else:
                preview = formatted_text

            preview = re.sub(r'\s+', ' ', preview)
            print(f"  Content: {preview}")


if __name__ == "__main__":
    channel_name = input("Enter Telegram channel username (with or without @): ")

    print(f"\nFetching information for {channel_name}...")
    channel_info = get_telegram_channel_info(channel_name)

    print_channel_info(channel_info)
