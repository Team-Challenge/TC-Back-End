"""Creates an empty sqlite db in digital ocean app platform"""

import sqlite3

conn = sqlite3.connect("./data/app.db", isolation_level=None)
conn.execute("VACUUM")
conn.close()
