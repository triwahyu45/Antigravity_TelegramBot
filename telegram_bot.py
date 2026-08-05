"""
Google Antigravity Telegram Remote Control Bridge
Main Asynchronous Bot Engine & Dispatcher

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os
import sys

import json
import time
import base64
import struct
import socket
import urllib.request
import psutil
import hashlib
import re
import html
import queue
import threading
import ctypes
import subprocess
import telebot
from telebot import types
from urllib.parse import urlparse, unquote

from PIL import ImageGrab
from antigravity_injector import inject_text_to_antigravity, _get_cdp_port


if os.name == 'nt':
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

# ── Single Instance Lock (kills stale duplicate on startup) ────
_LOCK_FILE = r"G:\Antigravity_Server\telegram_bot.pid"
def ensure_singleton():
    try:
        if os.path.exists(_LOCK_FILE):
            old_pid = int(open(_LOCK_FILE).read().strip())
            if old_pid != os.getpid():
                try:
                    old_proc = psutil.Process(old_pid)
                    old_proc.kill()
                    time.sleep(0.5)
                    print(f"[SINGLETON] Killed stale instance PID {old_pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        open(_LOCK_FILE, 'w').write(str(os.getpid()))
    except Exception as _e:
        print(f"[SINGLETON ERR] {_e}")



def md_to_telegram_html(md_text):
    if not md_text: return ""

    code_blocks = []
    def code_block_sub(m):
        code_blocks.append(f"<pre>{html.escape(m.group(1).strip())}</pre>")
        return f"XCODEBLOCKX{len(code_blocks)-1}X"
    
    inline_codes = []
    def inline_code_sub(m):
        inline_codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"XINLINECODEX{len(inline_codes)-1}X"

    text = re.sub(r'```(?:[a-zA-Z]*\n)?(.*?)```', code_block_sub, md_text, flags=re.DOTALL)
    text = re.sub(r'`([^`\n]+)`', inline_code_sub, text)
    text = re.sub(r'^(?:#{1,6})\s+(.+)$', r'\1', text, flags=re.MULTILINE)

    protected_html = []
    def protect_tag(m):
        protected_html.append(m.group(0))
        return f"XTAGX{len(protected_html)-1}X"
    text = re.sub(r'</?(?:b|i|u|s|code|pre|a)[^>]*>', protect_tag, text)

    text = html.escape(text, quote=False)

    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*([^*]+)\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'~([^~]+)~', r'<s>\1</s>', text)
    
    text = re.sub(r'^\s*\*+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*\*+$', '', text, flags=re.MULTILINE)


    for i, tag in enumerate(protected_html):
        text = text.replace(f"XTAGX{i}X", tag)
    for i, ic in enumerate(inline_codes):
        text = text.replace(f"XINLINECODEX{i}X", ic)
    for i, cb in enumerate(code_blocks):
        text = text.replace(f"XCODEBLOCKX{i}X", cb)

    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()



from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
BASE            = r"G:\Antigravity_Server"
RECEIVED        = os.path.join(BASE, "Received_Files")
RECV_DIR        = RECEIVED
SHOTS           = os.path.join(BASE, "Screenshots")

for d in [BASE, RECEIVED, SHOTS]:
    os.makedirs(d, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=4)

# ── Message Queue System ─────────────────────────────────────
msg_queue = queue.Queue()

COMPARE_LOG_FILE      = os.path.join(BASE, "compare_activity.log")
INJECTED_PROMPTS_FILE = os.path.join(BASE, "injected_prompts.txt")
INJECTED_HASHES_FILE  = os.path.join(BASE, "injected_hashes.json")

def log_compare(msg_str):
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg_str}\n"
        with open(COMPARE_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

LAST_TG_MSG_FILE = os.path.join(BASE, "last_tg_user_msg_id.txt")

def save_last_user_msg_id(msg_id):
    try:
        with open(LAST_TG_MSG_FILE, "w", encoding="utf-8") as f:
            f.write(str(msg_id))
    except Exception: pass

def record_injected_prompt(p, raw_text=None):
    if not p: return
    try:
        p_clean = p.replace('\r\n', '\n').strip()
        h1 = hashlib.md5(p_clean.encode('utf-8', errors='replace')).hexdigest()
        
        # Save to text log
        with open(INJECTED_PROMPTS_FILE, "a", encoding="utf-8") as f:
            f.write(p_clean + "\n")
            if raw_text:
                raw_clean = raw_text.replace('\r\n', '\n').strip()
                if raw_clean != p_clean:
                    f.write(raw_clean + "\n")
            
        # Save hash set
        hashes = set()
        if os.path.exists(INJECTED_HASHES_FILE):
            try:
                hashes = set(json.load(open(INJECTED_HASHES_FILE, encoding='utf-8')))
            except: pass
            
        hashes.add(h1)
        hashes.add(hashlib.md5(p_clean[:50].encode('utf-8', errors='replace')).hexdigest())
        
        if raw_text:
            raw_clean = raw_text.replace('\r\n', '\n').strip()
            hashes.add(hashlib.md5(raw_clean.encode('utf-8', errors='replace')).hexdigest())
            hashes.add(hashlib.md5(raw_clean[:50].encode('utf-8', errors='replace')).hexdigest())

        json.dump(list(hashes)[-3000:], open(INJECTED_HASHES_FILE, 'w', encoding='utf-8'))
        log_compare(f"📥 [HP RECEIVED & SAVED HASH] Hash: {h1[:8]}... | Prompt: {p_clean[:60]}")
    except Exception as e:
        log_compare(f"❌ [RECORD ERR] {e}")

def is_antigravity_running():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                return True
        except Exception: pass
    return False

def _inject_worker(text, chat_id):
    """Dedicated inject thread - runs independently, never blocks queue_worker"""
    try:
        ok = inject_text_to_antigravity(text)
        if ok:
            log_activity(f"✅ INJECT OK: {text[:60]}")
            send(chat_id, "⚡ _Pesan masuk ke Antigravity!_", use_kb=False)
        else:
            log_activity(f"❌ INJECT FAILED: {text[:60]}")
            send(chat_id, "⚠️ _Gagal inject. Pastikan Antigravity terbuka._", use_kb=False)
    except Exception as e:
        log_activity(f"❌ INJECT ERR: {e} | text={text[:40]}")

def queue_worker():
    print("[QUEUE WORKER] Started - multi-thread seamless mode")
    while True:
        item = None
        try:
            item = msg_queue.get(timeout=30)
            if not item:
                msg_queue.task_done()
                continue

            text, chat_id = (item[0], item[1]) if len(item) >= 2 else (item[0], None)
            raw_text = item[2] if len(item) == 3 else text

            log_activity(f"📥 QUEUE PROCESSING: {text[:60]}")

            # Only check for extreme text overflow (>15k chars)
            if len(text) > 15000:
                log_activity(f"⚠️ SKIP text overflow ({len(text)} chars)")
                msg_queue.task_done()
                continue

            record_injected_prompt(text, raw_text=raw_text)

            # Auto-launch Antigravity jika tidak jalan
            if not is_antigravity_running():
                log_activity("[QUEUE WORKER] Antigravity tidak aktif - auto launching...")
                send(chat_id, "🚀 _Antigravity sedang tidak aktif. Menyalakan ulang..._", use_kb=False)
                ANTIGRAVITY_PATH = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"
                if os.path.exists(ANTIGRAVITY_PATH):
                    import subprocess
                    subprocess.Popen(f'"{ANTIGRAVITY_PATH}"', shell=True, creationflags=0x08000000)
                    for _ in range(12):
                        time.sleep(0.5)
                        if is_antigravity_running() and _get_cdp_port():
                            break

            # Fire inject di thread terpisah - queue_worker TIDAK PERNAH block
            t = threading.Thread(target=_inject_worker, args=(text, chat_id), daemon=True)
            t.start()

            msg_queue.task_done()


        except queue.Empty:
            continue
        except Exception as e:
            log_activity(f"[QUEUE WORKER ERR] {e}")
            try:
                if item is not None:
                    msg_queue.task_done()
            except: pass
            time.sleep(0.5)

t_queue = threading.Thread(target=queue_worker, daemon=True, name="QueueWorker")
# t_queue.start() dipindah ke bawah setelah log_activity didefinisikan


def sys_monitor_worker():
    """Background system monitor — alerts Telegram HP if CPU/RAM load remains >92% for 2 consecutive checks"""
    print("[SYS MONITOR] Started...")
    high_count = 0
    last_alert_time = 0
    while True:
        try:
            time.sleep(60)
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            if cpu > 92 or ram > 92:
                high_count += 1
                if high_count >= 2 and (time.time() - last_alert_time) > 900:
                    last_alert_time = time.time()
                    high_count = 0
                    msg = f"⚠️ *PERINGATAN SERVER LOAD TINGGI!*\n\n🖥️ *CPU Load:* {cpu}%\n🧠 *RAM Usage:* {ram}%\n\nServer berjalan dengan beban tinggi."
                    try:
                        bot.send_message(ALLOWED_ID, msg, parse_mode="Markdown")
                    except Exception: pass
            else:
                high_count = 0
        except Exception as e:
            print(f"[SYS MONITOR ERR] {e}")
            time.sleep(60)

t_sys_mon = threading.Thread(target=sys_monitor_worker, daemon=True, name="SysMonitorWorker")
t_sys_mon.start()

LOG_FILE = os.path.join(BASE, "bot_activity.log")

def log_activity(msg_str):
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg_str}\n"
        print(line, end="")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

# Start queue_worker SETELAH log_activity didefinisikan
t_queue.start()

processed_tg_msg_ids = set()

def auth(msg):
    uid = getattr(getattr(msg, 'from_user', None), 'id', None)
    if uid is None and hasattr(msg, 'chat'):
        uid = getattr(msg.chat, 'id', None)
    if uid != ALLOWED_ID:
        log_activity(f"⚠️ UNAUTHORIZED MSG from ID {uid}: {getattr(msg, 'text', '')}")
        return False
    return True


def is_dup_msg(msg):
    if hasattr(msg, 'message_id') and msg.message_id:
        if msg.message_id in processed_tg_msg_ids:
            print(f"[TG DUP SKIP] Dropped duplicate Telegram msg_id {msg.message_id}")
            return True
        processed_tg_msg_ids.add(msg.message_id)
        if len(processed_tg_msg_ids) > 2000:
            processed_tg_msg_ids.clear()
    return False

def kb():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📊 Status PC")
    btn2 = types.KeyboardButton("📸 Screenshot")
    btn3 = types.KeyboardButton("🖥️ Buka Antigravity")
    btn4 = types.KeyboardButton("🙈 Sembunyikan Antigravity")
    btn5 = types.KeyboardButton("🤖 Pilih Model AI")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    return markup


def send(chat_id, text, use_kb=True):
    try:
        target_markup = kb() if use_kb else None
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=target_markup)
    except Exception:
        try:
            bot.send_message(chat_id, text, parse_mode=None, reply_markup=target_markup)
        except Exception as e:
            print(f"[BOT SEND ERR] {e}")

def run_cmd(cmd, cwd=None):
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, errors="ignore",
            cwd=cwd or BASE, timeout=30, creationflags=CREATE_NO_WINDOW
        )
        out = (r.stdout or r.stderr or "Selesai tanpa output.").strip()
        return out[:3000]
    except subprocess.TimeoutExpired:
        return "⏰ Timeout 30 detik."
    except Exception as e:
        return f"Error: {e}"

def cdp_capture_screenshot():
    """Capture full high-resolution rendered UI of Antigravity via CDP Page.captureScreenshot"""
    port = _get_cdp_port()
    if not port: return None
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
        targets = json.loads(req.read())
        ws_url = next((t['webSocketDebuggerUrl'] for t in targets if t.get('type') == 'page'), None)
        if not ws_url: return None
        
        parsed = urlparse(ws_url)
        host = parsed.hostname; p_port = parsed.port; path = parsed.path
        
        s = socket.socket()
        s.connect((host, p_port))
        s.settimeout(6)
        key = base64.b64encode(os.urandom(16)).decode()
        req_str = f"GET {path} HTTP/1.1\r\nHost: {host}:{p_port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        s.sendall(req_str.encode())
        resp = b""
        while b"\r\n\r\n" not in resp: resp += s.recv(4096)
        
        p = json.dumps({"id": 100, "method": "Page.captureScreenshot", "params": {"format": "png"}}).encode()
        ln = len(p); mk = os.urandom(4)
        h = bytes([0x81, 0x80|(ln if ln<126 else 126)])
        if ln >= 126: h += struct.pack('>H', ln)
        h += mk
        s.sendall(h + bytes(b^mk[i%4] for i,b in enumerate(p)))

        buf = b""
        for _ in range(50):
            chunk = s.recv(65536)
            if not chunk: break
            buf += chunk
            
            while len(buf) >= 2:
                payload_len = buf[1] & 0x7F
                head_len = 2
                if payload_len == 126:
                    if len(buf) < 4: break
                    payload_len = struct.unpack('>H', buf[2:4])[0]
                    head_len = 4
                elif payload_len == 127:
                    if len(buf) < 10: break
                    payload_len = struct.unpack('>Q', buf[2:10])[0]
                    head_len = 10
                
                total_len = head_len + payload_len
                if len(buf) < total_len: break
                
                frame_data = buf[head_len:total_len]
                buf = buf[total_len:]
                
                try:
                    msg = json.loads(frame_data.decode('utf-8'))
                    if msg.get('id') == 100:
                        b64_data = msg.get('result', {}).get('data')
                        if b64_data:
                            img_bytes = base64.b64decode(b64_data)
                            out_path = os.path.join(SHOTS, f"screenshot_{int(time.time())}.png")
                            with open(out_path, "wb") as f:
                                f.write(img_bytes)
                            s.close()
                            return out_path
                except Exception: pass

        s.close()
    except Exception as e:
        print("[CDP SS ERR]", e)
    return None

def do_screenshot():
    path = os.path.join(SHOTS, f"screenshot_{int(time.time())}.png")
    
    # 1. Primary: Native C# Physical Desktop Screen Grabber (Steam / PC Monitor / Active Apps)
    exe_path = os.path.join(BASE, "ScreenGrabber.exe")
    if os.path.exists(exe_path):
        try:
            res = subprocess.run([exe_path, path], capture_output=True, text=True, timeout=5, creationflags=0x08000000)
            if os.path.exists(path) and os.path.getsize(path) > 10000:
                print(f"[SS DESKTOP SUCCESS] Captured physical PC screen: {os.path.getsize(path)} bytes")
                return path
        except Exception as e:
            print(f"[SS EXE ERR] {e}")


    # 2. Secondary: PIL ImageGrab Desktop Screen Grabber
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        img = ImageGrab.grab()
        img.save(path)
        if os.path.exists(path) and os.path.getsize(path) > 10000:
            print(f"[SS PIL SUCCESS] Captured physical desktop: {os.path.getsize(path)} bytes")
            return path
    except Exception as e:
        print(f"[SS PIL ERR] {e}")

    # 3. Tertiary: CDP Render Engine Fallback
    try:
        cdp_path = cdp_capture_screenshot()
        if cdp_path and os.path.exists(cdp_path) and os.path.getsize(cdp_path) > 10000:
            print(f"[SS CDP FALLBACK SUCCESS] Captured CDP frame: {os.path.getsize(cdp_path)} bytes")
            return cdp_path
    except Exception as e:
        print(f"[SS CDP ERR] {e}")

    return None



def get_status():
    cpu  = psutil.cpu_percent(interval=0.3)
    ram  = psutil.virtual_memory()
    c    = psutil.disk_usage("C:\\")
    g_str = "N/A"
    try:
        g = psutil.disk_usage("G:\\")
        g_str = f"{round(g.free/1024**3,1)} GB free"
    except Exception:
        pass

    msg = (
        "📊 *Status Antigravity Bot Server*\n\n"
        f"🖥️ *CPU Usage:* {cpu}%\n"
        f"🧠 *RAM Usage:* {ram.percent}%\n"
        f"💾 *Disk C:* {c.percent}% used ({round(c.free/1024**3,1)} GB free)\n"
        f"💾 *Disk G:* {g_str}\n\n"
        f"⚙️ *Service Receiver:* Active (PID {os.getpid()})\n"
        f"🙈 *Window Mode:* Silent Background (Minimized Supported)\n"
        f"⚡ *System Creator:* [TriWahyu45](https://github.com/triwahyu45)"
    )

    return msg

def get_summary_text():
    return (
        "📋 *RANGKUMAN LENGKAP ARSITEKTUR GOOGLE ANTIGRAVITY BOT v2.0*\n\n"
        "✨ *Sistem Remote Control Telegram Bridge*\n"
        "• *Prompt Injector Engine:* CDP WebSocket native key event (100% instant submit)\n"
        "• *Real-Time DOM Mirror:* Scrape AI text, code edits, terminal logs, & foto original\n"
        "• *Fast Voice Synthesizer:* Pesan suara Bahasa Indonesia 1.35x tempo cepat & jernih\n"
        "• *ScreenGrabber:* Tangkapan layar PC monitor fisik asli (Steam, Apps, Desktop)\n"
        "• *1-Klik System Tray:* Ikon aktif di dekat jam PC dengan menu Klik Kanan\n"
        "• *Keamanan Secrets:* Token & Chat ID terisolasi di secrets.json (Clean Git History)\n\n"
        "⚡ *System Creator:* [TriWahyu45](https://github.com/triwahyu45)\n"
        "🌐 *GitHub Release:* [v2.0](https://github.com/triwahyu45/Antigravity_TelegramBot)"
    )

def get_storage_text():
    try:
        c = psutil.disk_usage('C:')
        g_free_str = "N/A"
        if os.path.exists('G:'):
            g = psutil.disk_usage('G:')
            g_free_str = f"{round(g.free/1024**3, 1)} GB Free ({g.percent}% used)"

        msg = (
            "💾 *LAPORAN SISA KAPASITAS STORAGE PC (REAL-TIME)*\n\n"
            f"• *Disk C: (System)* — {round(c.free/1024**3, 1)} GB Free ({c.percent}% used)\n"
            f"• *Disk G: (Tri Wahyu)* — {g_free_str}\n"
        )
        if os.path.exists('E:'):
            e = psutil.disk_usage('E:')
            msg += f"• *Disk E: (UMUM)* — {round(e.free/1024**3, 1)} GB Free ({e.percent}% used)\n"
        if os.path.exists('F:'):
            f_disk = psutil.disk_usage('F:')
            msg += f"• *Disk F: (DODO)* — {round(f_disk.free/1024**3, 1)} GB Free ({f_disk.percent}% used)\n"
            
        msg += "\n⚡ *System Creator:* [TriWahyu45](https://github.com/triwahyu45)"
        return msg
    except Exception as err:
        return f"❌ Error cek storage: {err}"

def setup_bot_commands():
    try:
        commands = [
            types.BotCommand("status", "📊 Monitor CPU, RAM & Server PC"),
            types.BotCommand("storage", "💾 Cek Sisa Storage Disk C, G, E, F"),
            types.BotCommand("summary", "📋 Rangkuman Lengkap Arsitektur Bot"),
            types.BotCommand("ss", "📸 Tangkap Layar PC Monitor Real-Time"),
            types.BotCommand("minimize_steam", "📉 Minimize Steam & Jendela PC"),
            types.BotCommand("hide", "🙈 Sembunyikan Antigravity (Silent Mode)"),
            types.BotCommand("open_antigravity", "🖥️ Tampilkan Jendela Antigravity"),
            types.BotCommand("models", "🤖 Pilihan Model AI (Flash, Pro, Sonnet)")
        ]
        bot.set_my_commands(commands)
        log_activity("✅ Telegram 3-Strip Menu Commands Updated Successfully!")
    except Exception as e:
        log_activity(f"⚠️ Failed to set bot commands: {e}")



def kill_antigravity_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                proc.kill()
        except Exception:
            pass

def focus_and_click_wahyu_pc(main_h, is_fresh_launch=False):
    import win32gui
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
    user32 = ctypes.windll.user32
    user32.ShowWindow(main_h, 9) # SW_RESTORE
    user32.ShowWindow(main_h, 3) # SW_MAXIMIZE
    user32.SetForegroundWindow(main_h)
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    user32.SetForegroundWindow(main_h)
    time.sleep(0.2)
    
    if is_fresh_launch:
        time.sleep(4.5)
    else:
        time.sleep(0.3)
        
    if not user32.IsWindowVisible(main_h):
        return False
        
    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    sidebar_x = rect[0] + int(w * 0.05)
    sidebar_y = rect[1] + int(h * 0.36)

    user32.SetCursorPos(sidebar_x, sidebar_y)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.2)
    user32.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x0D, 0, 2, 0)
    return True

# ── Handlers ──────────────────────────────────────────────────
@bot.message_handler(commands=["start", "help"])
def h_start(msg):
    if not auth(msg): return
    welcome = (
        "✨ *Selamat datang di AGY Bot Master Control!*\n\n"
        "Gunakan menu di bawah untuk mengontrol PC & Antigravity IDE:\n"
        "• *Status PC* — Monitor CPU, RAM, Disk\n"
        "• *Screenshot* — Tangkap layar PC saat ini\n"
        "• *Buka Antigravity* — Buka & aktifkan IDE\n"
        "• *Pilih Model AI* — Pilih 11 model AI interaktif\n\n"
        "💬 *Ketik pesan apapun* untuk chatting dengan Antigravity AI di PC!"
    )
    send(msg.chat.id, welcome)

@bot.message_handler(commands=["status"])
def h_status(msg):
    if not auth(msg): return
    send(msg.chat.id, get_status())

@bot.message_handler(commands=["ss", "screenshot"])
def h_ss(msg):
    if not auth(msg): return
    try:
        bot.send_chat_action(msg.chat.id, "upload_photo")
    except: pass
    path = do_screenshot()
    if path and os.path.exists(path):
        ts_now = time.strftime("%H:%M:%S")
        size_kb = round(os.path.getsize(path) / 1024, 1)
        caption_text = f"📸 *Layar PC Live ({ts_now} WIB)*\n• Ukuran File: `{size_kb} KB` (Real-Time)"
        try:
            with open(path, "rb") as f:
                bot.send_photo(msg.chat.id, f, caption=caption_text, parse_mode="Markdown", reply_markup=kb())
        except Exception:
            with open(path, "rb") as f:
                bot.send_photo(msg.chat.id, f, caption=caption_text, parse_mode=None, reply_markup=kb())
    else:
        send(msg.chat.id, "❌ Gagal ambil screenshot layar PC.")


def model_menu_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    b1  = types.InlineKeyboardButton("⚡ 3.6 Flash (High)", callback_data="sw_model:3.6 Flash (High)")
    b2  = types.InlineKeyboardButton("⚡ 3.6 Flash (Med)", callback_data="sw_model:3.6 Flash (Medium)")
    b3  = types.InlineKeyboardButton("⚡ 3.6 Flash (Low)", callback_data="sw_model:3.6 Flash (Low)")
    
    b4  = types.InlineKeyboardButton("⚡ 3.5 Flash (High)", callback_data="sw_model:3.5 Flash (High)")
    b5  = types.InlineKeyboardButton("⚡ 3.5 Flash (Med)", callback_data="sw_model:3.5 Flash (Medium)")
    b6  = types.InlineKeyboardButton("⚡ 3.5 Flash (Low)", callback_data="sw_model:3.5 Flash (Low)")
    
    b7  = types.InlineKeyboardButton("🧠 3.1 Pro (High)", callback_data="sw_model:3.1 Pro (High)")
    b8  = types.InlineKeyboardButton("🧠 3.1 Pro (Low)", callback_data="sw_model:3.1 Pro (Low)")
    
    b9  = types.InlineKeyboardButton("🎭 Sonnet 4.6", callback_data="sw_model:Sonnet")
    b10 = types.InlineKeyboardButton("👑 Opus 4.6", callback_data="sw_model:Opus")
    b11 = types.InlineKeyboardButton("🤖 GPT-OSS 120B", callback_data="sw_model:GPT-OSS")
    
    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5, b6)
    markup.add(b7, b8)
    markup.add(b9, b10)
    markup.add(b11)
    return markup

@bot.message_handler(commands=["models", "model_menu", "pilih_model"])
def h_model_menu(msg):
    if not auth(msg): return
    try:
        bot.send_message(msg.chat.id, "🤖 *PILIH MODEL AI UNTUK ANTIGRAVITY PC:*", reply_markup=model_menu_kb(), parse_mode="Markdown")
        print("[MODEL MENU] Sent model selection inline keyboard to Telegram HP!")
    except Exception as e:
        print("[MODEL MENU ERR]", e)
        try:
            bot.send_message(msg.chat.id, "🤖 *PILIH MODEL AI UNTUK ANTIGRAVITY PC:*", reply_markup=model_menu_kb(), parse_mode=None)
        except Exception as ex:
            print("[MODEL MENU ERR 2]", ex)

@bot.message_handler(commands=["flash", "flash_high", "pro", "sonnet", "opus", "gpt"])
def h_model_shortcuts(msg):
    if not auth(msg): return
    from model_switcher import switch_model
    cmd = msg.text.split()[0].replace('/', '').lower()
    
    mapping = {
        'flash': 'Flash (Medium)',
        'flash_high': 'Flash (High)',
        'pro': 'Gemini 3.1 Pro',
        'sonnet': 'Sonnet',
        'opus': 'Opus',
        'gpt': 'GPT-OSS'
    }
    target = mapping.get(cmd, 'Flash')
    send(msg.chat.id, f"🔄 *Mencoba mengganti model ke:* `{target}`...")
    res = switch_model(target)
    if res and res.startswith('OK:'):
        send(msg.chat.id, f"✅ *Model AI di PC Berhasil Diganti ke:* `{target}`")
    else:
        send(msg.chat.id, f"⚠️ *Status:* `{res}`")

@bot.callback_query_handler(func=lambda call: call.data.startswith("sw_model:"))
def callback_model_switch(call):
    if call.from_user.id != ALLOWED_ID: return
    target = call.data.split("sw_model:", 1)[1]
    bot.answer_callback_query(call.id, f"Mengganti model ke {target}...")
    from model_switcher import switch_model
    res = switch_model(target)
    if res and res.startswith('OK:'):
        bot.send_message(call.message.chat.id, f"✅ *Model AI di PC Berhasil Diganti ke:* `{target}`", parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, f"⚠️ *Status Ganti Model:* `{res}`", parse_mode="Markdown")

@bot.message_handler(commands=["model", "ganti_model"])
def h_switch_model(msg):
    if not auth(msg): return
    from model_switcher import switch_model
    parts = msg.text.split(maxsplit=1)
    target = parts[1].strip() if len(parts) > 1 else "Flash"
    send(msg.chat.id, f"🔄 *Mencoba mengganti model ke:* `{target}`...")
    res = switch_model(target)
    if res and res.startswith('OK:'):
        model_name = res.split('OK:', 1)[1]
        send(msg.chat.id, f"✅ *Model AI di PC Berhasil Diganti ke:* `{model_name}`")
    else:
        send(msg.chat.id, f"⚠️ *Status:* `{res}`\nBuka Menu tombol: `/models`\nShortcut: `/flash`, `/pro`, `/sonnet`, `/opus`, `/gpt`")

@bot.message_handler(commands=["open_antigravity", "buka_antigravity"])


def h_minimize_all(msg):
    try:
        ps_cmd = "Get-Process -Name steam -ErrorAction SilentlyContinue | ForEach-Object { `$_.CloseMainWindow() }; (New-Object -ComObject Shell.Application).MinimizeAll()"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, creationflags=0x08000000)
        send(msg.chat.id, "📉 *Jendela Steam & Seluruh Jendela Desktop Berhasil Di-Minimize!*")
        time.sleep(0.5)
        h_ss(msg)
    except Exception as e:
        send(msg.chat.id, f"❌ Error: {e}")



def h_hide_antigravity(msg):
    try:
        import win_toggle
        win_toggle.hide_antigravity_window()
        send(msg.chat.id, "🙈 *Jendela Antigravity BERHASIL DISEMBUNYIKAN TOTAL (100% Silent Background & Hilang dari Taskbar)!*\nLayar PC & Taskbar 100% bersih. Chat Telegram HP ↔ AI di PC tetap terhubung & berbalas instan di background!")
    except Exception as e:
        send(msg.chat.id, f"❌ Gagal menyembunyikan jendela: {e}")


def h_open_antigravity(msg):
    if not auth(msg): return
    send(msg.chat.id, "🖥️ *Memulihkan Jendela Antigravity & Membuka Chat Wahyu's PC...*")
    
    def bg_open():
        user32 = ctypes.windll.user32
        target_hwnd = []
        def enum_cb(hwnd, extra):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                if "Antigravity" in title or "Wahyu" in title:
                    target_hwnd.append((hwnd, title))
            return True
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        
        # Check if process is running
        running = False
        for p in psutil.process_iter(['name']):
            try:
                if p.info['name'] and 'antigravity' in p.info['name'].lower():
                    running = True; break
            except: pass

        ANTIGRAVITY_PATH = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"

        # Launch EXE if window is not found
        if not target_hwnd:
            if os.path.exists(ANTIGRAVITY_PATH):
                send(msg.chat.id, "🚀 *Jendela belum terbuka. Menjalankan Antigravity.exe...*")
                subprocess.Popen(f'"{ANTIGRAVITY_PATH}"', shell=True, creationflags=CREATE_NO_WINDOW)
                for _ in range(30):
                    time.sleep(0.5)
                    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
                    if target_hwnd: break
            else:
                send(msg.chat.id, f"❌ *Aplikasi tidak ditemukan di path:* `{ANTIGRAVITY_PATH}`")
                return


        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if not target_hwnd:
            send(msg.chat.id, "⚠️ *Gagal menemukan jendela Antigravity.*")
            return

        hwnd, title = target_hwnd[0]
        # 1. Restore & Show Window
        user32.ShowWindow(hwnd, 9) # SW_RESTORE
        user32.ShowWindow(hwnd, 5) # SW_SHOW
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        # 2. Switch tab to Wahyu's PC via CDP
        try:
            from antigravity_injector import cdp_click_wahyu
            cdp_click_wahyu()
        except: pass
        time.sleep(0.3)

        # Keep window visible on screen (do not auto-minimize)
        send(msg.chat.id, f"📖 *Jendela Antigravity Berhasil Dipulihkan & Terbuka di Layar PC!*\n(Untuk menyembunyikan kembali ke background, ketik `sembunyikan antigravity` atau `/hide`).")

    threading.Thread(target=bg_open, daemon=True).start()

# ── Handler Media (Foto, Video, Voice Note, Audio, Dokumen) ───
media_group_buffer = {}
media_group_lock = threading.Lock()

def flush_media_group(mg_id, chat_id):
    with media_group_lock:
        if mg_id not in media_group_buffer: return
        info = media_group_buffer.pop(mg_id)
    
    paths = info['photos']
    caption = info['caption']
    count = len(paths)
    
    if count == 1:
        prompt = f"User mengirim gambar / foto ke PC (Disimpan di: {paths[0]})."
        msg_text = "📥 *Gambar / foto diterima!* Disimpan di PC & dimasukkan ke antrean AI."
    else:
        paths_str = ", ".join(paths)
        prompt = f"User mengirim album {count} foto/gambar sekaligus ke PC (Disimpan di: {paths_str})."
        msg_text = f"📸 *Album {count} foto diterima sekaligus!* Disimpan di PC & dimasukkan ke antrean AI."

    if caption:
        prompt += f" Pesan/Caption dari user: \"{caption}\""

    record_injected_prompt(prompt, raw_text=caption or prompt)
    msg_queue.put((prompt, chat_id, caption or prompt))
    send(chat_id, msg_text, use_kb=False)

@bot.message_handler(content_types=['photo', 'video', 'voice', 'audio', 'video_note', 'document'])
def h_media(msg):
    if not auth(msg): return
    if is_dup_msg(msg): return
    save_last_user_msg_id(msg.message_id)
    try:
        bot.send_chat_action(msg.chat.id, "typing")
        caption = (msg.caption or "").strip()
        
        file_info = None
        media_type = "file"
        prefix = "file"

        if msg.photo:
            file_info = bot.get_file(msg.photo[-1].file_id)
            media_type = "gambar / foto"
            prefix = "photo"
        elif msg.video:
            file_info = bot.get_file(msg.video.file_id)
            media_type = "video"
            prefix = "video"
        elif msg.voice:
            file_info = bot.get_file(msg.voice.file_id)
            media_type = "voice note (pesan suara)"
            prefix = "voice"
        elif msg.audio:
            file_info = bot.get_file(msg.audio.file_id)
            media_type = "file audio / musik"
            prefix = "audio"
        elif msg.video_note:
            file_info = bot.get_file(msg.video_note.file_id)
            media_type = "video note (pesan video bulat)"
            prefix = "video_note"
        elif msg.document:
            file_info = bot.get_file(msg.document.file_id)
            media_type = f"dokumen ({msg.document.file_name or 'file'})"
            prefix = "doc"
            
        if not file_info: return

        downloaded_file = bot.download_file(file_info.file_path)
        ext = os.path.splitext(file_info.file_path)[1] or ".bin"
        save_path = os.path.join(RECV_DIR, f"{prefix}_{int(time.time())}_{os.urandom(2).hex()}{ext}")
        with open(save_path, "wb") as f:
            f.write(downloaded_file)
            
        log_activity(f"📁 [MEDIA RECEIVED] {media_type} saved to {save_path}")
        
        # Handle Telegram Multi-Photo Album Media Groups
        mg_id = getattr(msg, 'media_group_id', None)
        if mg_id and msg.photo:
            with media_group_lock:
                if mg_id not in media_group_buffer:
                    media_group_buffer[mg_id] = {
                        'photos': [save_path],
                        'caption': caption,
                        'timer': None
                    }
                    t = threading.Timer(1.2, flush_media_group, args=(mg_id, msg.chat.id))
                    media_group_buffer[mg_id]['timer'] = t
                    t.start()
                else:
                    media_group_buffer[mg_id]['photos'].append(save_path)
                    if caption and not media_group_buffer[mg_id]['caption']:
                        media_group_buffer[mg_id]['caption'] = caption
            return

        # Single media upload
        media_prompt = f"User mengirim {media_type} ke PC (Disimpan di: {save_path})."
        if caption:
            media_prompt += f" Pesan/Caption dari user: \"{caption}\""
            
        record_injected_prompt(media_prompt, raw_text=caption or media_prompt)
        msg_queue.put((media_prompt, msg.chat.id, caption or media_prompt))
        send(msg.chat.id, f"📥 *{media_type.capitalize()} diterima!* Disimpan di PC & dimasukkan ke antrean AI.", use_kb=False)

    except Exception as e:
        log_activity(f"[MEDIA ERR] {e}")
        send(msg.chat.id, f"❌ *Gagal memproses media dari Telegram:* {e}")


def h_open_chrome(msg, target_url="https://www.google.com"):
    site_name = "YouTube" if "youtube.com" in target_url else "Google Chrome"
    send(msg.chat.id, f"🌐 *Membuka {site_name} di Chrome PC...*")
    def bg_chrome():
        try:
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, "--new-window", target_url])
                send(msg.chat.id, f"✅ *{site_name} Berhasil Dibuka di Chrome PC!*")
            else:
                subprocess.Popen(["powershell", "-Command", f"Start-Process {target_url}"])
                send(msg.chat.id, f"✅ *{site_name} Berhasil Dibuka di Browser Default!*")
            time.sleep(1.5)
            h_ss(msg)
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal membuka {site_name}:* {e}")
    threading.Thread(target=bg_chrome, daemon=True).start()

def h_close_chrome(msg):
    send(msg.chat.id, "🚪 *Menutup Google Chrome di PC...*")
    def bg_close():
        try:
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True, creationflags=0x08000000)
            send(msg.chat.id, "✅ *Google Chrome Berhasil Ditutup Total!*")
            time.sleep(1.0)
            h_ss(msg)
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal menutup Chrome:* {e}")
    threading.Thread(target=bg_close, daemon=True).start()




def h_youtube_search(msg, query):
    import urllib.parse
    encoded = urllib.parse.quote_plus(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded}"
    send(msg.chat.id, f"🎶 *Mencari di YouTube:* `{query}`...")
    def bg_yt():
        try:
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, "--new-window", search_url])
            else:
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"])
            send(msg.chat.id, f"✅ *Hasil Pencarian YouTube '{query}' Berhasil Dibuka!*")
            time.sleep(1.5)
            h_ss(msg)
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal mencari di YouTube:* {e}")
    threading.Thread(target=bg_yt, daemon=True).start()

# ── Handler Teks Pesan dari Telegram ──────────────────────────
@bot.message_handler(func=lambda m: True)
def h_text(msg):
    if not msg.text: return
    t  = msg.text.strip()
    tl = t.lower()
    log_activity(f"📩 RECEIVED FROM TELEGRAM ({msg.from_user.first_name if msg.from_user else 'Unknown'}): {t}")

    if not auth(msg): return
    if is_dup_msg(msg): return
    save_last_user_msg_id(msg.message_id)

    if tl.startswith('/ecc') or tl in ['ecc', 'dashboard ecc']:
        h_ecc_dashboard(msg)
    elif tl.startswith('/architect'):
        h_ecc_delegate(msg, 'architect')
    elif tl.startswith('/tester'):
        h_ecc_delegate(msg, 'tester')
    elif tl.startswith('/security'):
        h_ecc_delegate(msg, 'security')
    elif tl.startswith('/debug'):
        h_ecc_delegate(msg, 'debug')
    elif tl.startswith('/uiux'):
        h_ecc_delegate(msg, 'ui_ux')
    elif tl.startswith('/mem') or tl in ['memori', 'ecc mem']:
        h_ecc_mem(msg)
    elif tl.startswith('/subagents') or tl in ['subagent', 'ecc subagents']:
        h_ecc_subagents(msg)
    elif tl.startswith('/learn'):
        h_ecc_learn(msg)
    elif tl in ("status", "status pc", "cek laptop", "cek pc", "kondisi", "kondisi pc", "/status", "📊 status pc"):
        h_status(msg)
    elif tl in ("/storage", "storage", "cek storage", "sisa storage", "💾 storage", "disk"):
        send(msg.chat.id, get_storage_text())
    elif tl in ("/summary", "summary", "summary antigravity", "📋 summary antigravity", "rangkuman"):
        send(msg.chat.id, get_summary_text())

    elif tl in ("/ss", "/screenshot", "ss", "screenshot", "foto layar", "📸 screenshot"):
        h_ss(msg)

    elif tl in ("klik", "/klik", "click", "mouse klik", "🖱️ klik"):
        try:
            import pc_remote_control as rc
            rc.mouse_click()
            send(msg.chat.id, "🖱️ *Mouse fisik PC berhasil diklik!*")
            time.sleep(1.0)
            h_ss(msg)
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal mengklik mouse:* {e}")

    elif tl in ("home", "home yt", "beranda", "beranda youtube", "/home", "🏠 home"):
        h_open_chrome(msg, "https://www.youtube.com")

    elif tl in ("back", "kembali", "/back", "buka back", "⬅️ back"):

        try:
            import pc_remote_control as rc
            rc.browser_back()
            send(msg.chat.id, "⬅️ *Browser Kembali ke Halaman Sebelumnya (Back)!*")
            time.sleep(1.0)
            h_ss(msg)
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal back:* {e}")


    elif tl in ("klik video", "buka video", "play video", "klik hasil", "pilih video", "▶️ play video"):
        try:
            import pc_remote_control as rc
            rc.click_first_yt_result()
            send(msg.chat.id, "🖱️ *Mouse mengklik hasil video pertama di layar PC!*")
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal mengklik video:* {e}")


    elif tl in ("pause", "play", "pause video", "klik tengah", "play/pause"):
        try:
            import pc_remote_control as rc
            rc.click_center_play()
            send(msg.chat.id, "⏯️ *Mouse mengklik layar tengah (Play/Pause Video)!*")
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal play/pause:* {e}")

    elif tl in ("scroll bawah", "scroll down", "layar bawah"):
        try:
            import pc_remote_control as rc
            rc.mouse_scroll(-400)
            send(msg.chat.id, "📜 *Mouse scroll ke bawah di layar PC!*")
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal scroll:* {e}")

    elif tl in ("scroll atas", "scroll up", "layar atas"):
        try:
            import pc_remote_control as rc
            rc.mouse_scroll(400)
            send(msg.chat.id, "📜 *Mouse scroll ke atas di layar PC!*")
        except Exception as e:
            send(msg.chat.id, f"❌ *Gagal scroll:* {e}")

    elif ("cari" in tl or "putar" in tl or "play" in tl) and ("yt" in tl or "youtube" in tl or "lagu" in tl or "musik" in tl):
        q = t
        for p_word in ["cari di yt", "cari di youtube", "sekarang cari di yt", "buka lagu", "putar lagu", "play"]:
            if p_word in q.lower():
                q = re.sub(p_word, '', q, flags=re.IGNORECASE).strip()
        h_youtube_search(msg, q or t)

    elif "youtube" in tl and ("buka" in tl or "open" in tl or "/youtube" in tl or "buka youtube" in tl):
        h_open_chrome(msg, "https://www.youtube.com")
    elif tl in ("tutup chrome", "close chrome", "/close_chrome", "tutup browser", "close browser", "🚪 tutup chrome"):
        h_close_chrome(msg)
    elif tl in ("chrome", "/buka_chrome", "buka chrome", "open chrome", "chrome", "🌐 buka chrome"):
        h_open_chrome(msg, "https://www.google.com")

    elif tl in ("/buka_antigravity", "/open_antigravity", "/show", "buka antigravity", "open antigravity", "🖥️ buka antigravity"):
        h_open_antigravity(msg)



    elif tl in ("/hide", "/sembunyikan", "sembunyikan antigravity", "hide antigravity", "🙈 sembunyikan antigravity", "🙈 hide antigravity"):
        h_hide_antigravity(msg)
    elif tl in ("/minimize_all", "/minimize_steam", "minimize steam", "minimize all", "minimize steamnya", "minimize steam dong", "📉 minimize steam"):
        h_minimize_all(msg)
    elif tl in ("/models", "/model", "pilih model ai", "ganti model", "🤖 pilih model ai"):
        h_model_menu(msg)


    else:
        # Chat bebas -> Dukung Fitur Reply Pesan Telegram secara Natural
        prompt = t
        if msg.reply_to_message:
            reply_raw = (msg.reply_to_message.text or msg.reply_to_message.caption or "").strip()
            if reply_raw:
                # Bersihkan tag HTML/Markdown & potong maksimal 60 karakter agar ringkas
                reply_clean = re.sub(r'<[^>]+>', '', reply_raw).replace('\n', ' ')
                if len(reply_clean) > 60: reply_clean = reply_clean[:60] + "..."
                prompt = f"[Membalas: \"{reply_clean}\"]\n{t}"

        try:
            bot.send_chat_action(msg.chat.id, "typing")
        except: pass

        msg_queue.put((prompt, msg.chat.id, t))



        q_size = msg_queue.qsize()
        log_activity(f"📥 QUEUED (size={q_size}): {prompt[:50]}")
        
        if q_size > 1:
            send(msg.chat.id, f"📋 *AI sedang memproses perintah sebelumnya. Pesan Anda masuk antrean Queue (#{q_size})*", use_kb=False)



# ── Auto-Hide Antigravity Window on Bot Startup ───────────────
# (DEACTIVATED so window is NEVER forcibly minimized while user is using it)



# ── Auto-Re-Launch Watcher (Re-opens Antigravity in SW_HIDE if closed by X) ──
def antigravity_auto_relauncher_worker():
    ANTIGRAVITY_PATH = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"
    while True:
        try:
            time.sleep(5)
            running = False
            for p in psutil.process_iter(['name']):
                try:
                    if p.info['name'] and 'antigravity' in p.info['name'].lower():
                        running = True; break
                except: pass
                
            if not running and os.path.exists(ANTIGRAVITY_PATH):
                log_activity("[AUTOLAUNCH] Antigravity.exe was closed! Auto-relaunching in background SW_HIDE...")
                subprocess.Popen(f'"{ANTIGRAVITY_PATH}"', shell=True, creationflags=CREATE_NO_WINDOW)
                time.sleep(3)
                user32 = ctypes.windll.user32
                target_hwnd = None
                def enum_cb(hwnd, lparam):
                    nonlocal target_hwnd
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        t_lower = buff.value.lower()
                        if "wahyu's pc" in t_lower or "antigravity" in t_lower:
                            target_hwnd = hwnd; return False
                    return True
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
                user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
                if target_hwnd:
                    user32.ShowWindow(target_hwnd, 0) # SW_HIDE (0) -> Completely hidden from taskbar!

        except Exception as e:
            print(f"[RELAUNCHER ERR] {e}")

threading.Thread(target=antigravity_auto_relauncher_worker, daemon=True, name="AutoRelauncher").start()


if __name__ == "__main__":
    ensure_singleton()
    setup_bot_commands()
    print(f"[NODE 1: BOT RECEIVER] Running PID={os.getpid()} with Message Queue & Photo System...")


    try:
        bot.delete_webhook()
    except Exception:
        pass
    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=10, long_polling_timeout=10)
        except Exception as e:
            try:
                log_activity(f"[BOT POLLING ERR] {e}")
            except: pass
            time.sleep(1)

