"""
Watcher HP → Antigravity
Tunggu pesan baru dari HP Telegram, lalu exit dengan output pesan.
AI akan restart watcher ini setiap kali selesai (chain pattern).
- Kalau ada pesan: print dan exit -> AI dapat notifikasi, baca & balas
- Kalau timeout 50 detik tidak ada pesan: exit normal -> AI restart lagi
"""
import os, json, time, sys

INBOX_NOTIFY   = r"G:\Antigravity_Server\inbox_notify.txt"
WATCHER_OFFSET = r"G:\Antigravity_Server\watcher_offset.txt"
MAX_WAIT       = 50  # detik, lalu restart

def get_offset():
    if os.path.exists(WATCHER_OFFSET):
        try:
            return int(open(WATCHER_OFFSET).read().strip())
        except:
            pass
    # Mulai dari ujung file saat ini
    if os.path.exists(INBOX_NOTIFY):
        try:
            n = len(open(INBOX_NOTIFY, encoding="utf-8").readlines())
            open(WATCHER_OFFSET, "w").write(str(n))
            return n
        except:
            pass
    return 0

def save_offset(n):
    open(WATCHER_OFFSET, "w").write(str(n))

offset = get_offset()
start  = time.time()

while time.time() - start < MAX_WAIT:
    try:
        if os.path.exists(INBOX_NOTIFY):
            lines = open(INBOX_NOTIFY, encoding="utf-8").readlines()
            if len(lines) > offset:
                new_msgs = []
                for raw in lines[offset:]:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        d = json.loads(raw)
                        text = d.get("text", "")
                        if text:
                            new_msgs.append(text)
                    except:
                        pass
                save_offset(len(lines))
                if new_msgs:
                    for m in new_msgs:
                        print(f"[HP_MSG] {m}", flush=True)
                    sys.exit(0)  # exit -> AI dapat notifikasi segera
    except Exception as e:
        print(f"[ERR] {e}", flush=True)
    time.sleep(0.5)

# Timeout, tidak ada pesan — exit normal, AI restart
sys.exit(0)
