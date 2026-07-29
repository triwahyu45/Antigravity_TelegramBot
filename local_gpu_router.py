"""
Google Antigravity Telegram Remote Control Bridge
Smart Hybrid Intent Router & Local GPU Ollama Fallback Engine

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import urllib.request
import json
import re

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"

# Keywords that indicate a complex coding / agent file editing task
CODING_KEYWORDS = [
    'buat', 'bikin', 'create', 'edit', 'fix', 'bug', 'code', 'koding', 'script',
    'python', 'javascript', 'html', 'css', 'git', 'commit', 'push', 'pull',
    'terminal', 'cmd', 'powershell', 'install', 'setup', 'build', 'run', 'exec',
    'file', 'folder', 'directory', 'repo', 'repository', 'github', 'bot', 'server',
    'antigravity', 'cdp', 'ss', 'screenshot', 'status', 'minimize', 'buka', 'sembunyikan'
]

def is_ollama_active():
    """Checks if Ollama Local GPU server is active on port 11434"""
    try:
        req = urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=1.5)
        if req.status == 200:
            data = json.loads(req.read().decode())
            models = data.get('models', [])
            return len(models) > 0, models
    except Exception:
        pass
    return False, []

def is_casual_chat(prompt_text):
    """Classifies if a prompt is a simple casual chat vs a complex coding task"""
    if not prompt_text: return False
    txt = prompt_text.lower().strip()
    
    # If prompt contains explicit coding keywords -> Complex task
    for kw in CODING_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', txt):
            return False
            
    # If short greeting or casual question -> Casual chat
    if len(txt) < 80:
        return True
        
    return False

def query_local_gpu_ollama(prompt_text, model_name="qwen2:1.5b"):
    """Queries the local PC GPU Ollama server for casual chat (0 API Tokens)"""
    try:
        active, models = is_ollama_active()
        if not active: return None
        
        # Pick installed model name if available
        if models:
            model_name = models[0].get('name', model_name)
            
        payload = json.dumps({
            "model": model_name,
            "prompt": f"Jawab dengan ramah, jelas, dan singkat dalam Bahasa Indonesia:\n{prompt_text}",
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode())
            reply = data.get("response", "").strip()
            if reply:
                return f"{reply}\n\n⚡ _(Dijawab oleh GPU PC Lokal - 0 Token API)_"


    except Exception as e:
        print("[LOCAL GPU ROUTER ERR]", e)
    return None
