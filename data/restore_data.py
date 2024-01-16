import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath('.')

old_db_path = os.path.join(basedir, 'data', 'old.db')
new_db_path = os.path.join(basedir, 'data', 'app.db')

conn_old = sqlite3.connect(old_db_path)
cursor_old = conn_old.cursor()

cursor_old.execute('SELECT * FROM users')
users_data_to_transfer = cursor_old.fetchall()

cursor_old.execute('SELECT * FROM security')
security_data_to_transfer = cursor_old.fetchall()

cursor_old.execute('SELECT * FROM delivery_user_info')
delivery_info_data_to_transfer = cursor_old.fetchall()

cursor_old.execute('SELECT * FROM shops')
shops_data_to_transfer = cursor_old.fetchall()

conn_old.close()

conn_new = sqlite3.connect(new_db_path)
cursor_new = conn_new.cursor()

for row in users_data_to_transfer:
    cursor_new.execute('INSERT INTO users (id, full_name, email, joined_at,'
    'is_active,profile_picture, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?)', row)

for row in security_data_to_transfer:
    cursor_new.execute('INSERT INTO security (user_id, password_hash) VALUES (?, ?)', row)

for row in delivery_info_data_to_transfer:
    cursor_new.execute('INSERT INTO delivery_user_info (id, owner_id, post, city,'
    'branch_name, address) VALUES (?, ?, ?, ?, ?, ?)', row)

for row in shops_data_to_transfer:
    cursor_new.execute('INSERT INTO shops (id, owner_id, name, description,'
    'photo_shop,banner_shop, phone_number, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', row)

conn_new.commit()
conn_new.close()
