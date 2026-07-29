"""
antigravity_cdp_master.py
=========================
Master script CDP-only untuk Antigravity:
1. open_antigravity()   - Buka/fokus window Antigravity
2. click_tab(name)      - Klik tab sidebar via CDP DOM (New Conv, Conv History, Scheduled Tasks, Wahyu's PC)
3. navigate_all()       - Navigasi semua tab berurutan
4. mirror_chat()        - Mirror pesan chat ke Telegram via DOM polling

Tidak butuh koordinat pixel sama sekali - semua via CDP JS injection.
"""

import os, sys, json, socket, struct, base64, time, re
import urllib.request
import ctypes, win32gui, psutil, subprocess
import telebot

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except: pass

# ─── Config ───────────────────────────────────────────────────────────────────
from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
BASE       = r"G:\Antigravity_Server"
SEEN_FILE  = os.path.join(BASE, "cdp_mirror_seen.json")
AGY_EXE    = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"

bot = telebot.TeleBot(BOT_TOKEN)

# ─── CDP Core ─────────────────────────────────────────────────────────────────
_cdp_port_cache = None

def find_cdp_port(force=False):
    global _cdp_port_cache
    if _cdp_port_cache and not force:
        return _cdp_port_cache
    ag_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                ag_pids.add(proc.info['pid'])
        except: pass
    for conn in psutil.net_connections(kind='tcp'):
        try:
            if conn.status == 'LISTEN' and conn.laddr.ip == '127.0.0.1' and conn.pid in ag_pids:
                port = conn.laddr.port
                r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    _cdp_port_cache = port
                    return port
        except: pass
    return None

def cdp_eval(js_code, port=None):
    """Inject JS ke Antigravity page dan return hasilnya"""
    if not port:
        port = find_cdp_port()
    if not port:
        return None
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
        ws_url = None
        for t in json.loads(req.read()):
            if t.get('type') == 'page':
                ws_url = t.get('webSocketDebuggerUrl')
                break
        if not ws_url: return None
        from urllib.parse import urlparse
        path = urlparse(ws_url).path
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        sock.settimeout(5)
        key = base64.b64encode(os.urandom(16)).decode()
        hs = (f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
              f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
              f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        sock.sendall(hs.encode())
        resp = b""
        while b"\r\n\r\n" not in resp: resp += sock.recv(4096)
        if "101" not in resp.decode().split('\r\n')[0]:
            sock.close(); return None
        payload = json.dumps({"id":1,"method":"Runtime.evaluate",
            "params":{"expression":js_code,"returnByValue":True}}).encode()
        ln = len(payload)
        mk = os.urandom(4)
        hdr = bytes([0x81, 0x80|(ln if ln<126 else 126)])
        if ln >= 126: hdr += struct.pack('>H', ln)
        hdr += mk
        sock.sendall(hdr + bytes(b ^ mk[i%4] for i,b in enumerate(payload)))
        data = b""
        for _ in range(30):
            chunk = sock.recv(65536)
            if not chunk: break
            data += chunk
            if len(data) > 2:
                l = data[1] & 0x7F; off = 2
                if l == 126: l = struct.unpack('>H', data[2:4])[0]; off = 4
                elif l == 127: l = struct.unpack('>Q', data[2:10])[0]; off = 10
                if len(data) >= off + l:
                    sock.close()
                    return json.loads(data[off:off+l].decode()).get('result',{}).get('result',{}).get('value')
        sock.close()
    except Exception as e:
        print("[CDP ERR]", e)
    return None

# ─── Antigravity Window ────────────────────────────────────────────────────────
def get_agy_hwnd():
    res = []
    def cb(hwnd, r):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if 'antigravity' in t.lower() or "wahyu" in t.lower():
                r.append(hwnd)
        return True
    win32gui.EnumWindows(cb, res)
    return res[0] if res else None

def open_antigravity():
    """Buka Antigravity jika belum buka, lalu fokus dan switch ke Wahyu's PC"""
    hwnd = get_agy_hwnd()
    if not hwnd:
        print("[OPEN] Launching Antigravity...")
        subprocess.Popen([AGY_EXE], creationflags=subprocess.DETACHED_PROCESS)
        # Tunggu sampai window muncul
        for _ in range(20):
            time.sleep(1)
            hwnd = get_agy_hwnd()
            if hwnd: break
        if not hwnd:
            print("[OPEN] Failed to open Antigravity!")
            return False
        # Tunggu CDP ready
        for _ in range(15):
            time.sleep(1)
            if find_cdp_port(force=True):
                break
        print("[OPEN] Antigravity launched, CDP ready")
    else:
        print("[OPEN] Antigravity already open, focusing...")

    # Fokus window
    user32 = ctypes.windll.user32
    user32.keybd_event(0x12, 0, 0, 0)  # Alt press
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x12, 0, 2, 0)  # Alt release
    time.sleep(0.3)

    # Switch ke Wahyu's PC via CDP
    result = click_tab("Wahyu's PC")
    print("[OPEN] Switched to Wahyu's PC:", result)
    return True

