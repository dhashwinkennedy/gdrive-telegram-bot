# 📤 Google Drive Upload Telegram Bot
 
[#-google-drive-upload-telegram-bot](#-google-drive-upload-telegram-bot)
 
### Send a file to your Telegram bot and watch it land straight in Google Drive — powered by a FastAPI backend, a dedicated bot service, and a lightweight frontend
 
[#send-a-file-to-your-telegram-bot-and-watch-it-land-straight-in-google-drive--powered-by-a-fastapi-backend-a-dedicated-bot-service-and-a-lightweight-frontend](#send-a-file-to-your-telegram-bot-and-watch-it-land-straight-in-google-drive--powered-by-a-fastapi-backend-a-dedicated-bot-service-and-a-lightweight-frontend)
 
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=FFD43B)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![Google Drive API](https://img.shields.io/badge/Google%20Drive-API-4285F4?style=flat-square&logo=googledrive&logoColor=white)
![python-dotenv](https://img.shields.io/badge/python--dotenv-Env%20Config-ECD53F?style=flat-square&logo=dotenv&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)
 
> A three-part automation stack that receives a file from a Telegram chat, streams it through a FastAPI backend,
> and uploads it directly to **Google Drive** — with a customizable upload limit and no manual handling required.
 
---
 
## ✨ Key Features
 
[#-key-features](#-key-features)
 
| Feature                          | Description                                                                                   |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| 🤖 **Telegram File Intake**       | Users send any file directly to the bot in a Telegram chat — no external app required           |
| ⚡ **FastAPI Backend**             | A lightweight, high-performance Python backend handles routing, validation, and upload requests |
| ☁️ **Direct Google Drive Upload** | Files are streamed straight to a configured Google Drive folder via the Google Drive API        |
| 📏 **Customizable Upload Limit**  | The maximum file size accepted by the bot is configurable from a single `.env` variable          |
| 🧩 **Decoupled Components**       | Frontend, Bot, and Backend are independent services that can be deployed and scaled separately   |
| 🔐 **Secure Config Management**   | All credentials and secrets are managed via `.env` — never hardcoded into source files           |
 
---
 
## 🏗️ Architecture & Workflow
 
[#️-architecture--workflow](#️-architecture--workflow)
 
The project is split into three independent components that communicate over HTTP:
 
```
┌─────────────────────────────────────────────────────────────────────┐
│                      SYSTEM ARCHITECTURE OVERVIEW                   │
└─────────────────────────────────────────────────────────────────────┘
 
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │              │     │              │     │              │     │              │
  │   Frontend   │ ──► │  Telegram    │ ──► │   Backend    │ ──► │   Google     │
  │              │     │  Bot         │     │  (FastAPI)   │     │   Drive API  │
  │  Dashboard / │     │              │     │              │     │              │
  │  status view │     │  Listens for │     │  Validates,  │     │  Stores the  │
  │  for uploads │     │  incoming    │     │  enforces    │     │  uploaded    │
  │              │     │  files from  │     │  size limit, │     │  file in the │
  │              │     │  users       │     │  streams     │     │  target      │
  │              │     │              │     │  upload      │     │  folder      │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
 
     COMPONENT 1          COMPONENT 2           COMPONENT 3          DESTINATION
     FRONTEND              TELEGRAM BOT          BACKEND (API)        GOOGLE DRIVE
```
 
Each component is designed to run and deploy **independently** — the Bot forwards file events to the Backend over its API, and the Backend is the only component that talks to Google Drive directly.
 
---
 
## 🛠️ Tech Stack
 
[#️-tech-stack](#️-tech-stack)
 
- **Core Language** — Python
- **Backend Framework** — FastAPI
- **Bot Framework** — Telegram Bot API
- **Storage** — Google Drive API
- **Config Management** — python-dotenv
- **Frontend** — Standalone client (deployed separately from the Bot/Backend)
---
 
## 📦 Dependencies
 
[#-dependencies](#-dependencies)
 
All required Python packages are listed in `requirements.txt`. Install them with:
 
```bash
pip install -r requirements.txt
```
 
| Package                   | Role                                                              |
| -------------------------- | ------------------------------------------------------------------ |
| `fastapi`                 | Powers the backend API that receives and routes upload requests    |
| `uvicorn`                 | ASGI server used to run the FastAPI backend                        |
| `python-telegram-bot`     | Handles the Telegram bot's message and file-event listeners        |
| `google-api-python-client`| Talks to the Google Drive API to perform the file upload           |
| `google-auth-oauthlib`    | Manages Google OAuth2 authentication for Drive access              |
| `python-dotenv`           | Loads all credentials and configuration securely from the `.env` file |
| `requests`                | Handles HTTP calls between the Bot and Backend components          |
 
> **Note:** If your `bot/` and `backend/` components ship separate `requirements.txt` files, run the install command inside each component's directory.
 
---
 
## 🚀 Installation & Setup
 
[#-installation--setup](#-installation--setup)
 
### 1️⃣ Fork the Repository
 
[#1️⃣-fork-the-repository](#1️⃣-fork-the-repository)
 
Start by forking this repository to your own GitHub account using the **Fork** button at the top of the page, then clone your fork locally:
 
```bash
git clone https://github.com/<your-username>/Google-Drive-Upload-Telegram-Bot.git
cd Google-Drive-Upload-Telegram-Bot
```
 
### 2️⃣ Create and Activate a Virtual Environment
 
[#2️⃣-create-and-activate-a-virtual-environment](#2️⃣-create-and-activate-a-virtual-environment)
 
```bash
# Create the virtual environment
python -m venv bot-venv
 
# Activate — macOS/Linux:
source bot-venv/bin/activate
 
# Activate — Windows:
.\bot-venv\Scripts\activate
```
 
> ⚠️ **Do not commit `bot-venv/` to your repository.** It is a local dependency folder, not project source code — make sure it's listed in your `.gitignore` before pushing any changes.
 
### 3️⃣ Install Dependencies
 
[#3️⃣-install-dependencies](#3️⃣-install-dependencies)
 
```bash
pip install -r requirements.txt
```
 
### 4️⃣ Configure Environment Variables
 
[#4️⃣-configure-environment-variables](#4️⃣-configure-environment-variables)
 
Copy the example environment file and fill in your own credentials:
 
```bash
cp .env.example .env
```
 
Then open `.env` and replace each placeholder with your real values (see the **Environment Variables** section below for the full reference).
 
### 5️⃣ Separate the Components for Deployment
 
[#5️⃣-separate-the-components-for-deployment](#5️⃣-separate-the-components-for-deployment)
 
The **Frontend**, **Telegram Bot**, and **Backend** are built to be deployed as independent services rather than a single monolith. Before deploying:
 
- Move or point each component (`frontend/`, `bot/`, `backend/`) to its own deployment target (e.g., separate services, containers, or hosting platforms)
- Make sure each component has its own environment configuration pointing to the correct URLs of the others
- From the `frontend/` directory, run the standard build command to generate the production build:
```bash
npm install
npm run build
```
 
### 6️⃣ Run the Bot and Backend
 
[#6️⃣-run-the-bot-and-backend](#6️⃣-run-the-bot-and-backend)
 
```bash
# Start the FastAPI backend
cd backend
uvicorn main:app --reload
 
# In a separate terminal, start the Telegram bot
cd bot
python bot.py
```
 
Once both are running, send a file to your bot on Telegram — it will be validated against your configured upload limit and uploaded straight to Google Drive.
 
---
 
## 🔑 Environment Variables
 
[#-environment-variables](#-environment-variables)
 
Create a `.env` file in the project root using the structure below. A template is provided as `.env.example`.
 
```env
# ─────────────────────────────────────────
# Telegram Bot
# ─────────────────────────────────────────
TELEGRAM_BOT_TOKEN = YOUR_TELEGRAM_BOT_TOKEN
 
# ─────────────────────────────────────────
# FastAPI Backend
# ─────────────────────────────────────────
BACKEND_HOST = 0.0.0.0
BACKEND_PORT = 8000
BACKEND_URL  = http://localhost:8000
 
# ─────────────────────────────────────────
# Google Drive API
# ─────────────────────────────────────────
GOOGLE_CLIENT_ID       = YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET   = YOUR_GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN   = YOUR_GOOGLE_REFRESH_TOKEN
GOOGLE_DRIVE_FOLDER_ID = YOUR_TARGET_FOLDER_ID
 
# ─────────────────────────────────────────
# Upload Settings
# ─────────────────────────────────────────
# Maximum file size accepted by the bot, in megabytes.
# Adjust this value freely to raise or lower the upload limit.
MAX_FILE_SIZE_MB = 50
```
 
### Where to obtain each credential:
 
[#where-to-obtain-each-credential](#where-to-obtain-each-credential)
 
| Variable                                    | Source                                                                                       |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `TELEGRAM_BOT_TOKEN`                        | [@BotFather](https://t.me/BotFather) on Telegram                                              |
| `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` | [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials      |
| `GOOGLE_REFRESH_TOKEN`                      | Generated via the Google OAuth2 consent flow for your Drive API credentials                    |
| `GOOGLE_DRIVE_FOLDER_ID`                    | The folder ID from your target Google Drive folder's URL                                       |
| `MAX_FILE_SIZE_MB`                          | Set by you — this directly controls the largest file the bot will accept                       |
 
---
 
## 📋 Guidelines
 
[#-guidelines](#-guidelines)
 
Warning
 
**Keep these in mind before you deploy or contribute**
 
- **Fork before you build.** Always work from your own fork so your credentials and changes stay isolated from the upstream repository.
- **Never push `bot-venv/` to your repository.** It's a local virtual environment folder full of installed packages, not project code — confirm it's listed in `.gitignore` before every commit and push.
- **Deploy components separately.** The Frontend, Telegram Bot, and Backend are decoupled by design. Deploy each one to its own host/service and run the standard build command (e.g., `npm run build`) for the Frontend before shipping it.
- **Tune the upload limit to your use case.** The `MAX_FILE_SIZE_MB` variable in `.env` controls the maximum file size the bot will accept — raise or lower it based on your Google Drive quota and hosting constraints.
- **Never hardcode secrets.** All tokens and API keys belong in `.env`, which should always be excluded from version control via `.gitignore`.
- **Install dependencies per component.** Run `pip install -r requirements.txt` inside whichever component (bot or backend) you're actively working on or deploying.
---
 
## 📁 Project Structure
 
[#-project-structure](#-project-structure)
 
```
Google-Drive-Upload-Telegram-Bot/
├── frontend/             # 🖥️  Standalone client, deployed independently
├── bot/                  # 🤖 Telegram bot service (listens for file events)
├── backend/              # ⚡ FastAPI service (validates & uploads to Drive)
├── .env.example          # 🔑 Safe environment variable template (no real keys)
├── .env                  # 🔒 Your actual credentials (git-ignored)
├── bot-venv/              # 🚫 Local virtual environment (git-ignored, never pushed)
├── requirements.txt       # 📦 Python dependencies
└── README.md              # 📄 Project documentation
```
 
---
 
## 🗺️ Roadmap
 
[#️-roadmap](#️-roadmap)
 
- [ ] 📊 Upload progress and history dashboard in the Frontend
- [ ] 🗂️ Support for uploading directly into user-selected Drive subfolders
- [ ] 🔁 Retry logic for failed or interrupted uploads
- [ ] 👥 Multi-user access control for shared bot deployments
- [ ] 🐳 Docker Compose setup for one-command local deployment
---
 
## 📄 License
 
[#-license](#-license)
 
This project is licensed under the **MIT License** — see the [LICENSE](https://github.com/dhashwinkennedy/Google-Drive-Upload-Telegram-Bot/blob/main/LICENSE) file for details.
 
---
 
Built with 🤖 Telegram Bot API · ⚡ FastAPI · ☁️ Google Drive API
 
*From a chat message to a Drive file — fully automated.*
 
