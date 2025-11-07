import sqlite3

# Connect to database file (or create it)
conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()

# Execute the schema (create tables)
with open('schema.sql', encoding='utf-8') as f:
    cur.executescript(f.read())

# Execute the seed data (insert 120 rows)
with open('seed.sql', encoding='utf-8') as f:
    cur.executescript(f.read())

# Check how many rows were added
cur.execute("SELECT COUNT(*) FROM faq")
print("Number of rows in faq table:", cur.fetchone()[0])

conn.commit()
conn.close()
print("Database created successfully as db.sqlite")
