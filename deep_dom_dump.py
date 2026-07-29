"""
Dump semua elemen text dari DOM Antigravity - cari semua struktur chat
"""
import os, sys, json, socket, struct, base64, urllib.request, psutil
from urllib.parse import urlparse

def find_cdp_port():
    ag_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                ag_pids.add(proc.info['pid'])
        except: pass
    for conn in psutil.net_connections(kind='tcp'):
        try:
            if conn.status == 'LISTEN' and conn.laddr.ip == '127.0.0.1' and conn.pid in ag_pids:
                port = conn.laddr.port
                r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    return port
        except: pass
    return None

def cdp_eval(port, js):
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type')=='page'), None)
    if not ws_url: return None
    path = urlparse(ws_url).path
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", port)); sock.settimeout(8)
    key = base64.b64encode(os.urandom(16)).decode()
    sock.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
    resp = b""
    while b"\r\n\r\n" not in resp: resp += sock.recv(4096)
    payload = json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":js,"returnByValue":True}}).encode()
    ln = len(payload); mk = os.urandom(4)
    hdr = bytes([0x81, 0x80|(ln if ln<126 else 126)])
    if ln >= 126: hdr += struct.pack('>H', ln)
    sock.sendall(hdr + mk + bytes(b ^ mk[i%4] for i,b in enumerate(payload)))
    data = b""
    for _ in range(50):
        try:
            chunk = sock.recv(65536)
            if not chunk: break
            data += chunk
            if len(data) > 2:
                l = data[1] & 0x7F; off = 2
                if l == 126: l = struct.unpack('>H', data[2:4])[0]; off = 4
                elif l == 127: l = struct.unpack('>Q', data[2:10])[0]; off = 10
                if len(data) >= off + l:
                    sock.close()
                    return json.loads(data[off:off+l].decode()).get('result',{}).get('result',{}).get('value')
        except: break
    sock.close()
    return None

port = find_cdp_port()
print("CDP port:", port)
print("Title:", cdp_eval(port, "document.title"))

# Dump semua elemen dengan class dan text - sangat detail
js_dump = """
(function() {
    var results = {
        title: document.title,
        all_divs_with_text: [],
        data_roles: [],
        aria_labels: []
    };
    
    // Cari semua elemen dengan data-* attribute
    var allEls = document.querySelectorAll('[data-role], [data-type], [data-message-id], [data-turn], [class*="message"], [class*="turn"], [class*="chat"]');
    for (var el of allEls) {
        var txt = (el.innerText || '').trim().substring(0, 100);
        results.data_roles.push({
            tag: el.tagName,
            dataRole: el.dataset.role || '',
            dataType: el.dataset.type || '',
            dataMsgId: el.dataset.messageId || '',
            cls: el.className.substring(0, 60),
            txt: txt
        });
    }
    
    // Semua DIV dengan whitespace-pre-wrap (user messages)
    var preWrap = document.querySelectorAll('div.whitespace-pre-wrap');
    for (var el of preWrap) {
        results.all_divs_with_text.push({
            cls: el.className.substring(0, 80),
            txt: (el.innerText || '').trim().substring(0, 200),
            parentCls: el.parentElement ? el.parentElement.className.substring(0, 60) : ''
        });
    }
    
    // Cari AI response blocks - biasanya markdown rendered
    var mdBlocks = document.querySelectorAll('[class*="prose"], [class*="markdown"], [class*="Markdown"]');
    for (var el of mdBlocks) {
        results.aria_labels.push({
            cls: el.className.substring(0, 60),
            txt: (el.innerText || '').trim().substring(0, 300)
        });
    }
    
    return JSON.stringify(results);
})()
"""
result = cdp_eval(port, js_dump)
if result:
    data = json.loads(result)
    print("\n=== DATA ROLES ===")
    for item in data.get('data_roles', [])[:10]:
        print(" ", item)
    print("\n=== WHITESPACE-PRE-WRAP DIVS ===")
    for item in data.get('all_divs_with_text', [])[:10]:
        print(" ", item)
    print("\n=== MARKDOWN BLOCKS ===")
    for item in data.get('aria_labels', [])[:5]:
        print("  cls:", item['cls'])
        print("  txt:", item['txt'][:150])
        print()
else:
    print("CDP eval returned None")
