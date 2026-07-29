"""
dom_mirror_v2.py - Mirror chat Antigravity -> Telegram via DOM polling
Baca pesan dari DOM div.whitespace-pre-wrap.text-sm (user)
dan cari AI responses dari rendered blocks.
"""
import os, sys, json, socket, struct, base64, time
import urllib.request, psutil
from urllib.parse import urlparse
import telebot

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except: pass

from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
SEEN_FILE  = r"G:\Antigravity_Server\dom_seen_v2.json"

bot = telebot.TeleBot(BOT_TOKEN)

# ─── CDP ─────────────────────────────────────────────────────────────────────
_port = None

def get_port():
    global _port
    if _port:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{_port}/json/version", timeout=1)
            return _port
        except: _port = None
    ag_pids = set()
    for proc in psutil.process_iter(['pid','name']):
        try:
            if 'antigravity' in (proc.info['name'] or '').lower():
                ag_pids.add(proc.info['pid'])
        except: pass
    for conn in psutil.net_connections(kind='tcp'):
        try:
            if conn.status=='LISTEN' and conn.laddr.ip=='127.0.0.1' and conn.pid in ag_pids:
                r = urllib.request.urlopen(f"http://127.0.0.1:{conn.laddr.port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    _port = conn.laddr.port
                    return _port
        except: pass
    return None

def cdp_eval(js, port=None):
    port = port or get_port()
    if not port: return None
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
        ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type')=='page'), None)
        if not ws_url: return None
        path = urlparse(ws_url).path
        s = socket.socket(); s.connect(("127.0.0.1", port)); s.settimeout(6)
        key = base64.b64encode(os.urandom(16)).decode()
        s.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
        resp = b""
        while b"\r\n\r\n" not in resp: resp += s.recv(4096)
        p = json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":js,"returnByValue":True}}).encode()
        ln = len(p); mk = os.urandom(4)
        h = bytes([0x81, 0x80|(ln if ln<126 else 126)])
        if ln>=126: h += struct.pack('>H',ln)
        s.sendall(h + mk + bytes(b^mk[i%4] for i,b in enumerate(p)))
        data = b""
        for _ in range(40):
            chunk = s.recv(65536)
            if not chunk: break
            data += chunk
            if len(data)>2:
                l=data[1]&0x7F; off=2
                if l==126: l=struct.unpack('>H',data[2:4])[0]; off=4
                elif l==127: l=struct.unpack('>Q',data[2:10])[0]; off=10
                if len(data)>=off+l:
                    s.close()
                    return json.loads(data[off:off+l].decode()).get('result',{}).get('result',{}).get('value')
        s.close()
    except Exception as e:
        print("[CDP]", e)
    return None

# ─── DOM Scraper ──────────────────────────────────────────────────────────────
JS_SCRAPE = """
(function() {
    var msgs = [];
    var title = document.title;
    
    // Only scrape if on Wahyu's PC page
    if (!title.includes("Wahyu")) {
        return JSON.stringify({page: title, msgs: []});
    }
    
    // 1. User messages
    var userEls = document.querySelectorAll('div.whitespace-pre-wrap.text-sm');
    for (var el of userEls) {
        var txt = (el.innerText || '').trim();
        var parentCls = el.parentElement ? el.parentElement.className : '';
        if (txt && txt.length > 0) {
            msgs.push({role: 'user', text: txt});
        }
    }
    
    // 2. AI responses - cari semua paragraf di luar user message area
    // Antigravity render markdown ke paragraf normal
    var allParas = document.querySelectorAll('p, h1, h2, h3, h4, li');
    var aiBlock = '';
    var aiBlocks = [];
    
    // Group paragraf yang berdekatan jadi satu block AI response
    var mainEl = document.querySelector('main') || document.body;
    var walker = document.createTreeWalker(
        mainEl,
        NodeFilter.SHOW_TEXT,
        null, false
    );
    
    // Alternative: cari container AI response
    // Biasanya wrapper div yang berisi p, code, pre, h1-h6
    var containers = document.querySelectorAll('div');
    for (var c of containers) {
        // Hanya direct children yang punya p/code/h2 (AI markdown)
        var hasMD = c.querySelector('p, code, pre, h1, h2, h3, ol, ul');
        var isUserMsg = c.className.includes('whitespace-pre-wrap');
        var txt = (c.innerText || '').trim();
        if (hasMD && !isUserMsg && txt.length > 50 && txt.length < 8000) {
            // Pastikan bukan nested (parent bukan container lain)
            var parentHasMD = c.parentElement && c.parentElement.querySelector(':scope > div > p');
            if (!parentHasMD || c.parentElement.tagName === 'BODY') {
                msgs.push({role: 'ai', text: txt.substring(0, 4000)});
            }
        }
    }
    
    return JSON.stringify({page: title, msgs: msgs});
})()
"""

# ─── Telegram Sender ──────────────────────────────────────────────────────────
def send_tg(text, role):
    if not text or len(text.strip()) < 3: return
    prefix = "You (PC):" if role=='user' else "Antigravity:"
    full = prefix + "\n" + text.strip()
    for chunk in [full[i:i+3500] for i in range(0, len(full), 3500)]:
        try:
            bot.send_message(ALLOWED_ID, chunk)
            time.sleep(0.3)
        except Exception as e:
            print("[TG]", e)

# ─── Seen tracker ─────────────────────────────────────────────────────────────
def load_seen():
    try:
        if os.path.exists(SEEN_FILE):
            return set(json.load(open(SEEN_FILE, encoding='utf-8')))
    except: pass
    return set()

def save_seen(seen):
    try:
        json.dump(list(seen)[-2000:], open(SEEN_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    except: pass

# ─── Main loop ────────────────────────────────────────────────────────────────
def run():
    seen = load_seen()
    print("[MIRROR v2] Started. Seen:", len(seen), "msgs")
    errors = 0

    while True:
        try:
            val = cdp_eval(JS_SCRAPE)
            if not val:
                errors += 1
                if errors % 10 == 0:
                    print("[MIRROR] CDP tidak tersedia, retry...")
                time.sleep(3)
                continue

            data = json.loads(val)
            page = data.get('page', '')
            msgs = data.get('msgs', [])
            errors = 0

            if not page or 'Wahyu' not in page:
                # Bukan di Wahyu's PC, tunggu
                time.sleep(3)
                continue

            new_count = 0
            for m in msgs:
                key = m['role'] + ":" + m['text'][:150].strip()
                if key not in seen:
                    seen.add(key)
                    send_tg(m['text'], m['role'])
                    new_count += 1
                    print("[MIRROR] Sent", m['role'], ":", m['text'][:60])

            if new_count:
                save_seen(seen)

        except Exception as e:
            print("[MIRROR ERR]", e)
        time.sleep(3)

if __name__ == "__main__":
    run()
