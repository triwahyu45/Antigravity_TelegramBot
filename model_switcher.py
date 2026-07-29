"""
model_switcher.py - Automated AI Model Switcher via CDP (Popover Filtered)
"""
import os, sys, time, json, socket, struct, base64
import urllib.request
from urllib.parse import urlparse
import psutil

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except: pass

_cdp_port_cache = None

def _get_cdp_port():
    global _cdp_port_cache
    if _cdp_port_cache:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{_cdp_port_cache}/json/version", timeout=1)
            return _cdp_port_cache
        except:
            _cdp_port_cache = None
    ag_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                ag_pids.add(proc.info['pid'])
        except: pass
    for conn in psutil.net_connections(kind='tcp'):
        try:
            if conn.status == 'LISTEN' and conn.laddr.ip == '127.0.0.1' and conn.pid in ag_pids:
                r = urllib.request.urlopen(f"http://127.0.0.1:{conn.laddr.port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    _cdp_port_cache = conn.laddr.port
                    return _cdp_port_cache
        except: pass
    return None

def _cdp_eval(js, await_promise=False):
    port = _get_cdp_port()
    if not port: return None
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
        ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type') == 'page'), None)
        if not ws_url: return None
        path = urlparse(ws_url).path
        s = socket.socket()
        s.connect(("127.0.0.1", port))
        s.settimeout(6)
        key = base64.b64encode(os.urandom(16)).decode()
        s.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
        resp = b""
        while b"\r\n\r\n" not in resp: resp += s.recv(4096)
        
        params = {"expression": js, "returnByValue": True}
        if await_promise:
            params["awaitPromise"] = True

        p = json.dumps({"id":1,"method":"Runtime.evaluate","params":params}).encode()
        ln = len(p); mk = os.urandom(4)
        h = bytes([0x81, 0x80|(ln if ln<126 else 126)])
        if ln >= 126: h += struct.pack('>H', ln)
        h += mk
        s.sendall(h + bytes(b^mk[i%4] for i,b in enumerate(p)))
        
        buf = b""
        for _ in range(40):
            try:
                chunk = s.recv(65536)
                if not chunk: break
                buf += chunk
                while len(buf) >= 2:
                    payload_len = buf[1] & 0x7F; head_len = 2
                    if payload_len == 126:
                        if len(buf) < 4: break
                        payload_len = struct.unpack('>H', buf[2:4])[0]; head_len = 4
                    elif payload_len == 127:
                        if len(buf) < 10: break
                        payload_len = struct.unpack('>Q', buf[2:10])[0]; head_len = 10
                    tot = head_len + payload_len
                    if len(buf) < tot: break
                    fdata = buf[head_len:tot]; buf = buf[tot:]
                    try:
                        msg = json.loads(fdata.decode('utf-8'))
                        if msg.get('id') == 1: s.close(); return msg.get('result', {}).get('result', {}).get('value')
                    except: pass
            except: break
        s.close()
    except Exception as e:
        print("[CDP ERR]", e)
    return None

def switch_model(target_model_name):
    """Switch AI model via CDP DOM automation excluding chat prose."""
    escaped_kw = json.dumps(target_model_name)
    js = f"""
    (async function() {{
        var modelBtn = Array.from(document.querySelectorAll('button')).find(function(b) {{
            var t = (b.innerText || '').trim();
            return b.className.includes('h-7') && (t.includes('Gemini') || t.includes('Flash') || t.includes('Pro') || t.includes('Claude') || t.includes('GPT'));
        }});
        
        if (!modelBtn) return 'MODEL_BTN_NOT_FOUND';
        var beforeModel = modelBtn.innerText.trim();
        
        modelBtn.click();
        await new Promise(r => setTimeout(r, 400));
        
        var kw = {escaped_kw}.toLowerCase();
        
        var allSpans = Array.from(document.querySelectorAll('span, button, div'));
        var match = allSpans.find(function(el) {{
            if (el.closest('.prose') || el.closest('div.leading-relaxed') || el.closest('[contenteditable="true"]')) return false;
            if (el === modelBtn || modelBtn.contains(el)) return false;
            var t = (el.innerText || el.textContent || '').trim().toLowerCase();
            return t.includes(kw) && t.length < 50;
        }});
        
        if (match) {{
            var clickedName = match.innerText.trim();
            match.click();
            await new Promise(r => setTimeout(r, 500));
            var afterModel = modelBtn.innerText.trim();
            return 'OK:' + afterModel;
        }}
        
        document.body.click();
        return 'NOT_FOUND:' + kw + ' (Current: ' + beforeModel + ')';
    }})()
    """
    res = _cdp_eval(js, await_promise=True)
    return res

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Flash"
    print(f"Switching model to '{target}'...")
    res = switch_model(target)
    print("Result:", res)
