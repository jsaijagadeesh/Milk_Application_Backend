import sqlite3
con = sqlite3.connect('dairy_app.db')
tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])
cols = con.execute("PRAGMA table_info(addresses)").fetchall()
print('Addresses columns:', [c[1] for c in cols])
con.close()