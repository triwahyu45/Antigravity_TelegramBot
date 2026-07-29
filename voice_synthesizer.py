"""
Google Antigravity Telegram Remote Control Bridge
Natural Indonesian & English Fast Text-to-Speech (TTS) Voice Synthesizer Module

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os
import re
import time
import subprocess
from gtts import gTTS

BASE_DIR = r"G:\Antigravity_Server"
SHOTS_DIR = os.path.join(BASE_DIR, "Screenshots")

def clean_text_for_speech(text):
    if not text: return ""
    t = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    t = re.sub(r'`.*?`', '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'[*#_~`-]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > 280:
        t = t[:280] + "..."
    return t

def generate_voice_note(text, lang='id', speed=1.35):
    """Generates a fast (1.35x speed) natural .ogg voice note file for Telegram"""
    try:
        speech_text = clean_text_for_speech(text)
        if not speech_text or len(speech_text) < 3:
            return None
            
        raw_path = os.path.join(SHOTS_DIR, f"voice_raw_{int(time.time())}.ogg")
        fast_path = os.path.join(SHOTS_DIR, f"voice_note_{int(time.time())}.ogg")
        
        tts = gTTS(text=speech_text, lang=lang, slow=False)
        tts.save(raw_path)
        
        if os.path.exists(raw_path):
            # Speed up audio naturally by 35% without changing pitch using ffmpeg atempo
            cmd = ["ffmpeg", "-y", "-i", raw_path, "-filter:a", f"atempo={speed}", "-c:a", "libvorbis", fast_path]
            subprocess.run(cmd, capture_output=True, text=True)
            
            try: os.remove(raw_path)
            except: pass
            
            if os.path.exists(fast_path) and os.path.getsize(fast_path) > 1000:
                return fast_path
            return raw_path
    except Exception as e:
        print("[VOICE SYNTH ERR]", e)
    return None
