import sqlite3, json
DB = r'C:\Users\Triwahyu45\.gemini\antigravity\conversations\2f289acc-06bd-4e56-b2d3-964240c95268.db'
conn = sqlite3.connect("file:" + DB + "?mode=ro", uri=True, timeout=2)
cur = conn.cursor()

# Ambil 5 steps terakhir
cur.execute("SELECT rowid, idx, step_type, status, step_payload FROM steps ORDER BY rowid DESC LIMIT 5")
rows = cur.fetchall()
conn.close()

for row in rows:
    rowid, idx, step_type, status, payload = row
    print("rowid=" + str(rowid) + " idx=" + str(idx) + " type=" + str(step_type) + " status=" + str(status))
    if payload:
        try:
            p = json.loads(payload)
            # Cari content/text di dalam payload
            content = p.get('content') or p.get('text') or p.get('message') or ''
            if content:
                print("  content[:200]=" + str(content)[:200])
            else:
                keys = list(p.keys())
                print("  payload keys=" + str(keys))
        except:
            print("  payload[:100]=" + str(payload)[:100])
    print()
