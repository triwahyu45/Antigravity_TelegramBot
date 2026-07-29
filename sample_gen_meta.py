import sqlite3, json
DB = r'C:\Users\Triwahyu45\.gemini\antigravity\conversations\2f289acc-06bd-4e56-b2d3-964240c95268.db'
conn = sqlite3.connect("file:" + DB + "?mode=ro", uri=True, timeout=2)
cur = conn.cursor()

# Coba gen_metadata - mungkin JSON
cur.execute("SELECT rowid, idx, data FROM gen_metadata ORDER BY rowid DESC LIMIT 3")
rows = cur.fetchall()
conn.close()

print("=== gen_metadata sample ===")
for row in rows:
    rowid, idx, data = row
    print("rowid=" + str(rowid) + " idx=" + str(idx))
    if data:
        if isinstance(data, bytes):
            # Coba decode sebagai UTF-8
            try:
                txt = data.decode('utf-8', errors='replace')
                print("  data[:300]=" + txt[:300])
            except:
                print("  data[:100] (hex)=" + data[:50].hex())
        else:
            try:
                p = json.loads(data)
                print("  json keys=" + str(list(p.keys())))
                # Cari content
                for k in ['content', 'text', 'message', 'response']:
                    if k in p:
                        print("  " + k + "[:200]=" + str(p[k])[:200])
            except:
                print("  data[:300]=" + str(data)[:300])
    print()
