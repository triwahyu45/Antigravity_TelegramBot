import os, sys, json, socket, struct, base64, urllib.request, psutil
from urllib.parse import urlparse
sys.stdout.reconfigure(encoding='utf-8')

ag_pids = set()
for p in psutil.process_iter(['pid','name']):
    try:
        if 'antigravity' in (p.info['name'] or '').lower(): ag_pids.add(p.info['pid'])
    except: pass

port = None
for c in psutil.net_connections(kind='tcp'):
    try:
        if c.status == 'LISTEN' and c.laddr.ip == '127.0.0.1' and c.pid in ag_pids:
            r = urllib.request.urlopen(f'http://127.0.0.1:{c.laddr.port}/json/version', timeout=1)
            if 'Browser' in json.loads(r.read()):
                port = c.laddr.port
                break
    except: pass

if port:
    req = urllib.request.urlopen(f'http://127.0.0.1:{port}/json', timeout=3)
    ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type') == 'page'), None)
    path = urlparse(ws_url).path
    s = socket.socket()
    s.connect(('127.0.0.1', port))
    s.settimeout(6)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(f'GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
    resp = b''
    while b'\r\n\r\n' not in resp: resp += s.recv(4096)
    
    js = """(function(){
        var inp = document.querySelector('[contenteditable="true"]');
        if (!inp) return 'NO_INPUT';
        inp.focus();
        var rng = document.createRange();
        rng.selectNodeContents(inp);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(rng);
        document.execCommand('delete', false, null);
        return 'CLEARED';
    })()"""
    
    p2 = json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':js,'returnByValue':True}}).encode()
    ln = len(p2); mk = os.urandom(4)
    h = bytes([0x81, 0x80|(ln if ln < 126 else 126)])
    if ln >= 126: h += struct.pack('>H', ln)
    h += mk
    s.sendall(h + bytes(b^mk[i%4] for i, b in enumerate(p2)))
    buf = s.recv(4096)
    s.close()
    print('Editor cleared!')
else:
    print('CDP port not found')
