"""Test DOM scraper - lihat semua pesan yang terbaca tanpa kirim ke TG"""
import os, sys, json, socket, struct, base64, urllib.request, psutil
from urllib.parse import urlparse

def get_port():
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
                    return conn.laddr.port
        except: pass
    return None

def cdp_eval(js):
    port = get_port()
    if not port: return None
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type')=='page'), None)
    if not ws_url: return None
    path = urlparse(ws_url).path
    s = socket.socket(); s.connect(("127.0.0.1", port)); s.settimeout(8)
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
    for _ in range(50):
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
    return None

# Test 1: user messages
print("=== USER MESSAGES ===")
val = cdp_eval("""JSON.stringify(Array.from(document.querySelectorAll('div.whitespace-pre-wrap.text-sm')).map(e => e.innerText.trim()).filter(t => t.length > 0))""")
if val:
    msgs = json.loads(val)
    for i, m in enumerate(msgs):
        print(f"  [{i}] {m[:80]}")
else:
    print("  (none)")

# Test 2: lihat semua child elements dari main container
print("\n=== MAIN CONTAINER CHILDREN ===")
val2 = cdp_eval("""
(function(){
    var main = document.querySelector('main') || document.querySelector('[class*="overflow-y-auto"]');
    if (!main) return JSON.stringify([{txt: 'no main', cls: ''}]);
    var children = Array.from(main.children);
    return JSON.stringify(children.slice(0, 10).map(c => ({
        tag: c.tagName,
        cls: c.className.substring(0, 60),
        childCount: c.children.length,
        txt: (c.innerText || '').trim().substring(0, 80)
    })));
})()
""")
if val2:
    items = json.loads(val2)
    for item in items:
        print("  ", item)

# Test 3: struktur lebih dalam - cari conversation turns
print("\n=== CONVERSATION TURNS (deep) ===")
val3 = cdp_eval("""
(function(){
    // Cari semua elements yang langsung contain text >20 chars tanpa nested divs dengan text
    var results = [];
    var all = document.querySelectorAll('*');
    var seenTexts = new Set();
    for (var el of all) {
        var directText = Array.from(el.childNodes)
            .filter(n => n.nodeType === 3)
            .map(n => n.textContent.trim())
            .join('');
        if (directText.length > 30 && !seenTexts.has(directText.substring(0,50))) {
            seenTexts.add(directText.substring(0,50));
            results.push({
                tag: el.tagName,
                cls: el.className.substring(0, 50),
                txt: directText.substring(0, 100)
            });
        }
    }
    return JSON.stringify(results.slice(0, 20));
})()
""")
if val3:
    items = json.loads(val3)
    for item in items:
        print("  ", item)
