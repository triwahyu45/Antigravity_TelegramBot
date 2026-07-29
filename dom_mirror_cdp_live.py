"""
dom_mirror_cdp_live.py - Real-time AI mirror via CDP MutationObserver
- Persistent WebSocket CDP connection (no 3-second polling)
- MutationObserver watches AI response container directly
- Edit Telegram message in-place as AI types
- Sub-second latency vs 3-second polling
"""
import os, sys, json, socket, struct, base64, time, hashlib, re, threading, queue
import urllib.request, psutil
from urllib.parse import urlparse, unquote
import telebot

import io

# File-based logging (works in non-interactive/Task Scheduler mode)
_LOG = open(r"G:\Antigravity_Server\cdp_live.log", "a", encoding="utf-8", buffering=1)
def _log(*args):
    msg = " ".join(str(a) for a in args)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    _LOG.write(f"[{ts}] {msg}\n")
    _LOG.flush()
    try: print(f"[{ts}] {msg}", flush=True)
    except: pass

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except: pass

from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
SEEN_FILE  = r"G:\Antigravity_Server\dom_mirror_final_seen.json"

bot = telebot.TeleBot(BOT_TOKEN)

# ─── CDP Helpers ────────────────────────────────────────────────────────────

def get_cdp_port():
    ag_pids = set()
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if 'antigravity' in (p.info['name'] or '').lower():
                ag_pids.add(p.info['pid'])
        except: pass
    for c in psutil.net_connections(kind='tcp'):
        try:
            if c.status == 'LISTEN' and c.laddr.ip == '127.0.0.1' and c.pid in ag_pids:
                r = urllib.request.urlopen(f"http://127.0.0.1:{c.laddr.port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    return c.laddr.port
        except: pass
    return None

def get_ws_url(port):
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    pages = json.loads(req.read())
    page = next((t for t in pages if t.get('type') == 'page'), None)
    return page['webSocketDebuggerUrl'] if page else None

class CDPSession:
    """Persistent CDP WebSocket session with event listener"""
    def __init__(self, ws_url):
        self.ws_url = ws_url
        parsed = urlparse(ws_url)
        self.host = parsed.hostname
        self.port = parsed.port
        self.path = parsed.path
        self.sock = None
        self._id = 1
        self._lock = threading.Lock()
        self._pending = {}  # id -> Event + result
        self._callbacks = {}  # method -> callback
        self._recv_thread = None
        self._connected = False

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(None)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall(
            f"GET {self.path} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode()
        )
        resp = b''
        while b'\r\n\r\n' not in resp:
            resp += self.sock.recv(4096)
        self._connected = True
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _send_frame(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        ln = len(data)
        mk = os.urandom(4)
        h = bytes([0x81, 0x80 | (ln if ln < 126 else (126 if ln < 65536 else 127))])
        if ln >= 126 and ln < 65536:
            h += struct.pack('>H', ln)
        elif ln >= 65536:
            h += struct.pack('>Q', ln)
        h += mk
        with self._lock:
            self.sock.sendall(h + bytes(b ^ mk[i % 4] for i, b in enumerate(data)))

    def send_cmd(self, method, params=None, wait=True, timeout=10):
        with self._lock:
            cmd_id = self._id
            self._id += 1
        evt = threading.Event()
        self._pending[cmd_id] = [evt, None]
        self._send_frame(json.dumps({'id': cmd_id, 'method': method, 'params': params or {}}))
        if wait:
            evt.wait(timeout)
            return self._pending.pop(cmd_id, [None, None])[1]
        return cmd_id

    def on(self, method, callback):
        self._callbacks[method] = callback

    def _recv_loop(self):
        buf = b''
        while self._connected:
            try:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                buf += chunk
                while len(buf) >= 2:
                    b1 = buf[1] & 0x7F
                    hlen = 2
                    if b1 == 126:
                        if len(buf) < 4: break
                        ln = struct.unpack('>H', buf[2:4])[0]; hlen = 4
                    elif b1 == 127:
                        if len(buf) < 10: break
                        ln = struct.unpack('>Q', buf[2:10])[0]; hlen = 10
                    else:
                        ln = b1
                    total = hlen + ln
                    if len(buf) < total: break
                    frame = buf[hlen:total]; buf = buf[total:]
                    try:
                        msg = json.loads(frame.decode('utf-8'))
                        if 'id' in msg and msg['id'] in self._pending:
                            self._pending[msg['id']][1] = msg.get('result')
                            self._pending[msg['id']][0].set()
                        elif 'method' in msg:
                            cb = self._callbacks.get(msg['method'])
                            if cb:
                                cb(msg.get('params', {}))
                    except: pass
            except: break

    def close(self):
        self._connected = False
        if self.sock:
            try: self.sock.close()
            except: pass


# ─── MutationObserver JS injected into page ─────────────────────────────────

OBSERVER_JS = """
(function() {
    if (window.__agy_mirror_active) return 'ALREADY_ACTIVE';
    window.__agy_mirror_active = true;

    function domToMD(node) {
        if (!node) return "";
        if (node.nodeType === 3) return node.textContent;
        if (node.nodeType !== 1) return "";
        var tag = node.tagName.toLowerCase();
        if (tag === "style" || tag === "script" || tag === "svg") return "";
        var children = Array.from(node.childNodes).map(domToMD).join("");
        if (!children.trim()) return "";
        if (tag === "p") return "\\n" + children.trim();
        if (tag === "h1"||tag==="h2"||tag==="h3"||tag==="h4") return "\\n*" + children.trim() + "*";
        if (tag === "li") return "\\n• " + children.trim();
        if (tag === "ul"||tag==="ol") return children;
        if (tag === "strong"||tag==="b") return "*" + children.trim() + "*";
        if (tag === "em"||tag==="i") return "_" + children.trim() + "_";
        if (tag === "code" && node.parentElement.tagName !== "PRE") return " `" + children.trim() + "` ";
        if (tag === "pre") return "\\n```\\n" + children.trim() + "\\n```";
        if (tag === "br") return "\\n";
        return children;
    }

    function getLatestAI() {
        var containers = document.querySelectorAll('div.leading-relaxed.select-text.text-sm, [class*="prose"]');
        var last = null;
        for (var c of containers) {
            var md = domToMD(c).replace(/\\n{2,}/g, "\\n").trim();
            if (md.length > 10) last = md;
        }
        return last;
    }

    function isBusy() {
        return !!(document.querySelector('.animate-spin') ||
            Array.from(document.querySelectorAll('button')).find(function(b) {
                return b.innerText && b.innerText.includes('Stop');
            }));
    }

    var lastSent = null;
    var debounceTimer = null;

    function emitUpdate() {
        var text = getLatestAI();
        var busy = isBusy();
        var payload = JSON.stringify({text: text, busy: busy});
        if (payload !== lastSent) {
            lastSent = payload;
            window.agy_mirror_update(payload);
        }
    }

    // Debounced emit — fire 500ms after last DOM change
    function onMutation() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(emitUpdate, 500);
    }

    var observer = new MutationObserver(onMutation);
    observer.observe(document.body, {childList: true, subtree: true, characterData: true});

    window.__agy_mirror_observer = observer;
    return 'OBSERVER_STARTED';
})()
"""

# ─── Telegram live edit state ────────────────────────────────────────────────

_live_msg_id = None
_live_last_text = None

def clean_ai_text(text):
    if not text: return ""
    markers = [
        "📌 Catatan Penting", "Catatan Penting", "📋 Task List",
        "Task List — Antigravity", "Dokumen ini mencatat",
        "Rangkuman situasi", "Root cause mirror", "Solusi: dom_mirror",
    ]
    for m in markers:
        if m in text:
            text = text.split(m)[0].strip()
    return text.strip()

def send_or_edit(text, is_final=False):
    global _live_msg_id, _live_last_text
    text = text.strip()[:3800]
    if not text: return
    label = "" if is_final else "⌛ "
    display = label + text
    if display == _live_last_text: return
    _live_last_text = display

    if _live_msg_id:
        try:
            bot.edit_message_text(display, ALLOWED_ID, _live_msg_id, parse_mode="Markdown")
            print(f"[LIVE{'✅' if is_final else '✏️'}] Edited {_live_msg_id}: {text[:50]}")
            if is_final:
                _live_msg_id = None
                _live_last_text = None
            return
        except Exception as e:
            if "message is not modified" in str(e):
                return
            _live_msg_id = None

    try:
        sent = bot.send_message(ALLOWED_ID, display, parse_mode="Markdown")
        if is_final:
            _live_msg_id = None
            _live_last_text = None
        else:
            _live_msg_id = sent.message_id
        print(f"[LIVE SEND] {sent.message_id}: {text[:50]}")
    except Exception:
        try:
            sent = bot.send_message(ALLOWED_ID, display)
            if not is_final:
                _live_msg_id = sent.message_id
        except Exception as e:
            print("[LIVE ERR]", str(e)[:80])

def delete_live():
    global _live_msg_id, _live_last_text
    if _live_msg_id:
        try:
            bot.delete_message(ALLOWED_ID, _live_msg_id)
            print(f"[LIVE DEL] Deleted {_live_msg_id}")
        except: pass
        _live_msg_id = None
        _live_last_text = None

# ─── Main ────────────────────────────────────────────────────────────────────

def run():
    global _live_msg_id, _live_last_text

    while True:
        print("[CDP LIVE] Connecting to Antigravity CDP...")
        port = get_cdp_port()
        if not port:
            print("[CDP LIVE] Antigravity not found, retrying in 5s...")
            time.sleep(5)
            continue

        ws_url = get_ws_url(port)
        if not ws_url:
            print("[CDP LIVE] No page found, retrying...")
            time.sleep(5)
            continue

        cdp = CDPSession(ws_url)
        try:
            cdp.connect()
            print(f"[CDP LIVE] Connected to {ws_url[:60]}")

            # Register binding: JS calls window.agy_mirror_update(payload)
            cdp.send_cmd("Runtime.addBinding", {"name": "agy_mirror_update"})

            # Listen for binding calls
            update_queue = queue.Queue()
            def on_binding(params):
                if params.get('name') == 'agy_mirror_update':
                    update_queue.put(params.get('payload', ''))

            cdp.on("Runtime.bindingCalled", on_binding)
            cdp.send_cmd("Runtime.enable")

            # Inject MutationObserver
            result = cdp.send_cmd("Runtime.evaluate", {
                "expression": OBSERVER_JS,
                "returnByValue": True
            })
            print("[CDP LIVE] Observer:", result)

            last_busy = False

            while True:
                try:
                    payload_str = update_queue.get(timeout=30)
                    payload = json.loads(payload_str)
                    text = payload.get('text')
                    busy = payload.get('busy', False)

                    cleaned = clean_ai_text(text) if text else None

                    if cleaned:
                        if busy:
                            # Still typing — live edit
                            send_or_edit(cleaned, is_final=False)
                        else:
                            # Finished — send final, lock message
                            send_or_edit(cleaned, is_final=True)
                    elif not busy and last_busy:
                        # Text gone after busy — delete live message
                        delete_live()

                    last_busy = busy

                except queue.Empty:
                    # Ping to keep connection alive
                    try:
                        cdp.send_cmd("Runtime.evaluate", {"expression": "1", "returnByValue": True}, wait=False)
                    except:
                        break

        except Exception as e:
            print(f"[CDP LIVE] Session error: {e}. Reconnecting in 5s...")
            try: cdp.close()
            except: pass
            time.sleep(5)

if __name__ == "__main__":
    run()
