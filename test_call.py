import requests
import os
from dotenv import load_dotenv
import re

# Load credentials from .env file
load_dotenv()
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
TMP_DIR = './static/'  # Temporary directory path

def sanitize_artist_name(artist_name):
    # Remove any text within parentheses
    sanitized_name = re.sub(r'\s*\(.*?\)\s*', '', artist_name)
    return sanitized_name

def get_album_info(artist, album):
    payload = {
        'method': 'album.getinfo',
        'api_key': LASTFM_API_KEY,
        'artist': artist,
        'album': album,
        'format': 'json'
    }

    result = requests.get('http://ws.audioscrobbler.com/2.0/', params=payload)
    if result.status_code != 200:
        print(f"Error: {result.status_code}")
        print(result.text)
        return None

    album_data = result.json().get('album')
    return album_data

def fetch_album_info(song, artist):
    payload = {
        'method': 'track.getInfo',
        'api_key': LASTFM_API_KEY,
        'artist': artist,
        'track': song,
        'format': 'json'
    }

    result = requests.get('http://ws.audioscrobbler.com/2.0/', params=payload)
    if result.status_code != 200:
        print(f"Error: {result.status_code}")
        print(result.text)
        return None

    track_info = result.json().get('track')
    return track_info

def save_album_art(images, filename):
    if images:
        image_uri = images[-1]['#text']
        if image_uri:
            img_data = requests.get(image_uri).content
            with open(filename, 'wb') as handler:
                handler.write(img_data)
            print(f"Album art saved as '{filename}'")
        else:
            print("No valid image URI found.")
    else:
        print("No images found.")

# Test inputs
test_artist = "Talking Heads (Rock)"
test_song = "Burning Down the House"

# Sanitize artist name
sanitized_artist = sanitize_artist_name(test_artist)
print(f"Sanitized Artist Name: {sanitized_artist}")

# Fetch album info
track_info = fetch_album_info(test_song, sanitized_artist)

if track_info:
    print("\nTrack Info:")
    for key, value in track_info.items():
        print(f"{key}: {value}")

    album_info = track_info.get('album')
    if album_info:
        album_name = album_info.get('title', 'Unknown')
        images = album_info.get('image', [])
        print(f"\nAlbum Name: {album_name}")
        print("Album Images:")
        for img in images:
            print(f"Size: {img['size']}, URL: {img['#text']}")

        # Save album art if available
        save_album_art(images, os.path.join(TMP_DIR, 'test_albumart.jpg'))

        # If no album art found, make a secondary request using album name
        if not images or not images[-1]['#text']:
            print("No album art found initially. Fetching album info using album name...")
            album_data = get_album_info(sanitized_artist, album_name)
            if album_data:
                images = album_data.get('image', [])
                print("Fetched Album Images:")
                for img in images:
                    print(f"Size: {img['size']}, URL: {img['#text']}")
                save_album_art(images, os.path.join(TMP_DIR, 'test_albumart.jpg'))
            else:
                print("No album data found for the secondary request.")
    else:
        print("No album info found in track info.")
else:
    print("No track info found.")
