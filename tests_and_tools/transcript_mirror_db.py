"""
Node 2 v2: DB-based Transcript Mirror
Membaca langsung dari SQLite conversation database Antigravity
karena transcript.jsonl sudah tidak diupdate setelah CHECKPOINT.
"""
import os, sys, time, json, re, sqlite3, telebot

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except: pass

from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
BASE       = r"G:\Antigravity_Server"
DB_PATH    = r"C:\Users\Triwahyu45\.gemini\antigravity\conversations\2f289acc-06bd-4e56-b2d3-964240c95268.db"
OFFSET_FILE = os.path.join(BASE, "db_mirror_last_id.txt")

bot = telebot.TeleBot(BOT_TOKEN)

def get_last_id():
    if os.path.exists(OFFSET_FILE):
        try: return int(open(OFFSET_FILE).read().strip())
        except: pass
    return 0

def save_last_id(n):
    try: open(OFFSET_FILE, "w").write(str(n))
    except: pass

def format_for_telegram(text):
    if not text: return ""
    t = str(text)
    t = re.sub(r'\*\*(.*?)\*\*', r'*\1*', t)
    t = re.sub(r'^#{1,6}\s*(.+)$', r'*\1*', t, flags=re.MULTILINE)
    t = re.sub(r'^\s*[\-\*]\s+', r'• ', t, flags=re.MULTILINE)
    return t.strip()

def send_to_tg(text, prefix=""):
    if not text or not text.strip(): return
    full = (prefix + "\n" + text) if prefix else text
    formatted = format_for_telegram(full)
    chunks = []
    curr = ""
    for line in formatted.splitlines():
        if len(curr) + len(line) + 1 > 3500:
            if curr: chunks.append(curr)
            curr = line
        else:
            curr = (curr + "\n" + line) if curr else line
    if curr: chunks.append(curr)

    for chunk in chunks:
        try:
            bot.send_message(ALLOWED_ID, chunk, parse_mode="Markdown")
        except Exception:
            try:
                plain = re.sub(r'[\*\_\`#]', '', chunk)
                bot.send_message(ALLOWED_ID, plain, parse_mode=None)
            except Exception as e:
                print("[SEND ERR]", e)

def mirror_worker():
    last_id = get_last_id()
    print("[DB MIRROR] Started. Last ID:", last_id)

    while True:
        try:
            if not os.path.exists(DB_PATH):
                print("[DB MIRROR] DB not found:", DB_PATH)
                time.sleep(5)
                continue

            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=2)
            cur = conn.cursor()

            # Cari tabel yang ada
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]

            # Cari tabel messages / turns / steps
            msg_table = None
            for t in tables:
                if any(k in t.lower() for k in ['message', 'turn', 'step', 'event']):
                    msg_table = t
                    break

            if not msg_table:
                # Fallback: list semua kolom tabel pertama
                if tables:
                    print("[DB MIRROR] Tables:", tables)
                    cur.execute(f"PRAGMA table_info({tables[0]})")
                    cols = cur.fetchall()
                    print("[DB MIRROR] Cols of", tables[0], ":", [c[1] for c in cols])
                conn.close()
                time.sleep(5)
                continue

            # Ambil rows baru setelah last_id
            cur.execute(f"SELECT * FROM {msg_table} WHERE rowid > ? ORDER BY rowid ASC LIMIT 50", (last_id,))
            rows = cur.fetchall()
            cur.execute(f"PRAGMA table_info({msg_table})")
            col_names = [c[1] for c in cur.fetchall()]
            conn.close()

            for row in rows:
                rowid = row[0] if rows else 0
                d = dict(zip(col_names, row))

                typ = str(d.get('type', d.get('role', d.get('source', '')))).upper()
                content = str(d.get('content', d.get('text', d.get('body', '')))).strip()
                status = str(d.get('status', 'DONE')).upper()

                # Mirror user messages dari PC
                if 'USER' in typ and content and len(content) > 2:
                    for tag in ['<USER_REQUEST>', '</USER_REQUEST>', '<ADDITIONAL_METADATA>', '</ADDITIONAL_METADATA>']:
                        content = content.replace(tag, '')
                    clean = '\n'.join(
                        l for l in content.splitlines()
                        if not l.strip().startswith('The current local time') and l.strip()
                    ).strip()
                    if clean and not any(k in clean.lower() for k in ['foto baru dari telegram', 'received_files']):
                        send_to_tg(clean, "You (PC):")

                # Mirror AI responses
                elif ('MODEL' in typ or 'PLANNER' in typ or 'ASSISTANT' in typ) and content and len(content) > 5:
                    if status in ('DONE', ''):
                        send_to_tg(content, "Antigravity:")

                last_id = d.get('rowid', last_id) or last_id
                save_last_id(last_id)

        except Exception as e:
            print("[DB MIRROR ERR]", e)
        time.sleep(2)

if __name__ == "__main__":
    mirror_worker()
