#!/usr/bin/env python3
"""
SoundCloud Downloader with ID3 Tags
-----------------------------------
This script downloads all tracks from a SoundCloud artist,
including proper ID3 tags and album artwork.

Requirements:
pip install scdl mutagen requests tqdm
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TCOM, COMM
from tqdm import tqdm
import re
import argparse


# ANSI colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'


def setup_argparser():
    parser = argparse.ArgumentParser(description='Download all tracks from a SoundCloud artist with proper ID3 tags')
    parser.add_argument('url', help='SoundCloud URL (artist profile or likes page)')
    parser.add_argument('-o', '--output', default='downloads', help='Output directory')
    parser.add_argument('-c', '--client-id', help='SoundCloud client ID (optional)')
    parser.add_argument('--likes', action='store_true', help='Download liked tracks (auto-detected from URL)')
    parser.add_argument('--author', help='Explicitly set the author name for all tracks')
    parser.add_argument('--album', help='Explicitly set the album name for all tracks')
    parser.add_argument('--force-tags', action='store_true', help='Force update of ID3 tags even if they exist')
    return parser.parse_args()


def get_client_id():
    """Extract client_id by scraping SoundCloud's website"""
    print(f"{Colors.BLUE}[*] Obtaining SoundCloud client ID...{Colors.ENDC}")

    try:
        response = requests.get('https://soundcloud.com/')
        scripts = re.findall(r'<script crossorigin src="(.*?\.js)"', response.text)

        # Try to find client_id in the scripts
        for script_url in scripts:
            if not script_url.startswith('http'):
                script_url = 'https://soundcloud.com' + script_url

            script_content = requests.get(script_url).text
            client_id_match = re.search(r'"client_id":"([a-zA-Z0-9]+)"', script_content)
            if client_id_match:
                return client_id_match.group(1)
    except Exception as e:
        print(f"{Colors.RED}[!] Error getting client ID: {e}{Colors.ENDC}")

    return None


