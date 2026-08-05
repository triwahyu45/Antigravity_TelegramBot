"""Test DOM structure untuk cari selector pesan chat"""
import os, sys, json, socket, struct, base64, urllib.request, psutil

def find_cdp_port():
    ag_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                ag_pids.add(proc.info['pid'])
        except: pass
    for conn in psutil.net_connections(kind='tcp'):
        if conn.status == 'LISTEN' and conn.laddr.ip == '127.0.0.1' and conn.pid in ag_pids:
            port = conn.laddr.port
            try:
                r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    return port
            except: pass
    return None

def raw_ws_eval(port, js_code):
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    ws_url = None
    for t in json.loads(req.read()):
        if t.get('type') == 'page':
            ws_url = t.get('webSocketDebuggerUrl')
            break
    if not ws_url: return None
    from urllib.parse import urlparse
    parsed = urlparse(ws_url)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", port))
    sock.settimeout(5)
    key = base64.b64encode(os.urandom(16)).decode()
    hs = f"GET {parsed.path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    sock.sendall(hs.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        resp += sock.recv(4096)
    payload = json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}}).encode()
    length = len(payload)
    mask_key = os.urandom(4)
    header = bytes([0x81, 0x80 | (length if length < 126 else 126)])
    if length >= 126: header += struct.pack('>H', length)
    header += mask_key
    masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    sock.sendall(header + masked)
    data = b""
    for _ in range(20):
        try:
            chunk = sock.recv(65536)
            if not chunk: break
            data += chunk
            if len(data) > 2:
                ln = data[1] & 0x7F
                off = 2
                if ln == 126: ln = struct.unpack('>H', data[2:4])[0]; off = 4
                if len(data) >= off + ln:
                    sock.close()
                    return json.loads(data[off:off+ln].decode()).get('result', {}).get('result', {}).get('value')
        except: break
    sock.close()
    return None

port = find_cdp_port()
print("CDP port:", port)

# Dump semua elemen dengan teks > 30 chars dari main content area
js = """
(function() {
    var info = {title: document.title, url: location.href};
    var items = [];
    var all = document.querySelectorAll('*');
    for (var el of all) {
        var txt = (el.innerText || '').trim();
        if (txt.length > 30 && el.children.length === 0 && el.offsetParent !== null) {
            items.push({
                tag: el.tagName,
                cls: el.className.substring(0, 60),
                role: el.getAttribute('data-role') || '',
                txt: txt.substring(0, 80)
            });
        }
    }
    info.items = items.slice(0, 20);
    return JSON.stringify(info);
})()
"""
result = raw_ws_eval(port, js)
if result:
    data = json.loads(result)
    print("Title:", data.get('title'))
    print("Items found:", len(data.get('items', [])))
    for item in data.get('items', []):
        print("  <" + item['tag'] + "> role=" + item['role'] + " cls=" + item['cls'][:40] + " | " + item['txt'][:60])
else:
    print("CDP eval returned None")
