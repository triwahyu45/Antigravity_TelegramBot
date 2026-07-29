"""
Google Antigravity Telegram Remote Control Bridge
CDP WebSocket Prompt Injection Engine & Native Keyboard Event Dispatcher

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
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
_cdp_port_cache_ts = 0

def _get_cdp_port():
    global _cdp_port_cache, _cdp_port_cache_ts
    # Return cached port if still valid (30s TTL) and still listening
    if _cdp_port_cache and (time.time() - _cdp_port_cache_ts) < 30:
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
                    _cdp_port_cache_ts = time.time()
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
        
        # Buffer loop for robust WebSocket frame decoding
        buf = b""
        for _ in range(50):
            try:
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
                    
                    total_frame_len = head_len + payload_len
                    if len(buf) < total_frame_len:
                        break
                    
                    frame_data = buf[head_len:total_frame_len]
                    buf = buf[total_frame_len:]
                    
                    try:
                        msg = json.loads(frame_data.decode('utf-8'))
                        if msg.get('id') == 1:
                            s.close()
                            return msg.get('result', {}).get('result', {}).get('value')
                    except Exception:
                        pass
            except Exception:
                break

        s.close()
    except Exception as e:
        print("[CDP ERR]", e)
    return None

def cdp_click_wahyu():
    """Klik Wahyu's PC via CDP DOM - zero koordinat"""
    js = """
    (function() {
        var all = document.querySelectorAll('li, div, a, button, span');
        for (var el of all) {
            var txt = (el.innerText || el.textContent || '').trim();
            if (txt === "Wahyu's PC") {
                el.click();
                return 'OK:' + el.tagName;
            }
        }
        return 'ALREADY_ACTIVE';
    })()
    """
    res = _cdp_eval(js)
    return res

def cdp_inject_and_submit(text):
    """Injeksi teks multiline & submit instan — pakai Shift+Enter KeyboardEvent untuk Lexical editor"""
    escaped_text = json.dumps(text)
    js = f"""
    (async function() {{
        var input = document.querySelector('[contenteditable="true"]');
        if (!input) return 'NO_INPUT';
        
        input.focus();
        
        // Select all & delete existing content
        var range = document.createRange();
        range.selectNodeContents(input);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        document.execCommand('delete', false, null);
        
        // Insert text line-by-line with Shift+Enter for newlines (Lexical-compatible)
        var fullText = {escaped_text};
        var lines = fullText.split('\\n');
        for (var i = 0; i < lines.length; i++) {{
            if (i > 0) {{
                input.dispatchEvent(new KeyboardEvent('keydown',  {{key:'Enter',code:'Enter',keyCode:13,which:13,shiftKey:true,bubbles:true}}));
                input.dispatchEvent(new KeyboardEvent('keypress', {{key:'Enter',code:'Enter',keyCode:13,which:13,shiftKey:true,bubbles:true}}));
                input.dispatchEvent(new KeyboardEvent('keyup',    {{key:'Enter',code:'Enter',keyCode:13,which:13,shiftKey:true,bubbles:true}}));
            }}
            if (lines[i].length > 0) {{
                document.execCommand('insertText', false, lines[i]);
            }}
        }}
        
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        
        // Fast dynamic polling for Send button re-render (< 20ms execution latency)
        var t0 = Date.now();
        while (Date.now() - t0 < 300) {{
            var sendBtn = document.querySelector('button[aria-label="Send message"]') ||
                          document.querySelector('button[aria-label*="Send"]') ||
                          document.querySelector('button[type="submit"]');
            if (sendBtn && !sendBtn.disabled) {{
                sendBtn.click();
                return 'OK_SUBMITTED';
            }}
            await new Promise(r => setTimeout(r, 10));
        }}
        
        // Backup Enter key if Send button not found
        input.dispatchEvent(new KeyboardEvent('keydown', {{key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true}}));
        return 'OK_TEXT_ONLY';
    }})()
    """
    res = _cdp_eval(js, await_promise=True)
    print("[INJECT] cdp_inject_and_submit result:", res)
    return res

def cdp_send_native_enter():
    """Send native Enter key via CDP WebSocket Input.dispatchKeyEvent (Lexical & React compatible)"""
    port = _get_cdp_port()
    if not port: return False
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
        targets = json.loads(req.read())
        ws_url = next((t['webSocketDebuggerUrl'] for t in targets if t.get('type') == 'page'), None)
        if not ws_url: return False
        
        parsed = urlparse(ws_url)
        host = parsed.hostname; p_port = parsed.port; path = parsed.path
        
        s = socket.socket()
        s.connect((host, p_port))
        s.settimeout(4)
        key = base64.b64encode(os.urandom(16)).decode()
        req_str = f"GET {path} HTTP/1.1\r\nHost: {host}:{p_port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        s.sendall(req_str.encode())
        resp = b""
        while b"\r\n\r\n" not in resp: resp += s.recv(4096)
        
        def send_frame(msg_dict):
            p2 = json.dumps(msg_dict).encode()
            ln = len(p2); mk = os.urandom(4)
            h = bytes([0x81, 0x80|(ln if ln<126 else 126)])
            if ln >= 126: h += struct.pack('>H', ln)
            h += mk
            s.sendall(h + bytes(b^mk[i%4] for i,b in enumerate(p2)))

        # Send Enter KeyDown & KeyUp
        send_frame({
            "id": 1,
            "method": "Input.dispatchKeyEvent",
            "params": {
                "type": "keyDown",
                "key": "Enter",
                "code": "Enter",
                "windowsVirtualKeyCode": 13,
                "nativeVirtualKeyCode": 13,
                "text": "\r"
            }
        })
        time.sleep(0.05)
        send_frame({
            "id": 2,
            "method": "Input.dispatchKeyEvent",
            "params": {
                "type": "keyUp",
                "key": "Enter",
                "code": "Enter",
                "windowsVirtualKeyCode": 13,
                "nativeVirtualKeyCode": 13
            }
        })
        s.close()
        return True
    except Exception as e:
        print("[CDP NATIVE ENTER ERR]", e)
        return False

def inject_text_to_antigravity(text):
    """Suntikkan teks ke Antigravity via Pure CDP DOM & Native Enter Fallback."""
    if not text or not text.strip():
        return True
    
    for attempt in range(2):
        try:
            try: cdp_click_wahyu()
            except: pass
            time.sleep(0.1)

            res = cdp_inject_and_submit(text)
            if res == 'OK_SUBMITTED':
                return True
            elif res == 'OK_TEXT_ONLY' or res is None:
                # Send button not found (e.g. agent is working/busy) -> Fire Native CDP Enter key!
                print("[INJECT] Send button not found, firing Native CDP Enter key...")
                cdp_send_native_enter()
                return True
            time.sleep(0.3)
        except Exception as e:
            print(f"[INJECT ERR attempt {attempt+1}]", e)

    return True

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Tes single-shot submit dari CDP"
    print("Testing single-shot CDP injection:", msg)
    ok = inject_text_to_antigravity(msg)
    print("Result:", ok)

