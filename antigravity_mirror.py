"""
Antigravity Mirror - Memantau transcript sesi ini dan menulis ke bridge_outbox.jsonl
Jalankan ini TERPISAH dari bot. Script ini yang "membaca" obrolan Antigravity
dan mengirim ke Telegram lewat file bridge.
"""
import os
import json
import time

TRANSCRIPT_PATH = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\.system_generated\logs\transcript.jsonl"
BRIDGE_FILE = r"G:\Antigravity_Server\bridge_outbox.jsonl"
OFFSET_FILE = r"G:\Antigravity_Server\mirror_offset.txt"

def get_offset():
    if os.path.exists(OFFSET_FILE):
        try:
            return int(open(OFFSET_FILE).read().strip())
        except Exception:
            pass
    # Start dari akhir file sekarang (tidak replay history)
    if os.path.exists(TRANSCRIPT_PATH):
        try:
            with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="ignore") as f:
                offset = len(f.readlines())
            save_offset(offset)
            return offset
        except Exception:
            pass
    return 0

def save_offset(n):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(n))

def write_bridge(text):
    entry = json.dumps({"text": text, "ts": time.time()}, ensure_ascii=False)
    with open(BRIDGE_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def monitor():
    offset = get_offset()
    print(f"Mirror dimulai dari baris transcript #{offset}")
    
    while True:
        try:
            if not os.path.exists(TRANSCRIPT_PATH):
                time.sleep(2)
                continue
            with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            if len(lines) > offset:
                new_lines = lines[offset:]
                offset = len(lines)
                save_offset(offset)
                
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        # Hanya kirim balasan AI (PLANNER_RESPONSE yang sudah DONE)
                        if (data.get("type") == "PLANNER_RESPONSE" 
                                and data.get("status") == "DONE"
                                and data.get("content")):
                            content = data["content"].strip()
                            # Filter pesan system/internal
                            if (content 
                                    and not content.startswith("[Message]")
                                    and len(content) > 5):
                                write_bridge(f"🤖 *[Antigravity]*:\n{content}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    monitor()
