# 🚀 Google Antigravity Telegram Bot & Remote Control Bridge

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

An advanced, asynchronous, multi-modal Telegram Bot bridge to remotely monitor, control, and interact with **Google Antigravity AI Agent** on Windows PC.

---

## ✨ Features

- ⚡ **Seamless Prompt Injection**: Uses Chromium DevTools Protocol (CDP) WebSocket native hardware key events (`Input.dispatchKeyEvent`) to queue/submit prompts 100% reliably whether the agent is IDLE or WORKING.
- 💬 **Natural Conversation & Media Support**: Full support for Telegram quoter replies (`[Membalas: "..."]`), Photos, Videos, Voice Notes, Audio files, and Documents.
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
├── config.example.py            # Configuration Template (Copy to config.py)
├── antigravity_bot_architecture.md # Full Architecture & Technical Specification
└── .gitignore                   # Keeps API Keys, Tokens, Logs, and Temp Files Safe
```

---

## 🚀 Quick Start Guide

### 1. Prerequisite
- Windows 10/11
- Python 3.10+
- Installed Google Antigravity Desktop App

### 2. Installation
```bash
git clone https://github.com/YourUsername/antigravity-telegram-bot.git
cd antigravity-telegram-bot
pip install -r requirements.txt
```

### 3. Configuration
Copy `config.example.py` to `config.py`:
```bash
cp config.example.py config.py
```
Edit `config.py` and set your Bot Token and Telegram User ID:
```python
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ALLOWED_TELEGRAM_ID = 123456789
```

### 4. Compile ScreenGrabber (Optional)
If `ScreenGrabber.exe` is missing, compile it with the native Windows C# compiler:
```cmd
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:exe /out:ScreenGrabber.exe ScreenGrabber.cs
```

### 5. Running the Bot
```bash
python telegram_bot.py
```
In a second terminal, launch the DOM mirror:
```bash
python dom_mirror_final.py
```

---

## 🛡️ Security Note

- **Secrets Protection**: `config.py`, `.env`, Telegram Bot Tokens, personal chat IDs, screenshot images, and logs are excluded via `.gitignore` to ensure **100% public safety**.
- **User Authorization**: All incoming commands are strictly checked against `ALLOWED_TELEGRAM_ID`.

---

## 📜 License
Licensed under the [MIT License](LICENSE).
