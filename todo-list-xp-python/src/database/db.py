import sqlite3
import os

def connect():
    return sqlite3.connect("todo.db")

def db_exists(path="todo.db"):
    return os.path.exists(path)

def init_db():
    with connect() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                done INTEGER DEFAULT 0
            )
        ''')

