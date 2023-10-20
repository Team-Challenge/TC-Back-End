"""Creates an empty sqlite db in digital ocean app platform"""

import os
import sqlite3


basedir = os.path.abspath('.')
conn = sqlite3.connect(os.path.join(basedir, 'data', 'app.db'), isolation_level=None)
conn.execute("VACUUM")
conn.close()
