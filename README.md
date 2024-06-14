# Needle Drop - Vinyl Recognition and Album Art Display

This project is a web application that listens to vinyl records playing through a connected audio input, recognizes the song, artist, and album, and displays the corresponding album art along with song information on a web page. The project leverages the ACRCloud and Last.fm APIs for song recognition and fetching album information, respectively.

## Features

- **Audio Recording**: Records audio from a specified input device.
- **Song Recognition**: Recognizes the song, artist, and album using the ACRCloud API.
- **Album Art Fetching**: Retrieves album art from Last.fm, with a fallback mechanism to ensure album art is found.
- **Web Display**: Displays the current song, artist, album, and album art on a web page that updates in real-time.

## Setup

### Prerequisites

- Python 3.x
- Flask
- pyaudio
- requests
- python-dotenv
- PIL (Pillow)
- NumPy

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/now-spinning.git
    cd now-spinning
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file** in the root directory and add your API keys:
    ```env
    AUDIOTAG_API_KEY=your_audiotag_api_key
    LASTFM_API_KEY=your_lastfm_api_key
    ```

5. **List available audio input devices**:
    Run the `listen.py` script to list available audio input devices and choose the appropriate device ID.
    ```bash
    python listen.py
    ```

6. **Update `recognizer.py`**:
    Set `DEVICE_INDEX` to the ID of your chosen audio input device in `recognizer.py`.

### Running the Application

1. **Start the Flask application**:
    ```bash
    python app.py
    ```

2. **Open your web browser** and navigate to `http://127.0.0.1:5001` to view the Now Spinning interface.

## Project Structure

- **app.py**: Main Flask application that handles routing and initializes the background thread for audio recording and song recognition.
- **recognizer.py**: Contains functions for recording audio, recognizing songs, and fetching album information and art.
- **templates/index.html**: Frontend template that displays the current song, artist, album, and album art.
- **static/**: Directory to store static files such as the album art image.
- **test_call.py**: Script for testing the Last.fm API integration.
- **listen.py**: Script for listing available audio input devices.

## How It Works

1. **Audio Recording**: The `listen_and_recognize` function in `app.py` records audio from the specified input device using the `record_audio` function in `recognizer.py`.
2. **Song Recognition**: The recorded audio is sent to the ACRCloud API for song recognition via the `recognize_song` function.
3. **Album Info Fetching**: If the song is recognized, the `fetch_album_info` function fetches album information from Last.fm. If the initial request does not provide valid album art, a secondary request is made using the album name.
4. **Web Display**: The recognized song, artist, album, and album art are displayed on a web page that updates every 5 seconds.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

