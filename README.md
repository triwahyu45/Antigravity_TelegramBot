# 🚀 Google Antigravity Telegram Bot & Remote Control Bridge

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Creator](https://img.shields.io/badge/creator-TriWahyu45-orange.svg)
![Release](https://img.shields.io/badge/release-v6.0-green.svg)

An advanced, asynchronous, multi-modal Telegram Bot bridge to remotely monitor, control, and interact with **Google Antigravity AI Agent** & Windows PC Desktop.

---

## ✨ Features

- 🕹️ **Physical PC Mouse & Keyboard Remote Control (`pc_remote_control.py`)**: Remote click, double click, scroll, enter, browser back (`Alt+Left`), home navigation, and video controls directly from Telegram.
- ⚙️ **User-Customizable Configuration Engine (`secrets.json` & `secrets_loader.py`)**: Easily configure Bot Token, Allowed User ID, Target Antigravity Workspace/Chat Title, Chrome Executable Path, and Antigravity Path.
- 📸 **Automatic Live Screenshot Verification (`v5.0+`)**: Every remote control action automatically triggers a real-time physical PC screen capture sent directly to your Telegram chat.
- 📌 **1-Click System Tray Launcher (`tray_launcher.py`)**: Double-click to launch bot services and monitor active status directly from the **Windows System Tray**.
- ⚡ **Seamless Lexical Multiline Prompt Injection**: Uses Chromium DevTools Protocol (CDP) WebSocket native hardware key events (`document.execCommand('insertText')`) to preserve linebreaks, enter, and dash bullet lists (`-`).
- 💬 **Natural Conversation & Media Support**: Full support for Telegram quoted replies (`[Membalas: "..."]`), Photos, Photo Albums (Media Groups), Videos, Voice Notes, Audio files, and Documents.
- 🙈 **100% Silent Background Mode (`SW_HIDE`)**: Completely hides the Antigravity window from the desktop and Windows taskbar without interrupting the Chromium V8 event loop.
- 🔄 **Strict Single-Turn DOM Mirroring**: Real-time response streaming with deduplication filters, formula sanitization ($\varepsilon_r \rightarrow \varepsilon_r$), and markdown formatting.

---

## 📁 Repository Structure

```text
├── telegram_bot.py              # Main Telegram Polling & Remote Control Handler
├── dom_mirror_final.py          # Real-time Strict Single-Turn DOM Scraper & Stream Mirror
├── antigravity_injector.py      # CDP WebSocket Multiline Lexical Injection Engine
├── pc_remote_control.py         # Physical Mouse & Keyboard Automation Engine
├── secrets_loader.py            # Dynamic Customizable Config & Credentials Loader
├── secrets.json                 # User Configuration File (Token, ID, Paths, Settings)
├── config.example.json          # Configuration Template for End Users
├── ScreenGrabber.cs             # Native C# Monitor Screen Capture Source
├── ScreenGrabber.exe            # Compiled Native Windows Desktop Grabber
├── Start_Antigravity_Bot.vbs    # Double-click silent launcher script
├── Start_Antigravity_Bot.bat    # Double-click batch launcher script
├── tests_and_tools/             # Clean subfolder containing 115+ test & debug scripts
├── antigravity_bot_architecture.md # Full Architecture & Technical Specification
└── .gitignore                   # Keeps API Keys, Tokens, Logs, and Temp Files Safe
```

---

## 📖 Step-by-Step Setup Guide

### 1️⃣ Step 1: Create a Telegram Bot via `@BotFather`
1. Open Telegram and search for `@BotFather`.
2. Send the command `/newbot`.
3. Enter a display name and username ending in `bot` (e.g. `MyAntigravityPC_bot`).
4. Copy the **HTTP API Access Token**.

### 2️⃣ Step 2: Get Your Numeric Telegram User ID via `@userinfobot`
1. Search for `@userinfobot` on Telegram.
2. Send `/start`.
3. Copy your numeric User ID (e.g., `991501277`).

### 3️⃣ Step 3: Clone Repository & Configure Settings
```bash
git clone https://github.com/triwahyu45/Antigravity_TelegramBot.git
cd Antigravity_TelegramBot
cp config.example.json secrets.json
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

## ☕ Support & Donation

If this project has been helpful to you, consider supporting the development! Your support is greatly appreciated:

[![Saweria](https://img.shields.io/badge/Donate-Saweria-red.svg?style=for-the-badge&logo=saweria)](https://saweria.co/triwahyu45)
[![Trakteer](https://img.shields.io/badge/Donate-Trakteer-red.svg?style=for-the-badge&logo=trakteer)](https://trakteer.id/triwahyu45)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/triwahyu45)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue.svg?style=for-the-badge&logo=paypal)](https://paypal.me/triwahyu45)

- 🇮🇩 **Saweria**: [saweria.co/triwahyu45](https://saweria.co/triwahyu45)
- 🇮🇩 **Trakteer**: [trakteer.id/triwahyu45](https://trakteer.id/triwahyu45)
- 🌐 **Buy Me a Coffee**: [buymeacoffee.com/triwahyu45](https://buymeacoffee.com/triwahyu45)
- 🌐 **PayPal**: [paypal.me/triwahyu45](https://paypal.me/triwahyu45)

---

## 👤 Author & Maintainer
Created with ❤️ by **[TriWahyu45](https://github.com/triwahyu45)**  
Repository: **[github.com/triwahyu45/Antigravity_TelegramBot](https://github.com/triwahyu45/Antigravity_TelegramBot)**

---

## 📜 License
Licensed under the [MIT License](LICENSE).
