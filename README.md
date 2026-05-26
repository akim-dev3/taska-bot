# Taska — Telegram Task Manager Bot

A clean, fully functional Telegram bot for personal task management. Built with Python and SQLite — no external services required.

**Bot:** [@taska_mng_bot](https://t.me/taska_mng_bot)

---

## Features

- Add tasks with `/add`
- View active tasks with inline Done / Delete buttons
- Mark tasks complete from the chat
- View completed tasks separately
- Progress stats with visual bar
- Per-user data isolation — each user sees only their own tasks
- SQLite storage — no external database needed

---

## Commands

| Command | Description |
|---|---|
| `/start` | Welcome message and command list |
| `/add <text>` | Add a new task |
| `/list` | Show active tasks with action buttons |
| `/done` | Show completed tasks |
| `/stats` | Progress summary |
| `/cleardone` | Delete all completed tasks |
| `/help` | Show command list |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Bot framework | aiogram 3.7 |
| Database | SQLite (built-in) |
| Config | python-dotenv |
| Deploy | Railway |

---

## Local Setup

```bash
git clone https://github.com/akim-dev3/taska-bot.git
cd taska-bot

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Add your BOT_TOKEN to .env

python bot.py
```

---

## Project Structure

```
taska-bot/
├── bot.py            — handlers, bot setup, entry point
├── database.py       — SQLite wrapper (init, CRUD)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Deploy to Railway

1. Push to GitHub
2. New project on [railway.app](https://railway.app) → Deploy from GitHub
3. Add environment variable: `BOT_TOKEN=your_token`
4. Start command: `python bot.py`

---

## License

MIT
