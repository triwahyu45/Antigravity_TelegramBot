import json
import os

TRANSCRIPT = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\.system_generated\logs\transcript.jsonl"
OFFSET_FILE = r"G:\Antigravity_Server\mirror_offset.txt"

def debug_offsets():
    lines = open(TRANSCRIPT, "rb").readlines()
    print("Total lines in transcript.jsonl:", len(lines))
    print("Current saved offset in mirror_offset.txt:", open(OFFSET_FILE).read().strip() if os.path.exists(OFFSET_FILE) else "None")

    cur_byte = 0
    for i, line_bytes in enumerate(lines):
        line_len = len(line_bytes)
        cur_byte += line_len
        line_str = line_bytes.decode("utf-8", errors="ignore").strip()
        if not line_str: continue
        try:
            d = json.loads(line_str)
            typ = d.get("type", "")
            status = d.get("status", "")
            content = (d.get("content") or "").strip()
            if typ == "PLANNER_RESPONSE" and status == "DONE" and content:
                print(f"Line #{i+1} | EndByte: {cur_byte} | Step: {d.get('step_index')} | Head: {repr(content[:60])}")
        except Exception as e:
            pass

if __name__ == "__main__":
    debug_offsets()
