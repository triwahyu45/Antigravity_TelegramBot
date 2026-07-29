"""
DOM-based Chat Mirror v2
Baca konten chat dari Antigravity DOM via CDP, kirim ke Telegram.
Cara kerja: poll DOM setiap 2 detik, deteksi pesan baru, kirim ke TG.
"""
import os, sys, time, json, socket, struct, base64, re, urllib.request
import telebot

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except: pass

from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
BASE       = r"G:\Antigravity_Server"
SEEN_FILE  = os.path.join(BASE, "dom_mirror_seen.json")

bot = telebot.TeleBot(BOT_TOKEN)

def find_cdp_port():
    import psutil
    ag_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                ag_pids.add(proc.info['pid'])
        except: pass
    for conn in psutil.net_connections(kind='tcp'):
        if conn.status == 'LISTEN' and conn.laddr.ip == '127.0.0.1' and conn.pid in ag_pids:
            port = conn.laddr.port
            try:
                r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    return port
            except: pass
    return None

def cdp_get_page_ws(port):
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    for t in json.loads(req.read()):
        if t.get('type') == 'page':
            return t.get('webSocketDebuggerUrl')
    return None

def raw_ws_eval(port, js_code):
    ws_url = cdp_get_page_ws(port)
    if not ws_url: return None
    from urllib.parse import urlparse
    parsed = urlparse(ws_url)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", port))
    sock.settimeout(5)
    key = base64.b64encode(os.urandom(16)).decode()
    handshake = (
        f"GET {parsed.path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(handshake.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        resp += sock.recv(4096)
    if "101" not in resp.decode().split('\r\n')[0]:
        sock.close()
        return None
    
    payload = json.dumps({"id": 1, "method": "Runtime.evaluate",
        "params": {"expression": js_code, "returnByValue": True}}).encode()
    length = len(payload)
    mask_key = os.urandom(4)
    header = bytes([0x81, 0x80 | (length if length < 126 else 126)])
    if length >= 126:
        header += struct.pack('>H', length)
    header += mask_key
    masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    sock.sendall(header + masked)
    
    data = b""
    for _ in range(20):
        try:
            chunk = sock.recv(8192)
            if not chunk: break
            data += chunk
            if len(data) > 2:
                ln = data[1] & 0x7F
                offset = 2
                if ln == 126: ln = struct.unpack('>H', data[2:4])[0]; offset = 4
                elif ln == 127: ln = struct.unpack('>Q', data[2:10])[0]; offset = 10
                if len(data) >= offset + ln:
                    result = json.loads(data[offset:offset+ln].decode())
                    sock.close()
                    return result.get('result', {}).get('result', {}).get('value')
        except: break
    sock.close()
    return None

def get_chat_messages(port):
    """Ambil semua pesan dari chat DOM Wahyu's PC"""
    js = """
    (function() {
        var results = [];
        
        // Cari semua pesan di chat area
        // User messages
        var userMsgs = document.querySelectorAll('[data-role="user"], [class*="user-message"], [class*="UserMessage"]');
        for (var el of userMsgs) {
            var txt = (el.innerText || '').trim();
            if (txt) results.push({role: 'user', text: txt.substring(0, 500)});
        }
        
        // AI responses - cari elemen yang berisi teks panjang dari AI
        var aiMsgs = document.querySelectorAll('[data-role="assistant"], [class*="assistant"], [class*="ModelMessage"], [class*="ai-message"]');
        for (var el of aiMsgs) {
            var txt = (el.innerText || '').trim();
            if (txt && txt.length > 10) results.push({role: 'assistant', text: txt.substring(0, 1000)});
        }
        
        // Fallback: cari semua text block yang cukup panjang di main content area
        if (results.length === 0) {
            var main = document.querySelector('main, [class*="chat"], [class*="conversation"], [class*="messages"]');
            if (main) {
                var blocks = main.querySelectorAll('p, div');
                for (var el of blocks) {
                    if (el.children.length === 0) {
                        var txt = (el.innerText || '').trim();
                        if (txt && txt.length > 20) {
                            results.push({role: 'unknown', text: txt.substring(0, 500)});
                        }
                    }
                }
            }
        }
        
        return JSON.stringify(results.slice(-10));  // 10 pesan terakhir
    })()
    """
    val = raw_ws_eval(port, js)
    if val:
        try:
            return json.loads(val)
        except: pass
    return []

def load_seen():
    if os.path.exists(SEEN_FILE):
        try: return set(json.load(open(SEEN_FILE)))
        except: pass
    return set()

def save_seen(seen):
    try: json.dump(list(seen)[-500:], open(SEEN_FILE, 'w'))
    except: pass

def send_to_tg(text, role):
    if not text or len(text) < 3: return
    prefix = "You (PC):" if role == 'user' else "Antigravity:"
    chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]
    for chunk in chunks:
        try:
            bot.send_message(ALLOWED_ID, prefix + "\n" + chunk, parse_mode=None)
        except Exception as e:
            print("[TG ERR]", e)

def mirror_worker():
    print("[DOM MIRROR] Started")
    seen = load_seen()
    port = None
    
    while True:
        try:
            if not port:
                port = find_cdp_port()
                if not port:
                    print("[DOM MIRROR] CDP port not found, retrying...")
                    time.sleep(5)
                    continue
                print("[DOM MIRROR] CDP port:", port)
            
            msgs = get_chat_messages(port)
            if msgs:
                new_msgs = []
                for m in msgs:
                    key = m['role'] + ":" + m['text'][:100]
                    if key not in seen:
                        seen.add(key)
                        new_msgs.append(m)
                
                if new_msgs:
                    save_seen(seen)
                    for m in new_msgs:
                        send_to_tg(m['text'], m['role'])
                        print("[DOM MIRROR] Sent:", m['role'], m['text'][:50])
        except Exception as e:
            print("[DOM MIRROR ERR]", e)
            port = None
        time.sleep(3)

if __name__ == "__main__":
    mirror_worker()
