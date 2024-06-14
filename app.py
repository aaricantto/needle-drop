from flask import Flask, render_template, jsonify
from recognizer import record_audio, recognize_song, fetch_album_info, check_silence
import time
import threading

app = Flask(__name__)

song = None
artist = None
album = None

def listen_and_recognize():
    global song, artist, album
    while True:
        print("Recording audio...")
        audio_filename = record_audio()
        if not check_silence(audio_filename):
            print("Valid audio detected, recognizing song...")
            new_song, new_artist, _, success = recognize_song(audio_filename)
            if success:
                print(f"Song recognized: {new_song} by {new_artist}")
                if new_song != song or new_artist != artist:
                    song = new_song
                    artist = new_artist
                    print("Fetching album info...")
                    album, _ = fetch_album_info(song, artist)
                    if not album:
                        album = "Unknown"
            else:
                print("Song not recognized.")
                song = None
                artist = None
                album = None
        else:
            print("No valid audio input detected.")
            song = None
            artist = None
            album = None
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html', song=song, artist=artist, album=album)

@app.route('/update')
def update():
    return jsonify(song=song, artist=artist, album=album)

if __name__ == '__main__':
    threading.Thread(target=listen_and_recognize, daemon=True).start()
    app.run(debug=True, port=5001)
