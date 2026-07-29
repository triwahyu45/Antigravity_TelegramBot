import sqlite3
DB = r'C:\Users\Triwahyu45\.gemini\antigravity\conversations\2f289acc-06bd-4e56-b2d3-964240c95268.db'
conn = sqlite3.connect("file:" + DB + "?mode=ro", uri=True, timeout=2)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)
for t in tables:
    cur.execute("PRAGMA table_info(" + t + ")")
    cols = [c[1] for c in cur.fetchall()]
    cur.execute("SELECT COUNT(*) FROM " + t)
    cnt = cur.fetchone()[0]
    print("  [" + t + "] rows=" + str(cnt) + " cols=" + str(cols))

# Sample 2 rows dari tabel terbesar
biggest = max(tables, key=lambda t2: (
    cur.execute("SELECT COUNT(*) FROM " + t2) or cur.fetchone()[0]
))
print("\nSample 2 rows from:", biggest)
cur.execute("SELECT rowid, * FROM " + biggest + " ORDER BY rowid DESC LIMIT 2")
rows = cur.fetchall()
cur.execute("PRAGMA table_info(" + biggest + ")")
cols2 = ['rowid'] + [c[1] for c in cur.fetchall()]
for row in rows:
    print(dict(zip(cols2, row)))
conn.close()
