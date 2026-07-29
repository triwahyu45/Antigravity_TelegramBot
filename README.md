# 🚀 Google Antigravity Telegram Bot & Remote Control Bridge

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Creator](https://img.shields.io/badge/creator-TriWahyu45-orange.svg)

An advanced, asynchronous, multi-modal Telegram Bot bridge to remotely monitor, control, and interact with **Google Antigravity AI Agent** on Windows PC.

---

## ✨ Features

- ⚡ **Seamless Prompt Injection**: Uses Chromium DevTools Protocol (CDP) WebSocket native hardware key events (`Input.dispatchKeyEvent`) to queue/submit prompts 100% reliably whether the agent is IDLE or WORKING.
- 💬 **Natural Conversation & Media Support**: Full support for Telegram quoted replies (`[Membalas: "..."]`), Photos, Videos, Voice Notes, Audio files, and Documents.
- 🙈 **100% Silent Background Mode (`SW_HIDE`)**: Completely hides the Antigravity window from the desktop and Windows taskbar without interrupting the Chromium V8 event loop.
- 📸 **Dual Screenshot Engine**:
  - **Physical PC Monitor Capture**: Native C# `ScreenGrabber.exe` captures actual monitor contents (Steam, Browser, Desktop).
  - **CDP Render Engine**: Captures high-resolution rendered Antigravity UI directly from Chromium memory.
- 🔄 **Real-Time DOM Mirroring**: Auto-streams AI responses, code edits, terminal execution logs, and generated images back to your Telegram chat.

---

## 📁 Repository Structure

```text
├── telegram_bot.py              # Main Telegram Polling & Command Handler
├── antigravity_injector.py      # CDP WebSocket Prompt Injection Engine
├── dom_mirror_final.py          # Real-time DOM Response & Progress Mirror
├── ScreenGrabber.cs             # Native C# Monitor Screen Capture Source
├── secrets_loader.py            # Dynamic Secrets & Credentials Loader
├── secrets.example.json         # Credentials Template (Copy to secrets.json)
├── config.example.py            # Configuration Template (Copy to config.py)
├── antigravity_bot_architecture.md # Full Architecture & Technical Specification
└── .gitignore                   # Keeps API Keys, Tokens, Logs, and Temp Files Safe
```

---

## 📖 Step-by-Step Setup Guide

### 1️⃣ Step 1: Create a Telegram Bot via `@BotFather`
1. Open Telegram and search for `@BotFather`.
2. Send the command `/newbot`.
3. Enter a display name for your bot (e.g. `My Antigravity Assistant`).
4. Enter a unique username ending in `bot` (e.g. `MyAntigravityPC_bot`).
5. `@BotFather` will generate an **HTTP API Access Token** (e.g., `8827974574:AAGYZSbOB612-Q8bSf9...`). **Copy and save this token**.

### 2️⃣ Step 2: Get Your Numeric Telegram User ID via `@userinfobot`
1. Search for `@userinfobot` or `@raw_data_bot` on Telegram.
2. Send `/start`.
3. The bot will respond with your numeric User ID (e.g., `991501277`). **Copy this ID**.  
   *(This ensures that ONLY YOU have authorization to control your PC bot).*

### 3️⃣ Step 3: Clone Repository & Configure Credentials
Clone the repository:
```bash
git clone https://github.com/triwahyu45/Antigravity_TelegramBot.git
cd Antigravity_TelegramBot
```
Copy `secrets.example.json` to `secrets.json`:
```bash
cp secrets.example.json secrets.json
```
Edit `secrets.json` and paste your Bot Token and User ID:
```json
{
  "BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN_FROM_BOTFATHER",
  "ALLOWED_ID": YOUR_NUMERIC_TELEGRAM_USER_ID
}
```

### 4️⃣ Step 4: Install Dependencies & Compile ScreenGrabber
Install Python dependencies:
```bash
pip install -r requirements.txt
```
*(Optional)* Compile the native C# ScreenGrabber executable:
```cmd
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:exe /out:ScreenGrabber.exe ScreenGrabber.cs
```

### 5️⃣ Step 5: Start the Bot & DOM Mirror
Run the main Telegram Receiver & Prompt Injector:
```bash
python telegram_bot.py
```
In a second terminal window, launch the Real-Time DOM Mirror:
```bash
python dom_mirror_final.py
```

---

## 🛡️ Security Note

- **Secrets Protection**: `secrets.json`, `config.py`, `.env`, Telegram Bot Tokens, personal chat IDs, screenshot images, and logs are excluded via `.gitignore` to ensure **100% public safety**.
- **User Authorization**: All incoming commands are strictly checked against `ALLOWED_ID`.

---

## 👤 Author & Maintainer
Created with ❤️ by **[TriWahyu45](https://github.com/triwahyu45)**  
Repository: **[github.com/triwahyu45/Antigravity_TelegramBot](https://github.com/triwahyu45/Antigravity_TelegramBot)**

---

## 📜 License
Licensed under the [MIT License](LICENSE).
