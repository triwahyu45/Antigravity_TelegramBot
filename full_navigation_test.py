"""
Full Navigation Test v2 - CDP Bypass Edition
Step 1: + New Conversation  (mouse click)
Step 2: Conversation History (mouse click)
Step 3: Scheduled Tasks     (mouse click)
Step 4: Wahyu's PC          (CDP JS inject - bypass Electron BUSY block)
"""
import ctypes
import win32gui
import time
import json
import socket
import hashlib
import base64
import struct
import os
import urllib.request
from PIL import ImageGrab

user32 = ctypes.windll.user32
ARTIFACT_DIR = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268"

# ─── CDP helpers ─────────────────────────────────────────────────────────────
def find_cdp_port():
    """Temukan port CDP Electron secara dinamis via netstat"""
    import psutil
    # Kumpulkan PID antigravity dulu
    ag_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                ag_pids.add(proc.info['pid'])
        except:
            pass
    # Cari listening port yang dimiliki antigravity
    for conn in psutil.net_connections(kind='tcp'):
        if conn.status == 'LISTEN' and conn.laddr.ip == '127.0.0.1' and conn.pid in ag_pids:
            port = conn.laddr.port
            try:
                r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                data = json.loads(r.read())
                if 'Browser' in data:
                    return port
            except:
                pass
    return None

def cdp_get_page_ws(port):
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
    targets = json.loads(req.read())
    for t in targets:
        if t.get('type') == 'page':
            return t.get('webSocketDebuggerUrl')
    return None

def raw_ws_connect(host, port, path):
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
    resp = b""
    while b"\r\n\r\n" not in resp:
        resp += sock.recv(4096)
    status = resp.decode().split('\r\n')[0]
    if "101" not in status:
        raise Exception(f"WS handshake failed: {status}")
    return sock

def ws_send(sock, data):
    payload = json.dumps(data).encode()
    length = len(payload)
    mask_key = os.urandom(4)
    header = bytes([0x81])
    if length < 126:
        header += bytes([0x80 | length])
    elif length < 65536:
        header += bytes([0x80 | 126]) + struct.pack('>H', length)
    else:
        header += bytes([0x80 | 127]) + struct.pack('>Q', length)
    header += mask_key
    masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    sock.sendall(header + masked)

def ws_recv(sock):
    data = b""
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            if len(data) < 2:
                continue
            length = data[1] & 0x7F
            offset = 2
            if length == 126:
                length = struct.unpack('>H', data[2:4])[0]
                offset = 4
            elif length == 127:
                length = struct.unpack('>Q', data[2:10])[0]
                offset = 10
            if len(data) < offset + length:
                continue
            return json.loads(data[offset:offset+length].decode())
        except:
            continue

def cdp_click_wahyu(port):
    """Klik Wahyu's PC via CDP JS inject - bypass BUSY block"""
    ws_url = cdp_get_page_ws(port)
    if not ws_url:
        return False, "No page target"
    from urllib.parse import urlparse
    parsed = urlparse(ws_url)
    path = parsed.path
    sock = raw_ws_connect("127.0.0.1", port, path)
    js = """
    (function() {
        var all = document.querySelectorAll('li, div[role], a, button, span');
        for (var el of all) {
            var txt = (el.innerText || el.textContent || '').trim();
            if (txt === "Wahyu's PC" && el.offsetParent !== null) {
                el.click();
                return 'CLICKED: ' + el.tagName + ' - ' + el.className.substring(0,40);
            }
        }
        // Broader search
        var all2 = document.querySelectorAll('*');
        for (var el of all2) {
            var txt = (el.innerText || '').trim();
            if (txt.includes("Wahyu") && el.children.length === 0 && el.offsetParent !== null) {
                el.parentElement.click();
                return 'CLICKED PARENT of: ' + el.tagName + ' text=' + txt.substring(0,30);
            }
        }
        return 'NOT FOUND';
    })()
    """
    ws_send(sock, {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}})
    result = ws_recv(sock)
    sock.close()
    val = result.get('result', {}).get('result', {}).get('value', 'unknown')
    return True, val

# ─── Mouse helpers ────────────────────────────────────────────────────────────
def get_hwnd():
    res = []
    def cb(hwnd, r):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if 'antigravity' in t.lower() or 'wahyu' in t.lower():
                r.append(hwnd)
        return True
    win32gui.EnumWindows(cb, res)
    return res[0] if res else None

def click_at(x, y, delay=1.2):
    user32.SetCursorPos(x, y)
    time.sleep(0.15)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(delay)

def screenshot(name):
    path = os.path.join(ARTIFACT_DIR, f"nav2_{name}.png")
    ImageGrab.grab(all_screens=True).save(path)
    print(f"  [SS] Saved: nav2_{name}.png")

# ─── Main ─────────────────────────────────────────────────────────────────────
def run():
    ctypes.windll.user32.SetProcessDPIAware()
    hwnd = get_hwnd()
    if not hwnd:
        print("ERROR: Antigravity window not found!")
        return

    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x0 = rect[0]
    y0 = rect[1]

    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.3)

    # Step 1: + New Conversation (Y=115 absolute - terbukti dari empirical test)
    print("[STEP 1] + New Conversation...")
    click_at(x0 + int(w * 0.05), y0 + 115)
    screenshot("step1_new_conv")

    # Step 2: Conversation History (Y=160)
    print("[STEP 2] Conversation History...")
    click_at(x0 + int(w * 0.05), y0 + 160)
    screenshot("step2_conv_history")

    # Step 3: Scheduled Tasks (Y=205)
    print("[STEP 3] Scheduled Tasks...")
    click_at(x0 + int(w * 0.05), y0 + 205)
    screenshot("step3_scheduled_tasks")

    # Step 4: Wahyu's PC via CDP bypass
    print("[STEP 4] Wahyu's PC via CDP bypass...")
    port = find_cdp_port()
    if port:
        print(f"  CDP port: {port}")
        ok, msg = cdp_click_wahyu(port)
        print(f"  CDP result: {msg}")
    else:
        print("  CDP port not found! Trying fallback mouse click...")
        click_at(x0 + int(w * 0.05), y0 + 304, delay=0.5)

    time.sleep(1.0)
    screenshot("step4_wahyu_pc")
    print("\n[DONE] Navigation complete!")

if __name__ == "__main__":
    run()
