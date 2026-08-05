"""
Google Antigravity Telegram Remote Control Bridge
Secrets & Configuration Loader Module

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os, json

BASE_DIR = r"G:\Antigravity_Server"
SECRETS_PATH = os.path.join(BASE_DIR, "Bot_Scripts", "secrets.json")

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ALLOWED_ID = 0
TARGET_CHAT_TITLE = "Wahyu's PC"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ANTIGRAVITY_PATH = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"
AUTO_SCREENSHOT = True
DUP_TIMEOUT = 300

if os.path.exists(SECRETS_PATH):
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            BOT_TOKEN = data.get("BOT_TOKEN", BOT_TOKEN)
            ALLOWED_ID = int(data.get("ALLOWED_ID", ALLOWED_ID))
            TARGET_CHAT_TITLE = data.get("TARGET_CHAT_TITLE", TARGET_CHAT_TITLE)
            CHROME_PATH = data.get("CHROME_PATH", CHROME_PATH)
            ANTIGRAVITY_PATH = data.get("ANTIGRAVITY_PATH", ANTIGRAVITY_PATH)
            AUTO_SCREENSHOT = bool(data.get("AUTO_SCREENSHOT", AUTO_SCREENSHOT))
            DUP_TIMEOUT = int(data.get("DUP_TIMEOUT", DUP_TIMEOUT))
    except Exception as e:
        print(f"[CONFIG LOAD ERR] {e}")

# Environment Variable Overrides
if "BOT_TOKEN" in os.environ: BOT_TOKEN = os.environ["BOT_TOKEN"]
if "ALLOWED_ID" in os.environ: ALLOWED_ID = int(os.environ["ALLOWED_ID"])
