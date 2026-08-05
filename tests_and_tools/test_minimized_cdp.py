import os, sys, json, socket, struct, base64, urllib.request, psutil, ctypes
from urllib.parse import urlparse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

user32 = ctypes.windll.user32

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

def cdp_send(method, params):
    port, ws_url = get_cdp()
    if not ws_url: return None
    path = urlparse(ws_url).path
    s = socket.socket(); s.connect(('127.0.0.1',port)); s.settimeout(6)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
    resp=b''
    while b"\r\n\r\n" not in resp: resp+=s.recv(4096)
    p2=json.dumps({"id":1,"method":method,"params":params}).encode()
    ln=len(p2); mk=os.urandom(4)
    h=bytes([0x81,0x80|(ln if ln<126 else 126)])
    if ln>=126: h+=struct.pack('>H',ln)
    h+=mk; s.sendall(h+bytes(b^mk[i%4] for i,b in enumerate(p2)))
    data=b''
    for _ in range(30):
        chunk=s.recv(65536)
        if not chunk: break
        data+=chunk
        if len(data)>2:
            l=data[1]&0x7F;off=2
            if l==126: l=struct.unpack('>H',data[2:4])[0];off=4
            elif l==127: l=struct.unpack('>Q',data[2:10])[0];off=10
            if len(data)>=off+l:
                s.close()
                return json.loads(data[off:off+l].decode())
    s.close()
    return None

def find_ag_hwnd():
    target_hwnd = []
    def enum_cb(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
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
    return target_hwnd

print("=== TESTING CDP IN MINIMIZED STATE ===")
hwnds = find_ag_hwnd()
print("Found Antigravity HWNDs:", hwnds)

# Test 1: Check CDP before minimizing
res1 = cdp_send("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
print("CDP title before minimize:", res1.get('result',{}).get('result',{}).get('value'))

# Test 2: Minimize window (SW_MINIMIZE = 6)
if hwnds:
    hwnd = hwnds[0][0]
    print(f"Minimizing window HWND {hwnd}...")
    user32.ShowWindow(hwnd, 6) # 6 = SW_MINIMIZE

# Test 3: Check CDP after minimizing
res2 = cdp_send("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
print("CDP title AFTER minimize:", res2.get('result',{}).get('result',{}).get('value'))

# Test 4: Evaluate DOM expression while minimized
js_eval = "document.querySelectorAll('div').length"
res3 = cdp_send("Runtime.evaluate", {"expression": js_eval, "returnByValue": True})
print("CDP DOM query AFTER minimize (div count):", res3.get('result',{}).get('result',{}).get('value'))

print("=== MINIMIZED CDP TEST COMPLETED ===")
