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
    buf=b''
    for _ in range(40):
        chunk=s.recv(65536)
        if not chunk: break
        buf+=chunk
        while len(buf)>=2:
            l=buf[1]&0x7F; hlen=2
            if l==126:
                if len(buf)<4: break
                l=struct.unpack('>H',buf[2:4])[0]; hlen=4
            elif l==127:
                if len(buf)<10: break
                l=struct.unpack('>Q',buf[2:10])[0]; hlen=10
            tot=hlen+l
            if len(buf)<tot: break
            fdata=buf[hlen:tot]; buf=buf[tot:]
            try:
                msg=json.loads(fdata.decode('utf-8'))
                if msg.get('id')==1: s.close(); return msg
            except: pass
    s.close()
    return None

def switch_model_cdp(target_keyword):
    escaped_kw = json.dumps(target_keyword)
    js = f"""
    (async function() {{
        // 1. Find model button
        var modelBtn = Array.from(document.querySelectorAll('button')).find(function(b) {{
            var t = (b.innerText || '').trim();
            return b.className.includes('h-7') && (t.includes('Gemini') || t.includes('Flash') || t.includes('Pro') || t.includes('Claude') || t.includes('GPT'));
        }});
        
        if (!modelBtn) return 'MODEL_BTN_NOT_FOUND';
        var initialModel = modelBtn.innerText.trim();
        
        // Open dropdown
        modelBtn.click();
        await new Promise(r => setTimeout(r, 250));
        
        // Search all visible elements in DOM
        var targetKw = {escaped_kw}.toLowerCase();
        var allEls = Array.from(document.querySelectorAll('div, button, span, li, a'));
        var match = allEls.find(function(el) {{
            if (el.offsetParent === null) return false;
            var t = (el.innerText || el.textContent || '').trim().toLowerCase();
            return t.includes(targetKw) && el !== modelBtn && !modelBtn.contains(el);
        }});
        
        if (match) {{
            match.click();
            await new Promise(r => setTimeout(r, 200));
            return 'OK_SWITCHED_TO_' + match.innerText.trim();
        }}
        
        document.body.click();
        return 'NOT_FOUND_KW:' + targetKw + ' (Current: ' + initialModel + ')';
    }})()
    """
    res = cdp_send("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
    if res and 'result' in res and 'result' in res['result']:
        return res['result']['result'].get('value')
    return 'CDP_ERR'

if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "Pro"
    print(f"Testing model switch to keyword '{kw}'...")
    res = switch_model_cdp(kw)
    print("Switch Result:", res)
