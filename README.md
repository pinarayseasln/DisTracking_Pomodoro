# DisTracking

DisTracking is a Flask and SQLite Pomodoro app with focus reset tasks and lightweight city-building rewards.

## Features

- Focus, short-break, and long-break timer modes
- Configurable focus duration and completion sound
- Points for completed focus sessions and reset tasks
- Daily quests linked to Pomodoro progress
- Focus reset task catalog and category-based recommendations
- Building marketplace and ambient audio player
- Random mini-challenge question API

The app currently uses one shared local profile. Account login, friend features, shared cities, and interactive mini-games are not implemented. Some city and theme views are interface prototypes.

## Run locally

Requires Python 3.14 or newer. Install dependencies and start the Flask app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The database schema is initialized when the Flask app starts. The local database file is `distracking.db` and is excluded from Git.

## Audio files

Audio files are excluded from this repository because of their size. Download the MP3 files from [the project's Google Drive folder](https://drive.google.com/drive/folders/1dcinhR_wVjKo5hD9vGTqr3rJ0o4OyqeW?usp=sharing) and place `Cat.mp3`, `Fire.mp3`, `Forest.mp3`, `Meditation.mp3`, and `Rain.mp3` in `static/audio/`. The app runs without them, but ambient sounds will not play.

## Project layout

- `app.py`: Flask application and blueprint registration
- `routes/`: page and API routes
- `models/`: database operations and feature logic
- `database/db.py`: SQLite schema and connections
- `task_library.py`, `task_strategies.py`: task catalog and recommendation strategies
- `templates/`, `static/`: web interface, styles, backgrounds, and audio
- `tests/`: Flask route and model tests

Run the test suite with `python -m pytest` after installing pytest.