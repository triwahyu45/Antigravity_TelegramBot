"""
Antigravity Telegram Daemon
Membaca pesan dari Telegram (via inbox file), memprosesnya dengan Antigravity SDK,
dan mengirim balasan kembali ke Telegram via bridge file.
"""
import os
import json
import time
import asyncio
import sys

INBOX_FILE = r"G:\Antigravity_Server\telegram_inbox.jsonl"
BRIDGE_FILE = r"G:\Antigravity_Server\bridge_outbox.jsonl"
PROCESSED_OFFSET_FILE = r"G:\Antigravity_Server\inbox_processed_offset.txt"

# Coba import Antigravity SDK
try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

def get_processed_offset():
    if os.path.exists(PROCESSED_OFFSET_FILE):
        try:
            return int(open(PROCESSED_OFFSET_FILE).read().strip())
        except Exception:
            pass
    return 0

def save_processed_offset(n):
    with open(PROCESSED_OFFSET_FILE, "w") as f:
        f.write(str(n))

def write_to_bridge(text):
    if not text or not text.strip():
        return
    entry = json.dumps({"text": text.strip(), "ts": time.time()}, ensure_ascii=False)
    with open(BRIDGE_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def read_new_inbox_messages():
    if not os.path.exists(INBOX_FILE):
        return []
    offset = get_processed_offset()
    try:
        with open(INBOX_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = lines[offset:]
        save_processed_offset(len(lines))
        messages = []
        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except Exception:
                pass
        return messages
    except Exception as e:
        print(f"Read inbox error: {e}")
        return []

async def process_with_sdk(prompt):
    """Proses pesan dengan Antigravity SDK"""
    config = LocalAgentConfig(
        system_instructions=(
            "Kamu adalah Antigravity AI assistant pribadi yang pintar, ramah, dan santai. "
            "Jawablah dalam Bahasa Indonesia yang natural dan kasual seperti percakapan sehari-hari. "
            "Kamu memiliki akses penuh ke sistem laptop ini."
        ),
        capabilities=CapabilitiesConfig()
    )
    full_response = ""
    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        async for token in response:
            full_response += token
    return full_response.strip()

def process_message_simple(text):
    """Fallback jika SDK tidak tersedia: jawab dengan info singkat"""
    return f"📨 Pesan diterima: '{text}'\n\nℹ️ AI SDK tidak tersedia saat ini. Gunakan perintah langsung seperti /status, /screenshot, /cmd, /git."

async def main_loop():
    print("Daemon started. Watching inbox...")
    write_to_bridge("🟢 *Antigravity AI Daemon aktif!*\nSekarang kamu bisa chat langsung dari Telegram dan balasannya akan dikirim ke sini.")
    
    while True:
        try:
            messages = read_new_inbox_messages()
            for msg in messages:
                text = msg.get("text", "").strip()
                if not text:
                    continue
                
                print(f"Processing: {text}")
                write_to_bridge(f"📨 *Pesan dari Telegram*: _{text}_\n\n⏳ Sedang diproses...")
                
                try:
                    if HAS_SDK:
                        response = await process_with_sdk(text)
                    else:
                        response = process_message_simple(text)
                    
                    write_to_bridge(f"🤖 *[Antigravity AI]*:\n{response}")
                except Exception as e:
                    write_to_bridge(f"❌ Error memproses: {e}")
        except Exception as e:
            print(f"Daemon loop error: {e}")
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main_loop())
