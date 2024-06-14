import pyaudio
import requests
import json
import time
import os
import wave
import re
from dotenv import load_dotenv
from PIL import Image
import numpy as np

# Load credentials from .env file
load_dotenv()
AUDIOTAG_API_KEY = os.getenv('AUDIOTAG_API_KEY')
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
TMP_DIR = './static/'  # Temporary directory path

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 20  # Increased recording time to 20 seconds
DEVICE_INDEX = 2
THRESHOLD = 20  # Threshold for silence detection

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    input_device_index=DEVICE_INDEX,
                    frames_per_buffer=CHUNK)

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_filename = os.path.join(TMP_DIR, 'audiochunk.wav')
    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return audio_filename

def check_silence(audio_filename):
    wf = wave.open(audio_filename, 'rb')
    frames = wf.readframes(wf.getnframes())
    wf.close()
    audio_data = np.frombuffer(frames, dtype=np.int16)
    return max(audio_data) < THRESHOLD

def recognize_song(audio_filename):
    payload = {'action': 'identify', 'apikey': AUDIOTAG_API_KEY}
    with open(audio_filename, 'rb') as audio_file:
        files = {'file': audio_file}
        result = requests.post('https://audiotag.info/api', data=payload, files=files)

    json_object = result.json()
    token = json_object.get('token')

    if not token:
        return None, None, None, False

    payload = {'action': 'get_result', 'token': token, 'apikey': AUDIOTAG_API_KEY}
    while True:
        song_result = requests.post('https://audiotag.info/api', data=payload)
        song_info = song_result.json()

        if song_info['result'] == 'wait':
            time.sleep(1)
        else:
            break

    if song_info['result'] == 'not found':
        return None, None, None, False

    hit_info = song_info['data'][0]['tracks'][0]
    song = hit_info[0]
    artist = hit_info[1]
    album = hit_info[2]

    # Remove any content within parentheses from the artist name
    artist = re.sub(r'\s*\(.*?\)\s*', '', artist)

    return song, artist, album, True

def get_album_info_by_song(song):
    payload = {
        'method': 'track.getInfo',
        'api_key': LASTFM_API_KEY,
        'track': song,
        'format': 'json'
    }

    result = requests.get('http://ws.audioscrobbler.com/2.0/', params=payload)
    if 'error' in result.text:
        return None, None

    track_info = result.json().get('track')
    if not track_info:
        return None, None

    album_info = track_info.get('album')
    if not album_info:
        return None, None

    album_name = album_info.get('title', 'Unknown')
    images = album_info.get('image', [])
    return album_name, images

def get_album_info(artist, album):
    payload = {
        'method': 'album.getinfo',
        'api_key': LASTFM_API_KEY,
        'artist': artist,
        'album': album,
        'format': 'json'
    }

    result = requests.get('http://ws.audioscrobbler.com/2.0/', params=payload)
    if 'error' in result.text:
        return None, None

    album_data = result.json().get('album')
    if not album_data:
        return None, None

    images = album_data.get('image', [])
    return album, images

def fetch_album_info(song, artist):
    payload = {
        'method': 'track.getInfo',
        'api_key': LASTFM_API_KEY,
        'artist': artist,
        'track': song,
        'format': 'json'
    }

    result = requests.get('http://ws.audioscrobbler.com/2.0/', params=payload)
    if 'error' in result.text:
        return None, None

    track_info = result.json().get('track')
    if not track_info:
        return None, None

    album_info = track_info.get('album')
    album_name = None
    images = None

    if album_info:
        album_name = album_info.get('title', 'Unknown')
        images = album_info.get('image', [])

    if not images or not images[-1]['#text']:
        print("No album art found initially. Fetching album info using album name...")
        album_data = get_album_info(artist, album_name)
        if album_data:
            _, images = album_data

    if images:
        save_album_art(images, os.path.join(TMP_DIR, 'albumart.jpg'))

    return album_name, None

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
