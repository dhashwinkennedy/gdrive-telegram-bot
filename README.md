# 📤 Google Drive Upload Telegram Bot



### Send a file to your Telegram bot and watch it land straight in Google Drive — a two-service Python stack built with FastAPI, Google OAuth, and MongoDB


![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=FFD43B)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![Google OAuth](https://img.shields.io/badge/Google-OAuth%202.0-4285F4?style=flat-square&logo=google&logoColor=white)
![Google Drive API](https://img.shields.io/badge/Google%20Drive-API-4285F4?style=flat-square&logo=googledrive&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?style=flat-square&logo=mongodb&logoColor=white)
![python-dotenv](https://img.shields.io/badge/python--dotenv-Env%20Config-ECD53F?style=flat-square&logo=dotenv&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)

> A two-service automation stack — a Telegram-facing **Bot** and an OAuth-aware **Backend** — that authenticates
> a user's Google account, receives a file from a Telegram chat, and uploads it directly to **Google Drive**,
> with a fully configurable upload limit and request timeout. Pure Python. No Node.js involved.

---

**🔗 [Try the live sample bot on Telegram](https://t.me/Gdrive_testbot)** — test the upload flow yourself before setting up your own instance.
## ✨ Key Features


| Feature                          | Description                                                                                     |
| --------------------------------- | --------------------------------------------------------------------------------------------------- |
| 🤖 **Telegram File Intake**       | Users send any file directly to the bot in a Telegram chat — no external app required               |
| ⚡ **FastAPI Backend**             | A dedicated Python/FastAPI service handles Google OAuth, file uploads, and data persistence         |
| 🔑 **Google OAuth 2.0 Flow**      | Users securely link their own Google account via a standard OAuth authorization + callback flow      |
| ☁️ **Direct Google Drive Upload** | Files are streamed straight to the authenticated user's Google Drive                                 |
| 🗄️ **MongoDB Persistence**       | User sessions and OAuth tokens are stored and retrieved via MongoDB                                  |
| 🔐 **HMAC-Secured Requests**      | A shared `BOT_HMAC_SECRET` signs requests between the Bot and Backend to prevent tampering            |
| 📏 **Customizable Upload Limit**  | Max file size (`UPLOAD_LENGTH`) and upload timeout (`UPLOAD_TIME`) are configurable from `.env`       |
| 🧩 **Fully Decoupled Services**   | The Bot and Backend are independent Python services, each with their own venv and dependencies       |

---

## 🏗️ Architecture & Workflow


The project is split into **two independent Python services** that communicate over HTTP, secured with an HMAC signature:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE OVERVIEW                      │
└───────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────┐    HMAC-signed    ┌────────────────────┐    OAuth /   ┌──────────────┐
  │                     │     requests      │                    │    Upload    │              │
  │   Bot (Frontend)    │ ────────────────► │      Backend       │ ───────────► │  Google Drive│
  │                     │                   │      (FastAPI)     │              │      API     │
  │  Listens for chats, │ ◄──────────────── │                    │ ◄─────────── │              │
  │  forwards files to  │     responses     │  Handles Google    │   tokens /   └──────────────┘
  │  the Backend        │                   │  OAuth, uploads,   │   status
  │                     │                   │  and MongoDB       │              ┌──────────────┐
  │  python main.py     │                   │  persistence       │ ───────────► │   MongoDB    │
  │                     │                   │                    │              │              │
  │                     │                   │  uvicorn main:app  │ ◄─────────── │  User + token│
  └────────────────────┘                   └────────────────────┘              │  storage     │
                                                                                 └──────────────┘

        SERVICE 1                                  SERVICE 2                        STORAGE
        bot/ folder                                backend/ folder
```

Each service lives in its own folder, ships its own `requirements.txt` and `.env.example`, and is meant to be **forked, deployed, and run independently**.

---

## 🛠️ Tech Stack


- **Core Language** — Python (no Node.js/JavaScript involved anywhere in the stack)
- **Bot Service** — Telegram Bot API, run via `python main.py`
- **Backend Service** — FastAPI, run via `uvicorn main:app`
- **Authentication** — Google OAuth 2.0
- **Storage** — Google Drive API (files) + MongoDB (users/tokens)
- **Config Management** — python-dotenv

---

## 📦 Dependencies


Each service manages its **own** `requirements.txt`. Install them separately from inside each folder:

```bash
# Inside bot/
pip install -r requirements.txt

# Inside backend/
pip install -r requirements.txt
```

| Package                    | Used In    | Role                                                                 |
| ---------------------------- | ----------- | ----------------------------------------------------------------------- |
| `fastapi`                  | backend    | Powers the API that handles OAuth, uploads, and session routes          |
| `uvicorn`                  | backend    | ASGI server used to run the FastAPI backend                             |
| `pymongo`                  | backend    | Connects to MongoDB to persist user sessions and OAuth tokens           |
| `google-auth`              | backend    | Verifies and refreshes Google OAuth tokens                              |
| `requests`                 | bot, backend | Handles HTTP calls, including OAuth token exchange and inter-service calls |
| `python-telegram-bot`      | bot        | Listens for and handles incoming Telegram messages and files            |
| `python-dotenv`            | bot, backend | Loads credentials and configuration securely from each `.env` file      |

> Package names above reflect the typical role each library plays — check each folder's own `requirements.txt` for the exact pinned versions.

---

## 🚀 Installation & Setup


### 1️⃣ Fork the Repository



Fork this repository to your own GitHub account using the **Fork** button at the top of the page, then clone your fork locally:

```bash
git clone https://github.com/<your-username>/Google-Drive-Upload-Telegram-Bot.git
cd Google-Drive-Upload-Telegram-Bot
```

### 2️⃣ Split the Project into Two Services

This project is designed to run as **two separate services**, not a single monolith:

- **`backend/`** — the Bot Backend (FastAPI + Google OAuth + MongoDB)
- **`bot/`** — the Bot Frontend (the Telegram-facing bot service)

Deploy each folder as its own repository/service (e.g., push each to its own host or container), so they can be scaled, restarted, and updated independently of one another.

### 3️⃣ Set Up the Backend


```bash
cd backend

# Create and activate a dedicated virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
.\venv\Scripts\activate       # Windows

# Install backend dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Open `backend/.env` and fill in your Google OAuth, MongoDB, and Telegram credentials (see **Environment Variables** below).

Run the backend:

```bash
uvicorn main:app --reload
```

### 4️⃣ Set Up the Bot (Frontend)

```bash
cd bot

# Create and activate a separate virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
.\venv\Scripts\activate       # Windows

# Install bot dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Open `bot/.env` and fill in your Telegram bot token, HMAC secret, and backend URL (see **Environment Variables** below).

Run the bot:

```bash
python main.py
```

Once both services are running, send a file to your bot on Telegram — it will authenticate the request, check it against your configured upload limit, and upload it to Google Drive.

---

## 🔑 Environment Variables


Each service has its **own** `.env`, created from its own `.env.example`. Keep the two separate — never merge them into one file.

### `bot/.env.example` — Bot (Frontend)


```env
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
BOT_HMAC_SECRET=your_bot_hmac_secret_here

# Backend Service Configuration
BACKEND_URL=http://127.0.0.1:8000

# File Upload Settings
UPLOAD_LENGTH=1      # Max upload limit in MB
UPLOAD_TIME=300      # Upload request timeout in seconds
```

### `backend/.env.example` — Backend


```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI={YOUR_BACKEND_URL}/google/callback

# Google OAuth Endpoints
TOKEN_URL=https://oauth2.googleapis.com/token
USER_INFO_URL=https://www.googleapis.com/oauth2/v2/userinfo
ACCESS_TOKEN_URL=https://oauth2.googleapis.com/token
GOOGLE_AUTH_URL=https://accounts.google.com/o/oauth2/v2/auth

# Database Configuration
MONGO_URI=your_mongodb_uri_here

# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
BOT_HMAC_SECRET=your_bot_hmac_secret_here
```

### Where to obtain each credential:


| Variable                                          | Source                                                                                  |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `BOT_TOKEN`                                        | [@BotFather](https://t.me/BotFather) on Telegram                                            |
| `BOT_HMAC_SECRET`                                  | Self-generated secret (e.g. `openssl rand -hex 32`) — **must match exactly** in both `.env` files |
| `BACKEND_URL`                                      | The URL where your `backend/` service is running or deployed                                |
| `UPLOAD_LENGTH` / `UPLOAD_TIME`                    | Set by you — controls the max file size (MB) and upload timeout (seconds) the bot accepts   |
| `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`       | [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials    |
| `GOOGLE_REDIRECT_URI`                              | Your deployed backend URL + `/google/callback`                                              |
| `TOKEN_URL` / `USER_INFO_URL` / `ACCESS_TOKEN_URL` / `GOOGLE_AUTH_URL` | Fixed Google OAuth 2.0 endpoints — use the defaults shown above                |
| `MONGO_URI`                                        | [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) or your own self-hosted MongoDB instance |

---

## 📋 Guidelines


Warning

**Keep these in mind before you deploy or contribute**

- **Fork before you build.** Always work from your own fork so your credentials and changes stay isolated from the upstream repository.
- **Treat `bot/` and `backend/` as two separate services.** Each has its own virtual environment, its own `requirements.txt`, and its own `.env` — don't merge them or share a single venv between the two.
- **Never push either virtual environment folder to your repository.** Confirm `venv/` (or however you name it) is listed in `.gitignore` in **both** `bot/` and `backend/` before every commit and push.
- **Keep `BOT_HMAC_SECRET` identical across both services.** The Bot signs requests with this secret and the Backend verifies them — a mismatch will cause every request to be rejected.
- **Tune the upload limit and timeout to your use case.** `UPLOAD_LENGTH` (MB) and `UPLOAD_TIME` (seconds) in `bot/.env` control what the bot will accept — adjust based on your Google Drive quota and hosting constraints.
- **Never hardcode secrets.** All tokens, OAuth credentials, and the MongoDB URI belong in `.env`, which should always be excluded from version control via `.gitignore`.
- **This is a pure Python stack.** There is no Node.js, npm, or frontend build step anywhere in this project — both services are started directly with Python (`uvicorn main:app` for the backend, `python main.py` for the bot).

---

## 📁 Project Structure


```
Google-Drive-Upload-Telegram-Bot/
├── backend/                # ⚡ FastAPI service — Google OAuth, uploads, MongoDB
│   ├── main.py              # Entry point — run via `uvicorn main:app`
│   ├── venv/                 # 🚫 Local virtual environment (git-ignored, never pushed)
│   ├── .env.example          # 🔑 Safe environment variable template (no real keys)
│   ├── .env                  # 🔒 Your actual backend credentials (git-ignored)
│   └── requirements.txt      # 📦 Backend-only Python dependencies
├── bot/                     # 🤖 Telegram bot service (frontend)
│   ├── main.py               # Entry point — run via `python main.py`
│   ├── venv/                  # 🚫 Local virtual environment (git-ignored, never pushed)
│   ├── .env.example           # 🔑 Safe environment variable template (no real keys)
│   ├── .env                   # 🔒 Your actual bot credentials (git-ignored)
│   └── requirements.txt       # 📦 Bot-only Python dependencies
├── .gitignore
└── README.md                # 📄 Project documentation
```

---

## 🗺️ Roadmap


- [ ] 🗂️ Support for uploading directly into user-selected Drive subfolders
- [ ] 🔁 Retry logic for failed or interrupted uploads
- [ ] 👥 Multi-user session management via MongoDB
- [ ] 📊 Upload history and status command inside the Telegram bot
- [ ] 🐳 Docker Compose setup to run both services with one command

---

## 📄 License


This project is licensed under the **MIT License** — see the [LICENSE](https://github.com/dhashwinkennedy/Google-Drive-Upload-Telegram-Bot/blob/main/LICENSE) file for details.

---

Built with 🤖 Telegram Bot API · ⚡ FastAPI · 🔑 Google OAuth · 🗄️ MongoDB

*From a chat message to a Drive file — fully automated.*
