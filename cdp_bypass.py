"""
CDP DOM Bypass - Klik Wahyu's PC via JavaScript injection langsung ke Electron DOM.
Bypass 100% semua mouse blocking Electron.
"""
import json
import urllib.request
import websocket
import time

CDP_HOST = "http://127.0.0.1:61786"

def get_targets():
    req = urllib.request.urlopen(f"{CDP_HOST}/json", timeout=3)
    return json.loads(req.read())

def cdp_eval(ws_url, js_code):
    # Gunakan header Origin yang sama dengan yang diharapkan Electron
    ws = websocket.create_connection(
        ws_url,
        timeout=5,
        suppress_origin=True,
        header=["Origin: chrome-extension://antigravity"]
    )
    payload = json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True,
            "awaitPromise": False
        }
    })
    ws.send(payload)
    result = json.loads(ws.recv())
    ws.close()
    return result

def switch_to_wahyu_via_cdp():
    targets = get_targets()
    
    # Ambil ws URL dari page target
    page_ws = None
    for t in targets:
        if t.get('type') == 'page':
            page_ws = t.get('webSocketDebuggerUrl')
            print(f"  Connecting to: {t.get('title')} -> {page_ws}")
            break
    
    if not page_ws:
        print("No page target found!")
        return False

    # JS: cari semua sidebar items, klik yang mengandung "Wahyu"
    js = """
    (function() {
        // Cari semua elemen di sidebar yang bisa diklik
        var allItems = document.querySelectorAll('[class*="conversation"], [class*="sidebar"], [class*="nav-item"], [role="listitem"], [role="treeitem"], li, a, button');
        var wahyuEl = null;
        
        for (var el of allItems) {
            var txt = el.innerText || el.textContent || '';
            if (txt.includes("Wahyu") && !txt.includes("New Conversation") && el.offsetParent !== null) {
                wahyuEl = el;
                break;
            }
        }
        
        if (wahyuEl) {
            var rect = wahyuEl.getBoundingClientRect();
            return JSON.stringify({
                found: true,
                text: wahyuEl.innerText.substring(0, 50),
                tag: wahyuEl.tagName,
                classes: wahyuEl.className.substring(0, 80),
                rect: {top: rect.top, left: rect.left, width: rect.width, height: rect.height}
            });
        }
        
        // Fallback: dump semua item teks di sidebar untuk debug
        var sidebar = document.querySelector('nav, [class*="sidebar"], aside');
        var items = [];
        if (sidebar) {
            var els = sidebar.querySelectorAll('*');
            for (var e of els) {
                var t = (e.innerText || '').trim();
                if (t && t.length < 50 && e.children.length === 0) {
                    items.push({tag: e.tagName, text: t, cls: e.className.substring(0,40)});
                }
            }
        }
        return JSON.stringify({found: false, items: items.slice(0,20)});
    })()
    """
    
    print("Injecting JS to find Wahyu's PC element...")
    result = cdp_eval(page_ws, js)
    
    if 'result' in result and 'result' in result['result']:
        val = result['result']['result'].get('value', '')
        data = json.loads(val)
        print(f"Result: {json.dumps(data, indent=2)}")
        
        if data.get('found'):
            # Klik elemen
            js_click = """
            (function() {
                var allItems = document.querySelectorAll('[class*="conversation"], [class*="sidebar"], [class*="nav-item"], [role="listitem"], [role="treeitem"], li, a, button');
                for (var el of allItems) {
                    var txt = el.innerText || el.textContent || '';
                    if (txt.includes("Wahyu") && !txt.includes("New Conversation") && el.offsetParent !== null) {
                        el.click();
                        return 'CLICKED: ' + el.tagName + ' - ' + txt.substring(0,30);
                    }
                }
                return 'NOT FOUND';
            })()
            """
            click_result = cdp_eval(page_ws, js_click)
            print(f"Click result: {click_result}")
            return True
        else:
            print("Element not found. Sidebar items:")
            for item in data.get('items', []):
                print(f"  <{item['tag']}> '{item['text']}' cls={item['cls']}")
    else:
        print(f"Unexpected result: {result}")
    return False

if __name__ == "__main__":
    print("=== CDP DOM BYPASS ===")
    ok = switch_to_wahyu_via_cdp()
    print(f"\nBypass result: {'SUCCESS' if ok else 'FAILED'}")
