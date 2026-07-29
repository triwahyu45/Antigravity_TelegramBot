"""
Google Antigravity Telegram Remote Control Bridge
Natural Indonesian & English Text-to-Speech (TTS) Voice Synthesizer Module

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os
import re
import time
import html
from gtts import gTTS

BASE_DIR = r"G:\Antigravity_Server"
SHOTS_DIR = os.path.join(BASE_DIR, "Screenshots")

def clean_text_for_speech(text):
    if not text: return ""
    # Strip HTML tags, markdown symbols, code blocks, URLs
    t = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    t = re.sub(r'`.*?`', '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'[*#_~`-]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > 280:
        t = t[:280] + "..."
    return t

def generate_voice_note(text, lang='id'):
    """Generates an .ogg voice note file for Telegram from text"""
    try:
        speech_text = clean_text_for_speech(text)
        if not speech_text or len(speech_text) < 3:
            return None
            
        out_path = os.path.join(SHOTS_DIR, f"voice_note_{int(time.time())}.ogg")
        tts = gTTS(text=speech_text, lang=lang, slow=False)
        tts.save(out_path)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            return out_path
    except Exception as e:
        print("[VOICE SYNTH ERR]", e)
    return None
