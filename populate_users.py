# populate_users.py
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
from flask import current_app

# Параметры (отредактируй при необходимости)
DB_TYPE = 'postgres'  # или 'sqlite'
if DB_TYPE == 'postgres':
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='anastasia_vitleva_knowledge_base',
        user='anastasia_vitleva_knowledge_base',
        password='123'
    )
    cur = conn.cursor()
else:
    db_path = path.join(path.dirname(path.realpath(__file__)), "database.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

# Создаём 100 пользователей: user1..user100, пароль = pass123
for i in range(1, 101):
    login = f"user{i}"
    name = f"User {i}"
    pwd = generate_password_hash("pass123")
    try:
        if DB_TYPE == 'postgres':
            cur.execute("INSERT INTO users (login, name, password) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                        (login, name, pwd))
        else:
            cur.execute("INSERT OR IGNORE INTO users (login, name, password) VALUES (?, ?, ?);",
                        (login, name, pwd))
    except Exception as e:
        print("err", e)

conn.commit()
cur.close()
conn.close()
print("done")
