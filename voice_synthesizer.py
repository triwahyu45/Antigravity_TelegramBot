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

def clean_text_for_speech(text, max_len=1200):
    if not text: return ""
    
    # 1. Strip markdown code blocks, inline code, HTML tags, URLs
    t = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    t = re.sub(r'`.*?`', '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'http\S+', '', t)
    
    # 2. Clean markdown bold, italic, strikethrough, quote formatting preserving words
    t = re.sub(r'\*+(.*?)\*+', r'\1', t)
    t = re.sub(r'_(.*?)_', r'\1', t)
    t = re.sub(r'~(.*?)~', r'\1', t)
    
    # 3. Normalize version numbers (v1.3.0 -> versi 1.3)
    t = re.sub(r'\bv(\d+)\.(\d+)(?:\.(\d+))?\b', r'versi \1 titik \2', t, flags=re.IGNORECASE)
    
    # 4. Remove list bullet symbols (*, -, #, •) at start of lines
    t = re.sub(r'^[*\-#•]+\s*', '', t, flags=re.MULTILINE)
    
    # 5. Indonesian Phonetic Dictionary for English Tech Words (Prevents Robotic/Spelled Pronunciation)
    phonetic_map = {
        r'\bGoogle\b': 'Gugel',
        r'\bAntigravity\b': 'Antigraviti',
        r'\bBackground\b': 'Bekglen',
        r'\bRelease\b': 'Rilis',
        r'\bScript\b': 'Skrip',
        r'\bFeatures?\b': 'Fitur',
        r'\bRepository\b': 'Repositori',
        r'\bPython\b': 'Paiton',
        r'\bGitHub\b': 'Git Hab',
        r'\bProcess\b': 'Proses',
        r'\bQueue\b': 'Kyu',
        r'\bInject(?:or)?\b': 'Injeksi',
        r'\bScraper\b': 'Skraper',
        r'\bSynthesizer\b': 'Sintesis',
        r'\bBridge\b': 'Jembatan',
        r'\bServer\b': 'Server',
        r'\bSystem\b': 'Sistem',
        r'\bTray\b': 'Trei',
        r'\bShortcut\b': 'Shortkut',
        r'\bDesktop\b': 'Desktop',
        r'\bMode\b': 'Modus',
        r'\bSingle\b': 'Singgel',
        r'\bInstance\b': 'Instan',
        r'\bLock\b': 'Lok'
    }
    
    for pattern, replacement in phonetic_map.items():
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)
        
    # 6. Replace remaining non-alphanumeric special characters with a single space
    t = re.sub(r'[^a-zA-Z0-9\s.,!?]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    
    if len(t) > max_len:
        cut_text = t[:max_len]
        last_period = max(cut_text.rfind('.'), cut_text.rfind('!'), cut_text.rfind('?'))
        if last_period > max_len // 2:
            cut_text = cut_text[:last_period+1]
        t = cut_text.strip()
    return t

def generate_voice_note(text, lang='id', speed=1.35):
    """Generates a fast (1.35x speed) natural .ogg voice note file for Telegram"""
    try:
        speech_text = clean_text_for_speech(text, max_len=1200)
        if not speech_text or len(speech_text) < 3:
            return None
            
        raw_path = os.path.join(SHOTS_DIR, f"voice_raw_{int(time.time())}.ogg")
        fast_path = os.path.join(SHOTS_DIR, f"voice_note_{int(time.time())}.ogg")
        
        tts = gTTS(text=speech_text, lang=lang, slow=False)
        tts.save(raw_path)
        
        if os.path.exists(raw_path):
            # Speed up audio naturally by 35% without changing pitch using ffmpeg atempo
            cmd = ["ffmpeg", "-y", "-i", raw_path, "-filter:a", f"atempo={speed}", "-c:a", "libvorbis", fast_path]
            subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000)

            try: os.remove(raw_path)
            except: pass
            
            if os.path.exists(fast_path) and os.path.getsize(fast_path) > 1000:
                return fast_path
            return raw_path
    except Exception as e:
        print("[VOICE SYNTH ERR]", e)
    return None
