"""
Google Antigravity Telegram Remote Control Bridge
Dynamic Secret Loader Module

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os, json


SECRETS_FILE = os.path.join(os.path.dirname(__file__), "secrets.json")

def load_secrets():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    allowed_id = os.getenv("ALLOWED_TELEGRAM_ID")
    
    if os.path.exists(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                token = token or data.get("BOT_TOKEN")
                allowed_id = allowed_id or data.get("ALLOWED_ID")
        except Exception: pass
        
    token = token or "YOUR_BOT_TOKEN_HERE"
    allowed_id = int(allowed_id) if allowed_id else 0
    return token, allowed_id

BOT_TOKEN, ALLOWED_ID = load_secrets()
