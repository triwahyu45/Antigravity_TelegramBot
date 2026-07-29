"""
CDP Raw WebSocket Bypass - Gunakan raw socket untuk koneksi WebSocket
tanpa Origin header sama sekali (biar Electron tidak reject)
"""
import socket
import hashlib
import base64
import struct
import json
import os

CDP_HOST = "127.0.0.1"
CDP_PORT = 61786

def get_ws_url():
    """Dapatkan WebSocket URL dari CDP /json endpoint via HTTP biasa"""
    import urllib.request
    req = urllib.request.urlopen(f"http://{CDP_HOST}:{CDP_PORT}/json", timeout=3)
    targets = json.loads(req.read())
    for t in targets:
        if t.get('type') == 'page':
            return t.get('webSocketDebuggerUrl'), t.get('id')
    return None, None

def raw_ws_connect(host, port, path):
    """Buat koneksi WebSocket raw tanpa Origin header"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.settimeout(5)
    
    key = base64.b64encode(os.urandom(16)).decode()
    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    sock.sendall(handshake.encode())
    response = b""
    while b"\r\n\r\n" not in response:
        response += sock.recv(4096)
    
    first_line = response.decode().split('\r\n')[0]
    print(f"  WS Handshake: {first_line}")
    if "101" not in first_line:
        raise Exception(f"WS handshake failed: {first_line}")
    return sock

def ws_send_json(sock, data):
    """Kirim frame WebSocket text"""
    payload = json.dumps(data).encode()
    length = len(payload)
    mask_key = os.urandom(4)
    
    # Frame header
    header = bytes([0x81])  # FIN + text opcode
    if length < 126:
        header += bytes([0x80 | length])  # MASK bit set
    elif length < 65536:
        header += bytes([0x80 | 126]) + struct.pack('>H', length)
    else:
        header += bytes([0x80 | 127]) + struct.pack('>Q', length)
    
    header += mask_key
    masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    sock.sendall(header + masked)

def ws_recv_json(sock):
    """Terima frame WebSocket"""
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        try:
            # Parse frame sederhana
            if len(data) < 2:
                continue
            opcode = data[0] & 0x0F
            masked = (data[1] & 0x80) != 0
            length = data[1] & 0x7F
            
            offset = 2
            if length == 126:
                length = struct.unpack('>H', data[2:4])[0]
                offset = 4
            elif length == 127:
                length = struct.unpack('>Q', data[2:10])[0]
                offset = 10
            
            if masked:
                mask = data[offset:offset+4]
                offset += 4
            
            if len(data) < offset + length:
                continue  # belum cukup data
            
            payload = data[offset:offset+length]
            if masked:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            
            return json.loads(payload.decode())
        except Exception:
            continue

def cdp_eval_raw(js_code):
    ws_url, page_id = get_ws_url()
    if not ws_url:
        raise Exception("No page target found")
    
    # Parse path dari URL
    path = ws_url.replace(f"ws://{CDP_HOST}:{CDP_PORT}", "")
    print(f"  Connecting to path: {path}")
    
    sock = raw_ws_connect(CDP_HOST, CDP_PORT, path)
    ws_send_json(sock, {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True,
            "awaitPromise": False
        }
    })
    result = ws_recv_json(sock)
    sock.close()
    return result

if __name__ == "__main__":
    print("=== CDP RAW WS BYPASS ===")
    
    # Test sederhana dulu
    js_test = "document.title"
    print("Testing JS eval: document.title")
    result = cdp_eval_raw(js_test)
    print(f"Result: {result}")
    
    if 'result' in result:
        print("\nCDP Raw WS connected! Now injecting click...")
        
        js_click = """
        (function() {
            // Cari Wahyu's PC di sidebar
            var all = document.querySelectorAll('*');
            var wahyu = null;
            for (var el of all) {
                var txt = (el.innerText || el.textContent || '').trim();
                if (txt === "Wahyu's PC" && el.offsetParent !== null) {
                    wahyu = el;
                    break;
                }
            }
            if (wahyu) {
                wahyu.click();
                return 'CLICKED: ' + wahyu.tagName + ' class=' + wahyu.className.substring(0,50);
            }
            // Debug: list semua visible text nodes
            var items = [];
            for (var el of document.querySelectorAll('li, a, button, span, div[role]')) {
                var t = (el.innerText || '').trim();
                if (t && t.length < 60 && t.length > 1 && el.offsetParent !== null) {
                    items.push(t.substring(0,40) + ' [' + el.tagName + ']');
                }
            }
            return 'NOT FOUND. Visible: ' + JSON.stringify([...new Set(items)].slice(0,15));
        })()
        """
        result2 = cdp_eval_raw(js_click)
        val = result2.get('result', {}).get('result', {}).get('value', '')
        print(f"Click result: {val}")
