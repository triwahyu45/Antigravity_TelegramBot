"""
Node 2: Dedicated Transcript Mirror & Live Progress Worker
Membaca transcript.jsonl dan mengirimkan balasan PC, input user PC, dan live progress ke Telegram.
"""
import os
import sys
import time
import json
import re
import glob
import telebot

# Force UTF-8 encoding for Windows Console to prevent charmap emoji crashes
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
BASE            = r"G:\Antigravity_Server"
TRANSCRIPT      = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\.system_generated\logs\transcript.jsonl"
MIRROR_OFFSET   = os.path.join(BASE, "mirror_offset.txt")
RECEIVED        = os.path.join(BASE, "Received_Files")

bot = telebot.TeleBot(BOT_TOKEN)

def format_for_telegram(text):
    if not text: return ""
    t = str(text)
    t = re.sub(r'\*\*(.*?)\*\*', r'*\1*', t)
    t = re.sub(r'^#{1,6}\s*(.+)$', r'*\1*', t, flags=re.MULTILINE)
    t = re.sub(r'^\s*[\-\*]\s+', r'• ', t, flags=re.MULTILINE)
    return t

def send(chat_id, text):
    if not text: return
    formatted_text = format_for_telegram(str(text).strip())
    
    lines = formatted_text.splitlines()
    chunks = []
    curr = ""
    for line in lines:
        if len(curr) + len(line) + 1 > 3500:
            if curr: chunks.append(curr)
            curr = line
        else:
            curr = curr + "\n" + line if curr else line
    if curr: chunks.append(curr)

    for chunk in chunks:
        try:
            bot.send_message(chat_id, chunk, parse_mode="Markdown")
        except Exception as e1:
            plain_text = re.sub(r'[\*\_\`#]', '', chunk)
            try:
                bot.send_message(chat_id, plain_text, parse_mode=None)
            except Exception as e2:
                try:
                    print(f"[MIRROR SEND ERR] {e2}")
                except Exception:
                    pass

def get_mirror_offset():
    if os.path.exists(MIRROR_OFFSET):
        try:
            return int(open(MIRROR_OFFSET).read().strip())
        except Exception:
            pass
    if os.path.exists(TRANSCRIPT):
        try:
            return os.path.getsize(TRANSCRIPT)
        except Exception:
            pass
    return 0

def save_mirror_offset(n):
    try:
        with open(MIRROR_OFFSET, "w") as f:
            f.write(str(n))
    except Exception:
        pass

def format_tool_progress(d):
    typ = d.get("type", "").upper()
    msgs = []
    
    tool_calls = d.get("tool_calls", [])
    if tool_calls:
        for tc in tool_calls:
            name = tc.get("name", "")
            args = tc.get("args", {})
            t_summary = args.get("toolSummary") or args.get("toolAction")
            
            if name in ["replace_file_content", "multi_replace_file_content", "write_to_file"]:
                target = args.get("TargetFile") or ""
                fname = os.path.basename(target) if target else ""
                desc = args.get("Description") or ""
                if desc:
                    msgs.append(f"✏️ *Editing file* `{fname}`: _{desc}_" if fname else f"✏️ *Editing file*: _{desc}_")
                else:
                    msgs.append(f"✏️ *Editing file*: `{fname}`" if fname else "✏️ *Editing file*")
            elif name in ["view_file", "list_dir", "grep_search"]:
                target = args.get("AbsolutePath") or args.get("DirectoryPath") or args.get("SearchPath") or ""
                fname = os.path.basename(target) if target else ""
                msgs.append(f"🔍 *Exploring/Analyzing*: `{fname}`" if fname else "🔍 *Exploring codebase*")
            elif name == "run_command":
                cmd = args.get("CommandLine", "")
                if len(cmd) > 60: cmd = cmd[:60] + "..."
                msgs.append(f"💻 *Running command*: `{cmd}`")
            elif name == "generate_image":
                p = args.get("Prompt", "")
                if len(p) > 60: p = p[:60] + "..."
                msgs.append(f"🎨 *Generating image*: _{p}_")
            elif t_summary:
                msgs.append(f"⚡ *Progress*: _{t_summary}_")

    if typ in ["RUN_COMMAND", "VIEW_FILE", "REPLACE_FILE_CONTENT", "WRITE_TO_FILE", "MULTI_REPLACE_FILE_CONTENT", "GREP_SEARCH", "LIST_DIR"]:
        if typ == "RUN_COMMAND":
            msgs.append("💻 *Command Execution Completed*")
        elif typ in ["REPLACE_FILE_CONTENT", "MULTI_REPLACE_FILE_CONTENT", "WRITE_TO_FILE"]:
            msgs.append("✏️ *File Edit Completed*")
        elif typ in ["VIEW_FILE", "GREP_SEARCH", "LIST_DIR"]:
            msgs.append("🔍 *Code Exploration Completed*")
            
    return "\n".join(msgs) if msgs else None

def mirror_worker():
    offset = get_mirror_offset()
    try:
        print(f"[NODE 2: MIRROR WORKER] Running PID={os.getpid()} from byte offset #{offset}...")
    except Exception:
        pass

    while True:
        try:
            if not os.path.exists(TRANSCRIPT):
                time.sleep(2)
                continue

            file_size = os.path.getsize(TRANSCRIPT)
            if file_size < offset:
                offset = 0
                save_mirror_offset(offset)

            if file_size > offset:
                with open(TRANSCRIPT, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(offset)
                    new_text = f.read()
                    offset = f.tell()
                    save_mirror_offset(offset)

                    for raw in new_text.splitlines():
                        raw = raw.strip()
                        if not raw: continue
                        try:
                            d       = json.loads(raw)
                            typ     = d.get("type","")
                            status  = d.get("status","")
                            content = (d.get("content") or "").strip()

                            # 1. Live Progress Badges
                            progress_msg = format_tool_progress(d)
                            if progress_msg:
                                send(ALLOWED_ID, progress_msg)

                            # 2. Pesan User dari PC
                            if typ == "USER_INPUT" and content:
                                clean = content
                                for tag in ["<USER_REQUEST>","</USER_REQUEST>",
                                            "<ADDITIONAL_METADATA>","</ADDITIONAL_METADATA>"]:
                                    clean = clean.replace(tag, "")
                                clean = "\n".join(
                                    l for l in clean.splitlines()
                                    if not l.strip().startswith("The current local time")
                                    and l.strip()
                                ).strip()
                                if clean:
                                    if not any(k in clean.lower() for k in ["foto baru dari telegram", "received_files", "photo_"]):
                                        send(ALLOWED_ID, f"👤 *Kamu (dari PC)*:\n{clean}")

                            # 3. Balasan AI dari PC
                            elif typ == "PLANNER_RESPONSE" and status == "DONE" and content:
                                if not content.startswith("[Message]") and len(content) > 5:
                                    send(ALLOWED_ID, f"🤖 *Antigravity*:\n{content}")
                        except Exception as e:
                            try:
                                print(f"[MIRROR PARSE ERR] {e}")
                            except Exception:
                                pass
        except Exception as e:
            try:
                print(f"[MIRROR ERR] {e}")
            except Exception:
                pass
        time.sleep(1)

if __name__ == "__main__":
    mirror_worker()
