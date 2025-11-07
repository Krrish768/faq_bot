import sqlite3

conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM faq")
count = cur.fetchone()[0]
print("Total rows in faq:", count)
print("-" * 40)

# Show last 15 rows by id (if id exists)
cur.execute("""
SELECT id, question, answer FROM faq
ORDER BY id DESC
LIMIT 15
""")
rows = cur.fetchall()
for r in rows:
    print(r[0], "-", r[1])
    # print the answer on next line for clarity
    print("   ->", (r[2] or "").replace("\n", " ")[:200])  # short preview
    print()

conn.close()
