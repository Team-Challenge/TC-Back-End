"""Creates an empty sqlite db in digital ocean app platform"""

import os
import logging
import sqlite3



basedir = os.path.abspath('.')
db_path = os.path.join(basedir, 'data', 'app.db')

if os.path.exists(db_path):
    os.remove(db_path)
    logging.info("existing DB file removed.")

conn = sqlite3.connect(db_path, isolation_level=None)
conn.execute("VACUUM")
conn.close()

logging.info("Vacuum DB file has been created.")
