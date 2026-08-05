import os, json

TRANSCRIPT = r'C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\.system_generated\logs\transcript.jsonl'
OFFSET_FILE = r'G:\Antigravity_Server\mirror_offset.txt'

fsize = os.path.getsize(TRANSCRIPT) if os.path.exists(TRANSCRIPT) else -1
offset = int(open(OFFSET_FILE).read().strip()) if os.path.exists(OFFSET_FILE) else -1
print("Transcript size :", fsize, "bytes")
print("Mirror offset   :", offset, "bytes")
print("Unread bytes    :", fsize - offset)

with open(TRANSCRIPT, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
print("Total lines     :", len(lines))
print()
print("=== 3 BARIS TERAKHIR ===")
for line in lines[-3:]:
    try:
        d = json.loads(line.strip())
        typ = d.get("type", "?")
        status = d.get("status", "?")
        clen = len(d.get("content") or "")
        print("  type=" + str(typ) + " status=" + str(status) + " content_len=" + str(clen))
    except Exception as e:
        print("  [parse error]", str(e)[:60])
