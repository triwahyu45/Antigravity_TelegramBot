# 📋 CHANGELOG - Google Antigravity Telegram Bot

All notable changes to this project will be documented in this file.

---

## 🚀 [v1.0.0] - 2026-07-29 (Production Clean Release)

### ✨ Core Features
- **Multi-Threaded Asynchronous Queue Worker**: Offloads prompt injection to background daemon threads to guarantee sub-millisecond polling response.
- **CDP WebSocket Prompt Injector (`antigravity_injector.py`)**: Uses native Chrome DevTools Protocol (`Input.dispatchKeyEvent` with `windowsVirtualKeyCode=13`, `code="Enter"`) to submit prompts 100% reliably whether the agent is IDLE or WORKING.
- **Physical PC Screen Capture (`ScreenGrabber.cs` / `ScreenGrabber.exe`)**: Native C# monitor grabber capturing actual physical screen contents (Steam, Browser, Desktop, Apps).
- **High-Resolution CDP Render Engine (`cdp_capture_screenshot`)**: Directly renders Chromium GPU memory canvas (111 KB HD).
- **Real-Time DOM Response Mirror (`dom_mirror_final.py`)**: Scrapes Chromium DOM for AI text blocks, progress badges (`Edited`, `Ran`, `Searched`, `Created`), and uncompressed image artifacts, converting Markdown to Telegram-compliant HTML.
- **Natural Conversation & Media Support**: Full support for Telegram quoter replies (`[Membalas: "..."]`), Photos, Videos, Voice Notes, Audio, and Documents.
- **100% Silent Background Mode (`SW_HIDE 0`)**: Completely hides Antigravity window from desktop and taskbar without stopping Chromium V8 event loops.
- **Auto-Relaunch Watcher**: Automatically re-launches Antigravity in `SW_HIDE (0)` mode if closed unexpectedly.

### 🛡️ Security & Secret Safeguards
- **Isolated Credential Architecture**: Extracted all sensitive tokens and chat IDs into `secrets.json` and loaded dynamically via `secrets_loader.py`.
- **Git Security Protection**: Added `secrets.json`, `.env`, `config.py`, logs, temp files, and media directories to `.gitignore`.
- **Public Template**: Added `secrets.example.json` and `config.example.py` for public GitHub repository safety.
- **History Purged**: Cleared all previous commit history containing legacy token strings and squashed into clean root release commit (`053802e`).

---
*Maintained by Tri Wahyu & Antigravity Pair Programming AI.*