# ─── Sidebar Navigation via CDP ───────────────────────────────────────────────
# Map nama tab ke text yang dicari di DOM
TAB_TEXTS = {
    "new":       ["New Conversation"],
    "history":   ["Conversation History"],
    "scheduled": ["Scheduled Tasks"],
    "wahyu":     ["Wahyu's PC"],
    # Juga terima nama lengkap
    "New Conversation":   ["New Conversation"],
    "Conversation History": ["Conversation History"],
    "Scheduled Tasks":    ["Scheduled Tasks"],
    "Wahyu's PC":         ["Wahyu's PC"],
}

def click_tab(name):
    """Klik sidebar tab via CDP DOM - zero koordinat"""
    targets = TAB_TEXTS.get(name, [name])
    for target in targets:
        js = f"""
        (function() {{
            var target = {json.dumps(target)};
            // Cari di semua elemen clickable
            var all = document.querySelectorAll('li, div, a, button, span');
            for (var el of all) {{
                var txt = (el.innerText || el.textContent || '').trim();
                if (txt === target && el.offsetParent !== null) {{
                    el.click();
                    return 'OK:' + el.tagName + ':' + el.className.substring(0,40);
                }}
            }}
            // Partial match fallback
            for (var el of all) {{
                var txt = (el.innerText || el.textContent || '').trim();
                if (txt.includes(target) && el.offsetParent !== null && el.children.length === 0) {{
                    el.parentElement.click();
                    return 'OK_PARTIAL:' + el.tagName;
                }}
            }}
            return 'NOT_FOUND:' + target;
        }})()
        """
        result = cdp_eval(js)
        if result and result.startswith('OK'):
            return result
    return "FAILED:" + name

def navigate_all(delay=1.5):
    """Navigasi semua tab berurutan via CDP"""
    steps = ["New Conversation", "Conversation History", "Scheduled Tasks", "Wahyu's PC"]
    results = {}
    for step in steps:
        print(f"[NAV] Clicking: {step}")
        r = click_tab(step)
        results[step] = r
        print(f"  -> {r}")
        time.sleep(delay)
    return results

# ─── Chat Mirror via DOM ───────────────────────────────────────────────────────
def get_chat_messages():
    """Baca pesan user dan AI dari DOM Antigravity"""
    js = """
    (function() {
        var msgs = [];
        // User messages: div.whitespace-pre-wrap.text-sm
        var userEls = document.querySelectorAll('div.whitespace-pre-wrap.text-sm');
        for (var el of userEls) {
            var txt = (el.innerText || '').trim();
            if (txt && txt.length > 1 && el.offsetParent !== null)
                msgs.push({role: 'user', text: txt.substring(0, 2000)});
        }
        // AI responses: cari block teks panjang dari AI
        var aiEls = document.querySelectorAll('[class*="prose"], [class*="markdown"], [class*="response"], [class*="assistant"]');
        for (var el of aiEls) {
            var txt = (el.innerText || '').trim();
            if (txt && txt.length > 20 && el.offsetParent !== null)
                msgs.push({role: 'ai', text: txt.substring(0, 3000)});
        }
        return JSON.stringify(msgs);
    })()
    """
    val = cdp_eval(js)
    if val:
        try: return json.loads(val)
        except: pass
    return []

def load_seen():
    if os.path.exists(SEEN_FILE):
        try: return set(json.load(open(SEEN_FILE)))
        except: pass
    return set()

def save_seen(seen):
    try: json.dump(list(seen)[-1000:], open(SEEN_FILE, 'w'))
    except: pass

def send_to_tg(text, role):
    prefix = "You (PC):" if role == 'user' else "Antigravity:"
    for chunk in [text[i:i+3500] for i in range(0, len(text), 3500)]:
        try:
            bot.send_message(ALLOWED_ID, prefix + "\n" + chunk)
        except Exception as e:
            print("[TG ERR]", e)

def mirror_worker():
    print("[MIRROR] Started")
    seen = load_seen()
    while True:
        try:
            msgs = get_chat_messages()
            for m in msgs:
                key = m['role'] + ":" + m['text'][:120]
                if key not in seen:
                    seen.add(key)
                    send_to_tg(m['text'], m['role'])
                    save_seen(seen)
                    print("[MIRROR] Sent:", m['role'], m['text'][:50])
        except Exception as e:
            print("[MIRROR ERR]", e)
        time.sleep(3)

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "open":
        open_antigravity()
    elif cmd == "nav":
        navigate_all()
    elif cmd == "tab":
        name = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Wahyu's PC"
        print(click_tab(name))
    elif cmd == "mirror":
        mirror_worker()
    elif cmd == "wahyu":
        print(click_tab("Wahyu's PC"))
    else:
        print("Usage: python antigravity_cdp_master.py [open|nav|tab <name>|mirror|wahyu]")
        print("  open   - Buka Antigravity + switch ke Wahyu's PC")
        print("  nav    - Navigasi semua tab berurutan")
        print("  tab    - Klik tab spesifik: tab 'Scheduled Tasks'")
        print("  mirror - Start DOM chat mirror ke Telegram")
        print("  wahyu  - Langsung switch ke Wahyu's PC")
