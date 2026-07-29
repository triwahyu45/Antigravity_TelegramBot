import os
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

BASE_DIR = r"G:\Antigravity_Server"
MEMORY_FILE = os.path.join(BASE_DIR, "ecc_memory.json")

DEFAULT_MEMORY = {
    "system": "Antigravity Agent Harness (ECC Architecture)",
    "version": "1.0",
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "user_preferences": {
        "preferred_disk": "G:\\",
        "bot_style": "Fast non-blocking, zero-delay, direct quote reply",
        "output_format": "Markdown & Original Quality Documents",
        "custom_rules": [
            "Prioritas Lokasi Pencarian File: Disk G (G:\\)",
            "Kirim pesan Telegram HP selalu balaskan langsung ke prompt ID",
            "Hindari artificial sleep delay, utamakan non-blocking execution"
        ]
    },
    "learned_instructions": [],
    "project_history": [
        {"project": "Wahyu's Plan", "path": "G:\\Github TriWahyu45\\Wahyus-Plan", "url": "https://triwahyu45.github.io/Wahyus-Plan/"},
        {"project": "Gamepad Piano", "path": "G:\\Github TriWahyu45\\GamepadPiano", "url": "https://triwahyu45.github.io/GamepadPiano/"}
    ],
    "subagents": {
        "architect": "System Architecture & Plan Creator",
        "tester": "Automated Unit Test & TDD Specialist",
        "security": "Security & Code Auditor",
        "bug_hunter": "Deep Traceback Debugger & Bug Fixer",
        "ui_ux": "Modern Web Design & CSS Specialist"
    }
}

def get_memory():
    if not os.path.exists(MEMORY_FILE):
        save_memory(DEFAULT_MEMORY)
        return DEFAULT_MEMORY
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ECC MEMORY ERR] {e}")
        return DEFAULT_MEMORY

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ECC MEMORY SAVE ERR] {e}")
        return False

def add_learned_instruction(text):
    mem = get_memory()
    if text and text not in mem["learned_instructions"]:
        mem["learned_instructions"].append({
            "instruction": text,
            "added_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        save_memory(mem)
        return True
    return False

def get_memory_summary():
    mem = get_memory()
    summary = "🧠 *EVERYTHING CLAUDE CODE (ECC) MEMORY SUMMARY*\n\n"
    summary += f"• *Version*: {mem.get('version', '1.0')}\n"
    summary += f"• *Preferred Disk*: `{mem['user_preferences']['preferred_disk']}`\n"
    summary += f"• *Subagents Active*: {len(mem.get('subagents', {}))}\n"
    summary += f"• *Learned Rules*: {len(mem.get('learned_instructions', []))}\n"
    summary += f"• *Projects Registered*: {len(mem.get('project_history', []))}\n\n"
    
    summary += "*📌 Preferensi & Aturan Utama*:\n"
    for r in mem['user_preferences']['custom_rules']:
        summary += f"- {r}\n"
        
    if mem['learned_instructions']:
        summary += "\n*🎓 Instruksi Baru Ditambahkan*:\n"
        for item in mem['learned_instructions'][-5:]:
            summary += f"- {item['instruction']} _({item['added_at']})_\n"
            
    return summary

if __name__ == "__main__":
    mem = get_memory()
    print("ECC Memory Initialized Successfully!")
    print(get_memory_summary())
