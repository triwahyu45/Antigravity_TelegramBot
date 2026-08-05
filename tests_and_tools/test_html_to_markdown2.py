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

js_test = """
(function() {
    function domToMD(node) {
        if (!node) return "";
        if (node.nodeType === 3) return node.textContent;
        if (node.nodeType !== 1) return "";
        var tag = node.tagName.toLowerCase();
        if (tag === "style" || tag === "script" || tag === "svg") return "";
        
        var children = Array.from(node.childNodes).map(domToMD).join("");
        if (!children.trim()) return "";
        
        if (tag === "p") return "\\n\\n" + children.trim() + "\\n\\n";
        if (tag === "h1" || tag === "h2" || tag === "h3" || tag === "h4") return "\\n\\n*" + children.trim() + "*\\n\\n";
        if (tag === "li") return "\\n• " + children.trim();
        if (tag === "ul" || tag === "ol") return "\\n" + children + "\\n";
        if (tag === "strong" || tag === "b") return "*" + children.trim() + "*";
        if (tag === "em" || tag === "i") return "_" + children.trim() + "_";
        if (tag === "code" && node.parentElement.tagName !== "PRE") return " `" + children.trim() + "` ";
        if (tag === "pre") return "\\n\\n```\\n" + children.trim() + "\\n```\\n\\n";
        if (tag === "br") return "\\n";
        return children;
    }
    
    var aiContainers = document.querySelectorAll("div.leading-relaxed.select-text.text-sm");
    var results = [];
    for (var c of aiContainers) {
        var md = domToMD(c).replace(/\\n{3,}/g, "\\n\\n").trim();
        if (md.length > 10) results.push(md);
    }
    return JSON.stringify(results);
})()
"""

res = cdp_send("Runtime.evaluate", {"expression": js_test, "returnByValue": True})
if res and 'result' in res and 'result' in res['result']:
    val = res['result']['result'].get('value')
    if val:
        items = json.loads(val)
        for i, item in enumerate(items[-3:]):
            print(f"=== SAMPLE {i+1} ===")
            print(item[:400])
            print()
