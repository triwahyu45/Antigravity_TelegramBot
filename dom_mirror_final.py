"""
Google Antigravity Telegram Remote Control Bridge
Real-time DOM Response & Progress Mirror Module

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os
import sys

import json
import time
import base64
import struct
import socket
import urllib.request
import psutil
import hashlib
import re
import html
import telebot
from urllib.parse import urlparse, unquote

if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

def md_to_telegram_html(md_text):
    if not md_text: return ""

    code_blocks = []
    def code_block_sub(m):
        code_blocks.append(f"<pre>{html.escape(m.group(1).strip())}</pre>")
        return f"XCODEBLOCKX{len(code_blocks)-1}X"
    
    inline_codes = []
    def inline_code_sub(m):
        inline_codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"XINLINECODEX{len(inline_codes)-1}X"

    text = re.sub(r'```(?:[a-zA-Z]*\n)?(.*?)```', code_block_sub, md_text, flags=re.DOTALL)
    text = re.sub(r'`([^`\n]+)`', inline_code_sub, text)
    text = re.sub(r'^(?:#{1,6})\s+(.+)$', r'\1', text, flags=re.MULTILINE)

    protected_html = []
    def protect_tag(m):
        protected_html.append(m.group(0))
        return f"XTAGX{len(protected_html)-1}X"
    text = re.sub(r'</?(?:b|i|u|s|code|pre|a)[^>]*>', protect_tag, text)

    text = html.escape(text, quote=False)

    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'~([^~]+)~', r'<s>\1</s>', text)
    
    text = re.sub(r'\s*\*\*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*\*$', '', text, flags=re.MULTILINE)

    for i, tag in enumerate(protected_html):
        text = text.replace(f"XTAGX{i}X", tag)
    for i, ic in enumerate(inline_codes):
        text = text.replace(f"XINLINECODEX{i}X", ic)
    for i, cb in enumerate(code_blocks):
        text = text.replace(f"XCODEBLOCKX{i}X", cb)

    return text.strip()


from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
BASE       = r"G:\Antigravity_Server"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def get_port():
    ag_pids = set()
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['name'] and 'antigravity' in p.info['name'].lower():
                ag_pids.add(p.info['pid'])
        except: pass
    if not ag_pids: return None
    for c in psutil.net_connections(kind='tcp'):
        try:
            if c.status=='LISTEN' and c.laddr.ip=='127.0.0.1' and c.pid in ag_pids:
                r = urllib.request.urlopen(f"http://127.0.0.1:{c.laddr.port}/json/version", timeout=1)
                if 'Browser' in json.loads(r.read()):
                    return c.laddr.port
        except: pass
    return None

def cdp(js):
    port = get_port()
    if not port: return None
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3)
        ws_url = next((t['webSocketDebuggerUrl'] for t in json.loads(req.read()) if t.get('type')=='page'), None)
        if not ws_url: return None
        path = urlparse(ws_url).path
        s = socket.socket()
        s.connect(("127.0.0.1", port))
        s.settimeout(3)
        key = base64.b64encode(os.urandom(16)).decode()
        s.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = s.recv(4096)
            if not chunk: break
            resp += chunk
        p2 = json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":js,"returnByValue":True}}).encode()
        ln = len(p2); mk = os.urandom(4)
        h = bytes([0x81, 0x80|(ln if ln<126 else 126)])
        if ln >= 126: h += struct.pack('>H', ln)
        h += mk
        s.sendall(h + bytes(b^mk[i%4] for i,b in enumerate(p2)))
        data = b""
        for _ in range(40):
            chunk = s.recv(65536)
            if not chunk: break
            data += chunk
            if len(data) > 2:
                l = data[1] & 0x7F; off = 2
                if l == 126: l = struct.unpack('>H', data[2:4])[0]; off = 4
                elif l == 127: l = struct.unpack('>Q', data[2:10])[0]; off = 10
                if len(data) >= off + l:
                    raw = data[off:off+l]
                    s.close()
                    return json.loads(raw.decode('utf-8', errors='ignore'))['result']['result']['value']
        s.close()
    except: pass
    return None

JS_SCRAPE = r"""
(function(){
    try {
        var title = document.title || "";
        var msgs = [];
        var inputArea = document.querySelector('[contenteditable="true"]');
        var isBusy = document.querySelector('button[aria-label*="Stop"], button[title*="Stop"], .animate-spin') !== null;

        // 1. SCRAPE USER INPUTS
        var PLACEHOLDER_TEXTS = [
            'ask anything', '@ to mention', '/ for actions', 'queued messages',
            'sends after agent', 'claude sonnet', 'claude opus', 'gemini', 'gpt-',
            'model selection', 'no matching results', 'new conversation',
            'type a message', 'press enter'
        ];
        var userNodes = document.querySelectorAll('div[class*="user-message"], div[class*="user_message"], div.bg-muted, div.rounded-2xl');
        for (var u of userNodes) {
            if (inputArea && inputArea.contains(u)) continue;
            var txt = u.innerText ? u.innerText.trim() : "";
            if (txt.length < 1) continue;
            var txtLow = txt.toLowerCase();
            var isPlaceholder = PLACEHOLDER_TEXTS.some(function(p){ return txtLow.includes(p); });
            if (isPlaceholder) continue;
            if (txt.includes('http://') || txt.includes('https://')) continue;
            if (txt.startsWith('/') || txt.startsWith('status') || txt.startsWith('ss') || txt.startsWith('screenshot') || txt.startsWith('buka') || txt.startsWith('sembunyikan') || txt.startsWith('hide') || txt.startsWith('open')) continue;
            msgs.push({role: 'user', text: txt});
        }

        // 2. SCRAPE TOOL CALL BADGES
        var seenText = new Set();
        var toolBadgeNodes = document.querySelectorAll('div, span, button');
        for (var el of toolBadgeNodes) {
            if (inputArea && inputArea.contains(el)) continue;
            if (el.closest('div.leading-relaxed, [class*="prose"], p')) continue;

            var txt = el.innerText ? el.innerText.replace(/\n+/g, ' ').trim() : '';
            if (!txt || seenText.has(txt) || txt.length < 4 || txt.length > 250) continue;
            var lower = txt.toLowerCase();
            if (lower.startsWith('worked for')) continue;

            if (lower.startsWith('edited') || lower.startsWith('explored') || lower.startsWith('ran') || lower.startsWith('searched') || lower.startsWith('created') || lower.startsWith('running') || lower.startsWith('editing') || lower.startsWith('run')) {
                seenText.add(txt);
                var formatted = '';
                if (lower.startsWith('edited') || lower.startsWith('editing')) formatted = '✏️ *' + txt + '*';
                else if (lower.startsWith('ran') || lower.startsWith('running') || lower.startsWith('run')) formatted = '💻 *' + txt + '*';
                else if (lower.startsWith('searched') || lower.startsWith('explored') || lower.startsWith('searching')) formatted = '🔎 *' + txt + '*';
                else if (lower.startsWith('created') || lower.startsWith('wrote') || lower.startsWith('writing')) formatted = '📝 *' + txt + '*';
                else formatted = '⚙️ *' + txt + '*';


                msgs.push({role: 'progress', text: formatted});
            }
        }

        // 3. FULL RICH MARKDOWN AI RESPONSES
        function domToMD(node) {
            if (!node) return "";
            if (node.nodeType === 3) return node.textContent;
            if (node.nodeType !== 1) return "";
            var tag = node.tagName.toLowerCase();
            if (tag === "style" || tag === "script" || tag === "svg") return "";
            
            var children = Array.from(node.childNodes).map(domToMD).join("");
            if (!children.trim()) return "";
            
            if (tag === "p") return "\n" + children.trim();
            if (tag === "h1" || tag === "h2" || tag === "h3" || tag === "h4") return "\n*" + children.trim() + "*";
            if (tag === "li") return "\n• " + children.trim();
            if (tag === "ul" || tag === "ol") return children;
            if (tag === "tr") return "\n" + children.trim();
            if (tag === "td" || tag === "th") return "  " + children.trim() + "  ";
            if (tag === "table") return "\n" + children.trim() + "\n";
            if (tag === "strong" || tag === "b") return "*" + children.trim() + "*";
            if (tag === "em" || tag === "i") return "_" + children.trim() + "_";
            if (tag === "code" && node.parentElement.tagName !== "PRE") return " `" + children.trim() + "` ";
            if (tag === "pre") return "\n```\n" + children.trim() + "\n```";
            if (tag === "br") return "\n";
            return children;
        }

        var aiContainers = document.querySelectorAll('div.leading-relaxed.select-text.text-sm, [class*="prose"]');
        for (var container of aiContainers) {
            if (container.closest('[contenteditable="true"]')) continue;
            if (inputArea && inputArea.contains(container)) continue;
            var md = domToMD(container).replace(/\n{2,}/g, "\n").trim();
            if (md.length > 10) {
                msgs.push({role: 'ai', text: md});
            }
        }

        // 4. IMAGE EXTRACTION
        var imgEls = document.querySelectorAll('img');
        for (var img of imgEls) {
            if (img.closest('[contenteditable="true"]')) continue;
            if (inputArea && inputArea.contains(img)) continue;
            var src = img.src || img.getAttribute('src') || '';
            if (!src || src.includes('.svg') || src.includes('symbols-icons') || src.startsWith('data:image/')) continue;
            if (src.startsWith('file://') || src.includes('.png') || src.includes('.jpg') || src.includes('.jpeg')) {
                msgs.push({role: 'image', text: src});
            }
        }

        return JSON.stringify({title: title, isBusy: isBusy, msgs: msgs});
    } catch(err) {
        return JSON.stringify({error: err.toString()});
    }
})()
"""

def clean_ai_text(text):
    if not text: return ""
    lines = text.splitlines()
    # Preserve Ran, Edited, Searched, Created progress lines (only filter out internal 'Worked for' timer)
    filtered = [l for l in lines if not l.strip().startswith('Worked for')]
    return "\n".join(filtered).strip()

def msg_key(role, text):
    return hashlib.md5(f"{role}:{text.strip()}".encode('utf-8', errors='ignore')).hexdigest()

SEEN_FILE = os.path.join(BASE, "dom_mirror_seen.json")

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            # Only load user/image hashes from disk, NEVER AI hashes
            loaded = json.load(open(SEEN_FILE, encoding='utf-8'))
            return set([h for h in loaded if not str(h).startswith('ai:')])
        except: pass
    return set()

def save_seen(s):
    try:
        # Only save user/image hashes to disk to prevent AI response block on restart
        user_only = [h for h in s if not str(h).startswith('ai:')]
        json.dump(user_only, open(SEEN_FILE, "w", encoding='utf-8'))
    except: pass

COMPARE_LOG_FILE = os.path.join(BASE, "compare_activity.log")
INJECTED_HASHES_FILE = os.path.join(BASE, "injected_hashes.json")

def log_compare(msg_str):
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(COMPARE_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg_str}\n")
    except: pass

def is_injected_from_telegram(user_text):
    if not user_text: return False
    text_clean = user_text.replace('\r\n', '\n').strip()
    h = hashlib.md5(text_clean.encode('utf-8', errors='replace')).hexdigest()
    
    if os.path.exists(INJECTED_HASHES_FILE):
        try:
            hashes = set(json.load(open(INJECTED_HASHES_FILE, encoding='utf-8')))
            if h in hashes:
                log_compare(f"🔍 [COMPARE MATCH -> SKIP ECHO] (MD5 Match) Text: {text_clean[:50]}")
                return True
        except: pass

    injected_file = os.path.join(BASE, "injected_prompts.txt")
    if os.path.exists(injected_file):
        try:
            lines = [l.strip() for l in open(injected_file, encoding='utf-8', errors='ignore').readlines() if l.strip()]
            for line in lines:
                if line == text_clean or text_clean.startswith(line[:30]):
                    log_compare(f"🔍 [COMPARE MATCH -> SKIP ECHO] (Text Match) Text: {text_clean[:50]}")
                    return True
        except: pass

    log_compare(f"💻 [COMPARE NO MATCH -> SEND You (PC)] (Origin: PC Keyboard) Text: {text_clean[:50]}")
    return False

LAST_TG_MSG_FILE = r"G:\Antigravity_Server\last_tg_user_msg_id.txt"

def get_last_tg_user_msg_id():
    try:
        if os.path.exists(LAST_TG_MSG_FILE):
            c = open(LAST_TG_MSG_FILE, encoding="utf-8").read().strip()
            if c.isdigit():
                return int(c)
    except: pass
    return None

import queue, threading

tg_send_queue = queue.Queue()
recent_sent_cache = {}

def is_duplicate_telegram_msg(raw_text):
    if not raw_text: return True
    clean = re.sub(r'^(✏️|💻|🔎|📝|\*|\s)*(Edited|Editing|Ran|Running|Run|Searched|Searching|Created|Wrote|Writing|\s)*', '', raw_text, flags=re.IGNORECASE).strip().lower()
    if len(clean) < 3: return True
    h = hashlib.md5(clean.encode('utf-8', errors='ignore')).hexdigest()
    now = time.time()
    expired = [k for k, v in recent_sent_cache.items() if now - v > 300]
    for k in expired: del recent_sent_cache[k]
    if h in recent_sent_cache: return True
    recent_sent_cache[h] = now
    return False

def smart_split_markdown(text, max_len=3800):
    if len(text) <= max_len:
        return [text]
    lines = text.splitlines(keepends=True)
    chunks = []
    curr = ""
    for line in lines:
        if len(curr) + len(line) > max_len:
            if curr: chunks.append(curr)
            curr = line
        else:
            curr += line
    if curr: chunks.append(curr)
    return chunks

def _do_send_tg_sync(text, role):
    if not text or len(text.strip()) < 3: return

    if role == 'image':
        src = text.strip()
        try:
            if src.startswith("file://"):
                local_path = unquote(urlparse(src).path)
                if local_path.startswith('/') and os.name == 'nt':
                    local_path = local_path[1:]
                if os.path.exists(local_path):
                    fname = os.path.basename(local_path)
                    with open(local_path, "rb") as f:
                        bot.send_document(ALLOWED_ID, f, caption="🖼️ Gambar dari Chat PC (Original Quality)", visible_file_name=fname)
                        print("[MIRROR PHOTO] Sent local doc (no compress):", local_path)
            elif src.startswith("data:image/"):
                import io
                header, base64_data = src.split(",", 1)
                img_data = base64.b64decode(base64_data)
                ext = header.split("/")[1].split(";")[0] if "/" in header else "png"
                fname = f"screenshot.{ext}"
                bot.send_document(ALLOWED_ID, io.BytesIO(img_data), caption="🖼️ Gambar dari Chat PC (Original Quality)", visible_file_name=fname)
                print("[MIRROR PHOTO] Sent base64 doc (no compress)")
        except Exception as e:
            print("[MIRROR PHOTO ERR]", e)
        return

    clean_text = re.sub(r'\n{3,}', '\n\n', text.strip())

    if role == 'progress':
        full = clean_text
    elif role == 'user':
        full = "You (PC):\n" + clean_text
    else:
        full = clean_text

    reply_id = get_last_tg_user_msg_id() if role == 'ai' else None
    formatted_html = md_to_telegram_html(full)

    for chunk in smart_split_markdown(formatted_html, max_len=3800):
        sent = False
        # Stage 1: Try HTML with reply_id
        if reply_id:
            try:
                bot.send_message(ALLOWED_ID, chunk, parse_mode="HTML", reply_to_message_id=reply_id)
                sent = True
            except Exception as e:
                print("[TG HTML REPLY ERR]", str(e)[:60])
        # Stage 2: Try HTML without reply_id if Stage 1 failed or no reply_id
        if not sent:
            try:
                bot.send_message(ALLOWED_ID, chunk, parse_mode="HTML")
                sent = True
            except Exception as e:
                print("[TG HTML NO-REPLY ERR]", str(e)[:60])
        # Stage 3: Try Plain Text without reply_id if Stage 2 failed
        if not sent:
            try:
                bot.send_message(ALLOWED_ID, chunk, parse_mode=None)
                sent = True
            except Exception as ex:
                print("[TG PLAIN ERR]", str(ex)[:80])

        # Automatic Voice Note Response for AI replies
        if role == 'ai' and sent:
            try:
                import voice_synthesizer
                v_path = voice_synthesizer.generate_voice_note(full)
                if v_path and os.path.exists(v_path):
                    with open(v_path, "rb") as vf:
                        bot.send_voice(ALLOWED_ID, vf, reply_to_message_id=reply_id)
                        print("[MIRROR VOICE] Sent AI Voice Note response to Telegram HP!")
            except Exception as ve:
                print("[MIRROR VOICE ERR]", ve)

        time.sleep(0.1)


def _tg_async_worker():
    print("[TG ASYNC WORKER] Started for non-blocking Telegram IO...")
    while True:
        try:
            item = tg_send_queue.get()
            if not item: continue
            _do_send_tg_sync(item[0], item[1])
            tg_send_queue.task_done()
        except Exception as e:
            print(f"[TG ASYNC ERR] {e}")

threading.Thread(target=_tg_async_worker, daemon=True, name="TgAsyncWorker").start()

def send_tg(text, role):
    if not text or len(text.strip()) < 3: return
    if role in ('progress', 'user') and is_duplicate_telegram_msg(text):
        return
    tg_send_queue.put((text, role))

def run():
    seen = load_seen()
    print(f"[MIRROR FINAL] Started with {len(seen)} seen items (HTML Engine Active)")
    last_title = None

    val = cdp(JS_SCRAPE)
    if val:
        try:
            data = json.loads(val)
            last_title = data.get('title', '')
            for m in data.get('msgs', []):
                if m['role'] in ('user', 'image'):
                    seen.add(msg_key(m['role'], m['text']))
            save_seen(seen)
        except: pass

    was_busy_state = False
    while True:
        try:
            time.sleep(0.5)
            val = cdp(JS_SCRAPE)
            if not val: continue
            data = json.loads(val)
            title = data.get('title', '')
            isBusy = data.get('isBusy', False)

            if was_busy_state and not isBusy:
                send_tg("✅ <b>[SELESAI / FINISHED]</b> AI telah selesai memproses perintah di PC!", "progress")
            was_busy_state = isBusy

            # Always mirror AI responses regardless of window title (MD5 hashes prevent duplicates)
            pass

            if last_title and title != last_title:
                print(f"[MIRROR FINAL] Conversation switched -> '{title}'. Resetting.")
                seen = set()
                for m in data.get('msgs', []):
                    if m['role'] in ('user', 'image'):
                        seen.add(msg_key(m['role'], m['text']))
                save_seen(seen)
            last_title = title

            msgs = data.get('msgs', [])

            for m in msgs:
                if m['role'] == 'ai':
                    cleaned = clean_ai_text(m['text'])
                    if not cleaned or len(cleaned) < 5: continue
                    ai_k = msg_key('ai', cleaned)
                    if ai_k not in seen:
                        if not isBusy:
                            send_tg(cleaned, 'ai')
                            seen.add(ai_k)
                            save_seen(seen)

                elif m['role'] == 'user':
                    uk = msg_key('user', m['text'])
                    if uk not in seen:
                        seen.add(uk)
                        save_seen(seen)
                        # NEVER echo user messages back to Telegram - breaks injection loop!
                        # User messages are already visible in Antigravity on PC.


                elif m['role'] in ('progress', 'image'):
                    k = msg_key(m['role'], m['text'])
                    if k not in seen:
                        # Send progress badges LIVE immediately even while isBusy is True!
                        send_tg(m['text'], m['role'])
                        seen.add(k)
                        save_seen(seen)

        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    run()
