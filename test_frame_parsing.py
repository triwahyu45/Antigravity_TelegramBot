import os, sys, json, socket, struct, base64, urllib.request, psutil
from urllib.parse import urlparse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

def get_cdp():
    ag_pids = set()
    for p in psutil.process_iter(['pid','name']):
        try:
            if 'antigravity' in (p.info['name'] or '').lower(): ag_pids.add(p.info['pid'])
        except: pass
    port = None
    for c in psutil.net_connections(kind='tcp'):
        try:
            if c.status=='LISTEN' and c.laddr.ip=='127.0.0.1' and c.pid in ag_pids:
                r=urllib.request.urlopen(f"http://127.0.0.1:{c.laddr.port}/json/version",timeout=1)
                if 'Browser' in json.loads(r.read()): port=c.laddr.port; break
        except: pass
    if not port: return None, None
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type')=='page'), None)
    return port, ws_url

def cdp_eval_robust(js, await_promise=False):
    port, ws_url = get_cdp()
    if not ws_url: return None
    path = urlparse(ws_url).path
    s = socket.socket(); s.connect(('127.0.0.1',port)); s.settimeout(6)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
    resp=b''
    while b"\r\n\r\n" not in resp: resp+=s.recv(4096)
    
    params = {"expression": js, "returnByValue": True}
    if await_promise:
        params["awaitPromise"] = True

    p = json.dumps({"id":1,"method":"Runtime.evaluate","params":params}).encode()
    ln = len(p); mk = os.urandom(4)
    h = bytes([0x81, 0x80|(ln if ln<126 else 126)])
    if ln >= 126: h += struct.pack('>H', ln)
    h += mk
    s.sendall(h + bytes(b^mk[i%4] for i,b in enumerate(p)))
    
    # Read WS frames until id == 1 response is found
    buf = b""
    for _ in range(50):
        try:
            chunk = s.recv(65536)
            if not chunk: break
            buf += chunk
            
            # Process frames in buffer
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
                    break # Wait for more bytes
                
                frame_data = buf[head_len:total_frame_len]
                buf = buf[total_frame_len:] # Consume frame from buffer
                
                try:
                    msg = json.loads(frame_data.decode('utf-8'))
                    if msg.get('id') == 1:
                        s.close()
                        return msg.get('result', {}).get('result', {}).get('value')
                except Exception:
                    pass
        except Exception as e:
            print("[RECV ERR]", e)
            break
            
    s.close()
    return None

js_test = """
(async function() {
    var input = document.querySelector('[contenteditable="true"]');
    if (!input) return 'NO_INPUT';
    await new Promise(r => setTimeout(r, 200));
    return 'OK_TEST_PASSED';
})()
"""

res = cdp_eval_robust(js_test, await_promise=True)
print("ROBUST CDP EVAL RESULT:", res)
