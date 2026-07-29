import os,sys,json,socket,struct,base64,urllib.request,psutil
from urllib.parse import urlparse
sys.stdout.reconfigure(encoding='utf-8')

def get_port():
    ag_pids = set()
    for p2 in psutil.process_iter(['pid','name']):
        try:
            if 'antigravity' in (p2.info['name'] or '').lower():
                ag_pids.add(p2.info['pid'])
        except: pass
    for c in psutil.net_connections(kind='tcp'):
        try:
            if c.status=='LISTEN' and c.laddr.ip=='127.0.0.1' and c.pid in ag_pids:
                r=urllib.request.urlopen(f"http://127.0.0.1:{c.laddr.port}/json/version",timeout=1)
                if 'Browser' in json.loads(r.read()):
                    return c.laddr.port
        except: pass
    return None

def cdp(js):
    port = get_port()
    if not port: return None
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type')=='page'), None)
    if not ws_url: return None
    path = urlparse(ws_url).path
    s = socket.socket()
    s.connect(("127.0.0.1", port))
    s.settimeout(6)
    key = base64.b64encode(os.urandom(16)).decode()
    hs = f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    s.sendall(hs.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        resp += s.recv(4096)
    payload_obj = {"id":1,"method":"Runtime.evaluate","params":{"expression":js,"returnByValue":True}}
    p = json.dumps(payload_obj).encode()
    ln = len(p)
    mk = os.urandom(4)
    h = bytes([0x81, 0x80|(ln if ln<126 else 126)])
    if ln >= 126:
        h += struct.pack('>H', ln)
    h += mk
    masked = bytes(b^mk[i%4] for i,b in enumerate(p))
    s.sendall(h + masked)
    data = b""
    for _ in range(30):
        chunk = s.recv(65536)
        if not chunk: break
        data += chunk
        if len(data) > 2:
            l = data[1] & 0x7F
            off = 2
            if l == 126:
                l = struct.unpack('>H', data[2:4])[0]
                off = 4
            elif l == 127:
                l = struct.unpack('>Q', data[2:10])[0]
                off = 10
            if len(data) >= off + l:
                s.close()
                return json.loads(data[off:off+l].decode()).get('result',{}).get('result',{}).get('value')
    s.close()
    return None

# Cek error messages di DOM
print("=== ERROR MESSAGES ===")
val = cdp("JSON.stringify(Array.from(document.querySelectorAll('span.truncate')).map(function(e){return e.innerText.trim();}).filter(function(t){return t.length>0;}))")
if val:
    items = json.loads(val)
    for it in items:
        print(" ", it)

# Cek full text dari semua paragraf di conversation area
print("\n=== ALL PARAGRAPHS IN PAGE ===")
val2 = cdp("JSON.stringify(Array.from(document.querySelectorAll('p')).map(function(e){return e.innerText.trim();}).filter(function(t){return t.length>5;}))")
if val2:
    items2 = json.loads(val2)
    for it in items2[:10]:
        print(" ", it[:100])