def download_tracks(artist_url, output_dir, client_id=None, likes=False):
    """Download all tracks from the given artist URL or likes page"""
    if not client_id:
        client_id = get_client_id()

    if not client_id:
        print(f"{Colors.RED}[!] Failed to get client ID. Please provide it manually with --client-id{Colors.ENDC}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract artist name from URL
    url_parts = artist_url.strip('/').split('/')
    artist_name = url_parts[-2] if likes or '/likes' in artist_url else url_parts[-1]

    print(
        f"{Colors.GREEN}[+] {'Downloading liked tracks' if likes else 'Downloading tracks'} for {artist_name} to {output_dir}{Colors.ENDC}")

    # Use scdl to download tracks
    cmd = [
        'scdl',
        '-l', artist_url,
        '--path', output_dir,
        '--client-id', client_id,
        '--flac',  # Try to get best quality where available
        '-c'  # Continue if download already exists
    ]

    # Add appropriate flag based on download type
    if likes or '/likes' in artist_url:
        cmd.append('-f')  # Download favorites/likes
    elif '/sets/' in artist_url:
        cmd.append('-p')  # Download playlist
    else:
        cmd.append('-a')  # Download all tracks from user

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[!] Error running scdl: {e}{Colors.ENDC}")
        sys.exit(1)

    return output_dir, artist_name


def get_artist_info(artist_url, client_id):
    """Get artist information from SoundCloud API"""
    resolve_url = f"https://api-v2.soundcloud.com/resolve?url={artist_url}&client_id={client_id}"

    try:
        response = requests.get(resolve_url)
        data = response.json()
        return data
    except Exception as e:
        print(f"{Colors.RED}[!] Error getting artist info: {e}{Colors.ENDC}")
        return None


def get_tracks_info(download_dir, client_id):
    """Get information about tracks from SoundCloud API"""
    print(f"{Colors.BLUE}[*] Gathering track information from SoundCloud...{Colors.ENDC}")

    # Find all MP3 files
    mp3_files = list(Path(download_dir).glob('*.mp3'))
    track_info_map = {}

    for mp3_file in mp3_files:
        # Try to extract track ID or permalink from filename
        # Many SoundCloud downloaders append the track ID to the filename
        track_id_match = re.search(r'[-_](\d{6,})(\.mp3)?$', mp3_file.stem)

        if track_id_match:
            # If we have a track ID, use it to get info from the API
            track_id = track_id_match.group(1)
            try:
                track_url = f"https://api-v2.soundcloud.com/tracks/{track_id}?client_id={client_id}"
                response = requests.get(track_url)
                if response.status_code == 200:
                    track_data = response.json()
                    track_info_map[mp3_file.name] = track_data
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Warning: Could not get info for track ID {track_id}: {e}{Colors.ENDC}")

    return track_info_map


def extract_set_info(filename):
    """Extract information from set/playlist filenames"""
    # For files from sets: "Set Name_Artist - Track Title.mp3"
    set_match = re.search(r'^(.+?)_(.+?)\.mp3$', filename)
    if set_match:
        set_name = set_match.group(1).strip()
        title_part = set_match.group(2).strip()

        # Try to extract artist from title if it's in the "Artist - Title" format
        artist_title_match = re.search(r'^(.+?) - (.+)$', title_part)
        if artist_title_match:
            artist = artist_title_match.group(1).strip()
            title = artist_title_match.group(2).strip()
        else:
            # If no artist separator found, the whole part is the title
            artist = None
            title = title_part

        return {
            'set_name': set_name,
            'artist': artist,
            'title': title
        }

    # Another pattern: Some playlist files don't have the separator
    # Example: "Playlist Name - Track Title.mp3" without artist info
    alt_match = re.search(r'^(.+?) - (.+?)\.mp3$', filename)
    if alt_match:
        set_name = alt_match.group(1).strip()
        title = alt_match.group(2).strip()

        return {
            'set_name': set_name,
            'artist': None,  # No artist info in this format
            'title': title
        }

    return None


def extract_album_from_comments(tags):
    """Try to extract album information from ID3 comment tags"""
    if "COMM" in tags:
        comment = str(tags["COMM"])
        # Look for potential album indicators in comments
        album_match = re.search(r'CTCD-\d+\s+["\'](.+?)["\']', comment)
        if album_match:
            return album_match.group(1)

        # Another pattern: Album name followed by E.P. or EP
        ep_match = re.search(r'([^"\']+?)\s+E\.?P\.?', comment)
        if ep_match:
            return f"{ep_match.group(1)} E.P."

    return None


def fix_id3_tags(download_dir, artist_name, client_id, forced_author=None, forced_album=None, force_tags=False):
    """Fix ID3 tags and add album artwork to downloaded files"""
    print(f"{Colors.BLUE}[*] Adding ID3 tags and artwork...{Colors.ENDC}")

    # Get artist info
    artist_info = get_artist_info(f"https://soundcloud.com/{artist_name}", client_id)
    artist_avatar_url = artist_info.get('avatar_url') if artist_info else None

    # Try to get additional track info from SoundCloud API
    track_info_map = get_tracks_info(download_dir, client_id)

    # Download artist avatar for use as album art if needed
    avatar_data = None
    if artist_avatar_url:
        try:
            # Get highest resolution image by replacing size in URL
            hi_res_avatar_url = artist_avatar_url.replace('-large', '-t500x500')
            avatar_response = requests.get(hi_res_avatar_url)
            avatar_data = avatar_response.content
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Warning: Could not download artist avatar: {e}{Colors.ENDC}")

    # Process all MP3 files
    downloaded_files = list(Path(download_dir).glob('*.mp3'))
    processed_count = 0
    skipped_count = 0

    for mp3_file in tqdm(downloaded_files, desc="Processing files"):
        try:
            # Read or create ID3 tags
            try:
                tags = ID3(mp3_file)
                # Skip if tags exist and force_tags is not set
                if not force_tags and "TIT2" in tags and "TPE1" in tags and "TALB" in tags:
                    skipped_count += 1
                    continue
            except:
                # Create new ID3 tag if not present
                tags = ID3()

            # Extract information from filename
            set_info = extract_set_info(mp3_file.name)

            # Initialize variables
            title = None
            artist = forced_author
            album = forced_album

            # Get title from set_info or filename
            if set_info:
                title = set_info['title']
                # Only use artist from set_info if forced_author not provided
                if not artist and set_info['artist']:
                    artist = set_info['artist']
                # Only use set_name as album if forced_album not provided
                if not album:
                    album = set_info['set_name']
            else:
                # Try to extract from regular filename
                filename_match = re.search(r'(.+?) - (.+?)\.mp3$', mp3_file.name)
                if filename_match:
                    if not artist:
                        artist = filename_match.group(1).strip()
                    title = filename_match.group(2).strip()
                else:
                    # Just use the filename as title
                    title = mp3_file.stem

            # Try to extract album info from existing tags if available
            if not album and "COMM" in tags:
                album_from_comment = extract_album_from_comments(tags)
                if album_from_comment:
                    album = album_from_comment

            # If no album was determined, use a default
            if not album:
                album = "Unknown Album"

            # If no artist was determined, use the forced_author or a default
            if not artist:
                artist = forced_author or "Unknown Artist"

            # Set ID3 tags
            tags["TIT2"] = TIT2(encoding=3, text=title)
            tags["TPE1"] = TPE1(encoding=3, text=artist)
            tags["TALB"] = TALB(encoding=3, text=album)

            # Add artwork if we have it and it's missing or we're forcing updates
            if avatar_data and (force_tags or not any(tag.startswith('APIC') for tag in tags.keys())):
                tags["APIC"] = APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,  # Cover (front)
                    desc="Cover",
                    data=avatar_data
                )

            # Save tags to file
            tags.save(mp3_file)
            processed_count += 1

        except Exception as e:
            print(f"{Colors.YELLOW}[!] Warning: Could not process file {mp3_file}: {e}{Colors.ENDC}")

    print(
        f"{Colors.GREEN}[+] Successfully processed {processed_count} files, skipped {skipped_count} files with existing tags{Colors.ENDC}")


def main():
    args = setup_argparser()

    print(f"{Colors.GREEN}[+] SoundCloud Downloader with ID3 Tags{Colors.ENDC}")

    # Auto-detect likes URL if not explicitly set
    likes = args.likes or '/likes' in args.url

    download_dir, artist_name = download_tracks(args.url, args.output, args.client_id, likes)
    client_id = args.client_id or get_client_id()
    fix_id3_tags(download_dir, artist_name, client_id, args.author, args.album, args.force_tags)

    print(f"{Colors.GREEN}[+] All done! Downloaded tracks are in: {download_dir}{Colors.ENDC}")


if __name__ == "__main__":
    main()
