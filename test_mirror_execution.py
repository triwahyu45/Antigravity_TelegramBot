import json
import os
import sys

sys.path.append(r"G:\Antigravity_Server\Bot_Scripts")
import transcript_mirror

TRANSCRIPT = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\.system_generated\logs\transcript.jsonl"
OFFSET_FILE = r"G:\Antigravity_Server\mirror_offset.txt"

def test_run():
    offset = transcript_mirror.get_mirror_offset()
    file_size = os.path.getsize(TRANSCRIPT)
    print(f"[TEST RUN] Offset: {offset} | File Size: {file_size}")

    if file_size >= offset:
        with open(TRANSCRIPT, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(offset)
            new_text = f.read()
            lines = new_text.splitlines()
            print(f"[TEST RUN] Lines read after offset #{offset}: {len(lines)}")
            for i, raw in enumerate(lines):
                raw = raw.strip()
                if not raw: continue
                try:
                    d = json.loads(raw)
                    typ = d.get("type", "")
                    status = d.get("status", "")
                    content = (d.get("content") or "").strip()
                    prog = transcript_mirror.format_tool_progress(d)
                    
                    print(f"Line #{i+1} | Step: {d.get('step_index')} | Type: {typ} | Status: {status} | Prog: {bool(prog)} | ContentLen: {len(content)}")
                    
                    if typ == "PLANNER_RESPONSE" and status == "DONE" and content:
                        print(f" -> MATCHED PLANNER_RESPONSE DONE! Head: {repr(content[:60])}")
                        # Try sending to telegram directly
                        res = transcript_mirror.send(transcript_mirror.ALLOWED_ID, f"🤖 *Antigravity*:\n{content}")
                        print(" -> Send Result:", res)
                except Exception as e:
                    print(f"Line #{i+1} Err:", e)

if __name__ == "__main__":
    test_run()
