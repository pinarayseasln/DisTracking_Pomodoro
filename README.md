# 🏰 DisTracking – Pomodoro & Civilization

**DisTracking** is a Pomodoro-based web application that aims to make studying more productive and enjoyable through gamification.

Users earn points by completing focus sessions and gradually develop their own cities. In future versions, they will also be able to build a shared civilization with their friends.

## 🎯 Project Goal

The main goal of DisTracking is to combine the traditional Pomodoro technique with a city-building and progression system.

Instead of simply tracking study time, the application aims to motivate users by allowing them to see the results of their efforts through in-game rewards and progress.

## ✨ Features

### Currently Implemented
- [x] Pomodoro timer
- [x] Focus, short break, and long break modes
- [x] Start, pause, and reset timer controls
- [x] Main dashboard interface
- [x] Study room and marketplace interface
- [x] Random question API for mini challenges
- [x] Focus reset task library with category-based Strategy recommendations

### Planned Features
- [ ] Earn points by completing Pomodoro sessions
- [ ] Store user data using SQLite
- [ ] Resource system (wood, stone, and gold)
- [ ] Building construction and city development
- [ ] City levels and progression system
- [ ] Music and ambient sound options
- [ ] Daily goals and study statistics
- [ ] User registration and login
- [ ] Friend system and shared study rooms
- [ ] Build a shared civilization with friends

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web framework and API management |
| HTML | Web page structure |
| CSS | Interface design |
| JavaScript | Timer functionality and interactions |
| SQLite | Data storage (

### Focus reset tasks

The `/tasks` page contains five task categories and all 27 catalog entries. The `I lost concentration` flow maps the selected need to a recommendation strategy in `task_strategies.py`; each strategy recommends tasks from its own category. Mini-game interactions are placeholders until their game logic is implemented. Completing a task records it in SQLite and adds its XP to the existing points balance.

## Audio Files

The audio files are not included in this repository because of their file size
(GitHub does not accept files larger than 100 MB). Before running the app:

1. Download the mp3 files from [this Google Drive folder](https://drive.google.com/drive/folders/1dcinhR_wVjKo5hD9vGTqr3rJ0o4OyqeW?usp=sharing).
2. In the project's root folder, create the `static/audio` folder if it does not exist.
3. Place the downloaded files (`Cat.mp3`, `Fire.mp3`, `Forest.mp3`, `Meditation.mp3`, `Rain.mp3`) inside it.

Without these files the app still runs, but the ambient sounds will not play.
