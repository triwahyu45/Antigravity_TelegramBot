# 🚀 Google Antigravity Telegram Bridge & Remote Control System
> **Technical Specification & System Architecture Specification**

---

## 📌 Executive Summary

The **Google Antigravity Telegram Bridge** is a production-grade, real-time, asynchronous remote control interface connecting Telegram mobile/desktop clients directly to Google Antigravity Agent running on Windows PC.

It enables natural multi-modal bidirectional communication (Text, Photos, Videos, Voice Notes, Audio, Documents), instant prompt injection via Chromium DevTools Protocol (CDP) WebSocket native hardware key events, real-time DOM mirror synchronization, and 100% silent background execution without taskbar icons (`SW_HIDE`).

---

## 🏗️ Architecture & Component Flow

```
                                  +---------------------------------------+
                                  |         Telegram Mobile App           |
                                  +-------------------+-------------------+
                                                      | (Poll / Webhook)
                                                      v
                                  +-------------------+-------------------+
                                  |        AGY_Bot_Receiver (PID A)       |
                                  |   (telegram_bot.py - Multi-Threaded)  |
                                  +---------+-------------------+---------+
                                            |                   |
            +-------------------------------+                   +-------------------------------+
            |                                                                                   |
            v                                                                                   v
+-----------+-----------------------+                                       +-------------------+-------------------+
|  CDP Injector Engine              |                                       |  Physical & CDP Screen Grabber    |
|  (antigravity_injector.py)        |                                       |  (ScreenGrabber.exe & CDP SS)     |
+-----------+-----------------------+                                       +-------------------+-------------------+
            | (Native Hardware Enter)                                                           |
            v                                                                                   |
+-----------+-----------------------+                                                           |
|  Google Antigravity Desktop App   | <---------------------------------------------------------+
|  (Chromium V8 DOM Engine)         |
+-----------+-----------------------+
            | (Real-time DOM Watcher)
            v
+-----------+-----------------------+
|  AGY_Bot_Mirror (PID B)           |
|  (dom_mirror_final.py)            |
+-----------+-----------------------+
            | (Markdown/HTML Filter)
            v
+-----------+-----------------------+
|  Telegram Client Notification     |
+-----------------------------------+
```

---

## 🌟 Core System Modules

### 1. `telegram_bot.py` (Bot Engine & Listener)
- **Role**: Primary polling engine for Telegram incoming messages, commands, and media files.
- **Key Features**:
  - **Multi-threaded Queue Worker**: Offloads prompt injection to background daemon threads to maintain sub-millisecond responsiveness.
  - **Natural Multi-Media Handling**: Receives photos, videos, voice notes, audio, and documents, saving them to `G:\Antigravity_Server\Received_Files\` and embedding their context into Antigravity prompt stream.
  - **Natural Telegram Reply Context**: Parses quoted messages (`[Membalas: "..."]`) so AI always maintains exact conversation thread awareness.
  - **`SW_HIDE (0)` Background Manager**: Minimizes and hides the Antigravity desktop window completely from both the screen and the Windows taskbar.
  - **Live Timestamp Captions**: Appends real-time `HH:MM:SS WIB` timestamp to photo captions to prevent Telegram client image caching.

### 2. `antigravity_injector.py` (CDP WebSocket Injection Engine)
- **Role**: Dispatches prompts directly into Lexical React editor inside Antigravity's Chromium V8 DOM.
- **Key Features**:
  - **Dynamic CDP Port Discovery**: Scans local Chrome debugging ports (`127.0.0.1:<port>`) with 30s TTL caching.
  - **Native Keyboard Event Fallback (`cdp_send_native_enter`)**: Uses CDP WebSocket `Input.dispatchKeyEvent` to send hardware Enter key events (`windowsVirtualKeyCode=13`, `code="Enter"`). Works 100% whether the Antigravity agent is IDLE or actively WORKING.

### 3. `dom_mirror_final.py` (Real-time DOM Response & Progress Mirror)
- **Role**: Monitors Antigravity Chromium DOM for AI response blocks, tool badges, code edits, and terminal output.
- **Key Features**:
  - **Progress Badge Formatter**: Formats `Edited`, `Ran command`, `Searched`, `Created` activity badges using Markdown (`✏️ *Editing...*`, `💻 *Ran...*`) for clean Telegram HTML rendering.
  - **Original Quality Image Extraction**: Extracts images generated by AI and forwards them to Telegram as original uncompressed documents.
  - **Async Output Queue**: Uses non-blocking Telegram send worker thread to prevent DOM scrape loop latency.

### 4. `ScreenGrabber.cs` & `ScreenGrabber.exe` (Native Monitor Screen Grabber)
- **Role**: C# Win32 standalone screen grabber compiled via native Windows `csc.exe`.
- **Key Features**:
  - Captures true physical PC monitor screen (Steam, Browser, VS Code, Desktop) using Win32 `Graphics.CopyFromScreen` with DPI awareness.
  - Falls back to Chromium CDP screenshot engine if the monitor display is locked/disconnected.

---

## 🔒 Security & Public GitHub Guidelines

1. **Never Commit Secrets**:
   - `config.py`, `.env`, API keys, and Telegram Bot Tokens are strictly listed in `.gitignore`.
   - Use `config.example.py` for public GitHub repositories.
2. **Path Sanitization**:
   - Sensitive folder paths and user paths must be configurable via environment variables or `config.py`.
3. **Authorized User Filter**:
   - Strict chat ID whitelist filtering (`auth(msg)`) prevents unauthorized Telegram users from interacting with the bot.

---

## 🛠️ Installation & Setup Guide

1. Clone repository to your project directory.
2. Copy `config.example.py` to `config.py` and set your credentials:
   ```python
   TELEGRAM_BOT_TOKEN = "your_bot_token_here"
   ALLOWED_TELEGRAM_ID = 123456789
   ```
3. Compile `ScreenGrabber.cs` (if needed):
   ```cmd
   C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:exe /out:ScreenGrabber.exe ScreenGrabber.cs
   ```
4. Start Bot & Mirror Services:
   ```cmd
   python telegram_bot.py
   python dom_mirror_final.py
   ```

---
*Built with ❤️ for Google Antigravity Agent Remote Automation.*
