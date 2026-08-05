# 🚀 Google Antigravity Telegram Bot & Remote Control Bridge

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Creator](https://img.shields.io/badge/creator-TriWahyu45-orange.svg)

An advanced, asynchronous, multi-modal Telegram Bot bridge to remotely monitor, control, and interact with **Google Antigravity AI Agent** on Windows PC.

---

## ✨ Features

- 📌 **1-Click Desktop & System Tray Launcher (`tray_launcher.py`)**: Double-click to launch bot services and monitor active status directly from the **Windows System Tray (icon near clock)**.
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
├── tray_launcher.py             # System Tray App & Status Indicator (Icon near clock)
├── telegram_bot.py              # Main Telegram Polling & Command Handler
├── antigravity_injector.py      # CDP WebSocket Prompt Injection Engine
├── dom_mirror_final.py          # Real-time DOM Response & Progress Mirror
├── voice_synthesizer.py         # Natural Bilingual Fast TTS Voice Synthesizer
├── win_toggle.py                # C# Win32 Silent Window Show/Hide Toggle Engine
├── ScreenGrabber.cs             # Native C# Monitor Screen Capture Source
├── secrets_loader.py            # Dynamic Secrets & Credentials Loader
├── Start_Antigravity_Bot.vbs    # Double-click silent launcher
├── Start_Antigravity_Bot.bat    # Double-click batch launcher
├── secrets.example.json         # Credentials Template (Copy to secrets.json)
├── config.example.py            # Configuration Template (Copy to config.py)
├── antigravity_bot_architecture.md # Full Architecture & Technical Specification
└── .gitignore                   # Keeps API Keys, Tokens, Logs, and Temp Files Safe
```


---

## 🖥️ 1-Click Desktop & System Tray Usage

Double-click **`Start Antigravity Bot`** shortcut on your Desktop or run:
```cmd
Start_Antigravity_Bot.vbs
```
- A sleek **A** icon will appear in the Windows System Tray (bottom-right near the clock).
- Right-click the icon to view status, take screenshots, show/hide Antigravity, or restart services.

---

## 📖 Step-by-Step Setup Guide

### 1️⃣ Step 1: Create a Telegram Bot via `@BotFather`
1. Open Telegram and search for `@BotFather`.
2. Send the command `/newbot`.
3. Enter a display name (e.g. `My Antigravity Assistant`) and username ending in `bot` (e.g. `MyAntigravityPC_bot`).
4. Copy the **HTTP API Access Token**.

### 2️⃣ Step 2: Get Your Numeric Telegram User ID via `@userinfobot`
1. Search for `@userinfobot` on Telegram.
2. Send `/start`.
3. Copy your numeric User ID (e.g., `991501277`).

### 3️⃣ Step 3: Clone Repository & Configure Credentials
```bash
git clone https://github.com/triwahyu45/Antigravity_TelegramBot.git
cd Antigravity_TelegramBot
cp secrets.example.json secrets.json
```
Edit `secrets.json` and customize your settings:
```json
{
  "BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN_FROM_BOTFATHER",
  "ALLOWED_ID": YOUR_NUMERIC_TELEGRAM_USER_ID,
  "TARGET_CHAT_TITLE": "Wahyu's PC",
  "CHROME_PATH": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "ANTIGRAVITY_PATH": "C:\\Users\\YOUR_USERNAME\\AppData\\Local\\Programs\\antigravity\\Antigravity.exe",
  "AUTO_SCREENSHOT": true,
  "DUP_TIMEOUT": 300
}
```


### 4️⃣ Step 4: Install Dependencies & Compile ScreenGrabber
```bash
pip install -r requirements.txt
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:exe /out:ScreenGrabber.exe ScreenGrabber.cs
```

### 5️⃣ Step 5: Start the Bot
Double-click `Start_Antigravity_Bot.vbs` or run:
```bash
python tray_launcher.py
```

---

## 👤 Author & Maintainer
Created with ❤️ by **[TriWahyu45](https://github.com/triwahyu45)**  
Repository: **[github.com/triwahyu45/Antigravity_TelegramBot](https://github.com/triwahyu45/Antigravity_TelegramBot)**

---

## 📜 License
Licensed under the [MIT License](LICENSE).
