import sqlite3
import os
from dotenv import load_dotenv

categories_fixtures = ["на голову", "на вуха", "на шию", "на руки", "аксесуари", "набори"]

load_dotenv()
basedir = os.path.abspath('.')


db_path = os.path.join(basedir, 'data', 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()


for value in categories_fixtures:
    cursor.execute('INSERT INTO categories (category_name) VALUES (?)', (value,))

conn.commit()
conn.close()