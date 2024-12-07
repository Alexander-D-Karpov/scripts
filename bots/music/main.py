import os
import json
import yaml
import asyncio
from typing import Optional, Dict, Any
from telethon import TelegramClient
from telethon.tl.types import (
    MessageMediaDocument,
    Document,
    DocumentAttributeAudio,
    PhotoSize,
)
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import (
    ID3,
    TIT2,  # Title
    TPE1,  # Artist
    TALB,  # Album
    APIC,  # Album Art
    TDRC,  # Recording time
    TPE2,  # Album Artist
    TRCK,  # Track number
)
import mimetypes
import aiofiles
import aiohttp
from pathlib import Path


class MusicDownloader:
    def __init__(self, api_id: str, api_hash: str):
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.client = TelegramClient('music_downloader', self.api_id, self.api_hash)
        self.supported_audio_types = {
            'audio/mpeg': '.mp3',
            'audio/mp4': '.m4a',
            'audio/ogg': '.ogg',
            'audio/x-wav': '.wav',
            'audio/x-flac': '.flac'
        }

    async def start(self):
        await self.client.start()

    async def extract_audio_metadata(self, document: Document) -> Dict[str, Any]:
        """Extract metadata from Telegram Document object."""
        metadata = {
            'title': None,
            'performer': None,
            'album': None,
            'duration': None,
            'track_num': None,
            'thumbnail': None
        }

        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                metadata['title'] = attr.title
                metadata['performer'] = attr.performer
                metadata['duration'] = attr.duration

        # Extract thumbnail if available
        if document.thumbs:
            for thumb in document.thumbs:
                if isinstance(thumb, PhotoSize):
                    metadata['thumbnail'] = thumb
                    break

        return metadata

    async def download_thumbnail(self, thumb: PhotoSize) -> Optional[bytes]:
        """Download thumbnail bytes."""
        if not thumb:
            return None

        try:
            return await self.client.download_media(thumb, bytes)
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")
            return None

    async def convert_to_mp3(self, input_path: str, output_path: str):
        """Convert audio file to MP3 format."""
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format='mp3', bitrate='320k')
            return True
        except Exception as e:
            print(f"Error converting to MP3: {e}")
            return False

    async def update_mp3_metadata(self, file_path: str, metadata: Dict[str, Any], thumb_data: Optional[bytes]):
        """Update MP3 file with metadata and album art."""
        try:
            audio = MP3(file_path)
            if not audio.tags:
                audio.tags = ID3()

            # Add basic metadata
            if metadata['title']:
                audio.tags.add(TIT2(text=metadata['title']))
            if metadata['performer']:
                audio.tags.add(TPE1(text=metadata['performer']))
                audio.tags.add(TPE2(text=metadata['performer']))

            # Add album art if available
            if thumb_data:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=thumb_data
                ))

            audio.save()
            return True
        except Exception as e:
            print(f"Error updating MP3 metadata: {e}")
            return False

    async def process_audio_message(self, message) -> bool:
        """Process a single audio message."""
        if not message.media or not isinstance(message.media, MessageMediaDocument):
            return False

        document = message.media.document
        mime_type = document.mime_type

        if mime_type not in self.supported_audio_types:
            return False

        # Extract metadata
        metadata = await self.extract_audio_metadata(document)
        thumb_data = await self.download_thumbnail(metadata['thumbnail'])

        # Create file paths
        temp_path = f"temp_{message.id}{self.supported_audio_types[mime_type]}"
        final_path = f"downloads/{metadata['performer'] if metadata['performer'] else 'Unknown Artist'}"
        os.makedirs(final_path, exist_ok=True)

        final_filename = f"{metadata['title'] if metadata['title'] else f'track_{message.id}'}.mp3"
        final_path = os.path.join(final_path, final_filename)

        # Download original file
        try:
            await self.client.download_media(message, temp_path)
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

        try:
            # Convert to MP3 if needed
            if mime_type != 'audio/mpeg':
                if not await self.convert_to_mp3(temp_path, final_path):
                    os.remove(temp_path)
                    return False
            else:
                os.rename(temp_path, final_path)

            # Update metadata
            await self.update_mp3_metadata(final_path, metadata, thumb_data)

            print(f"Successfully processed: {final_filename}")
            return True

        except Exception as e:
            print(f"Error processing file: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    async def process_channel(self, channel_id: str, limit: int = None):
        """Process all audio messages from a channel."""
        try:
            print(f"Processing channel: {channel_id}")

            # Create downloads directory
            os.makedirs("downloads", exist_ok=True)

            # Iterate through messages
            async for message in self.client.iter_messages(channel_id, limit=limit):
                await self.process_audio_message(message)

        except Exception as e:
            print(f"Error processing channel: {e}")

    async def close(self):
        await self.client.disconnect()


async def main():
    # Load config
    if not os.path.isfile("poller.yaml"):
        raise FileNotFoundError("Please create poller.yaml")

    with open("poller.yaml", "r") as stream:
        config = yaml.safe_load(stream)

    api_id = os.getenv("api_id")
    api_hash = os.getenv("api_hash")

    if not api_id or not api_hash:
        raise ValueError("Please set api_id and api_hash environment variables")

    downloader = MusicDownloader(api_id, api_hash)
    await downloader.start()

    try:
        # Process channels from config
        if 'channels' in config:
            if 'usernames' in config['channels']:
                for username in config['channels']['usernames']:
                    username = username.replace('https://t.me/', '').replace('@', '')
                    await downloader.process_channel(username)

            if 'ids' in config['channels']:
                for channel_id in config['channels']['ids']:
                    await downloader.process_channel(channel_id)

    finally:
        await downloader.close()


if __name__ == "__main__":
    # Install required packages
    # pip install telethon pydub mutagen cryptg
    asyncio.run(main())