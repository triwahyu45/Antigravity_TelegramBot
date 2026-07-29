"""Find the correct input element selector in Antigravity"""
import os, sys, json, socket, struct, base64, urllib.request, psutil
from urllib.parse import urlparse
sys.stdout.reconfigure(encoding='utf-8')

def cdp_eval(js):
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
    if not port: return None
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type')=='page'), None)
    if not ws_url: return None
    path = urlparse(ws_url).path
    s = socket.socket(); s.connect(("127.0.0.1",port)); s.settimeout(6)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
    resp=b""
    while b"\r\n\r\n" not in resp: resp+=s.recv(4096)
    p2=json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":js,"returnByValue":True}}).encode()
    ln=len(p2); mk=os.urandom(4)
    h=bytes([0x81,0x80|(ln if ln<126 else 126)])
    if ln>=126: h+=struct.pack('>H',ln)
    h+=mk; s.sendall(h+bytes(b^mk[i%4] for i,b in enumerate(p2)))
    data=b""
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
                return json.loads(data[off:off+l].decode()).get('result',{}).get('result',{}).get('value')
    s.close()
    return None

# Cari input elements
result = cdp_eval("""JSON.stringify(Array.from(document.querySelectorAll('textarea, [contenteditable], input')).map(function(el){
    return {
        tag: el.tagName,
        type: el.type || '',
        contenteditable: el.getAttribute('contenteditable'),
        placeholder: el.getAttribute('placeholder') || '',
        cls: el.className.substring(0,60),
        visible: el.offsetParent !== null,
        value: (el.value || el.textContent || '').substring(0,30)
    };
}))""")

if result:
    items = json.loads(result)
    print("Found", len(items), "input elements:")
    for it in items:
        print(" ", it)
else:
    print("No result from CDP")
