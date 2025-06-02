import sqlite3
import os

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'todo.db')

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            category TEXT NOT NULL,
            priority INTEGER DEFAULT 2,
            done BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_task(task, category, priority=2):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('INSERT INTO tasks (task, category, priority) VALUES (?, ?, ?)', 
              (task, category, priority))
    conn.commit()
    conn.close()

def get_tasks_by_category(category=None):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    if category:
        c.execute('''
            SELECT id, task, category, priority, done 
            FROM tasks 
            WHERE category = ? AND done = 0
            ORDER BY priority ASC, created_at DESC
        ''', (category,))
    else:
        c.execute('''
            SELECT id, task, category, priority, done 
            FROM tasks 
            WHERE done = 0
            ORDER BY category, priority ASC, created_at DESC
        ''')
    
    tasks = []
    for row in c.fetchall():
        tasks.append({
            'id': row[0],
            'task': row[1],
            'category': row[2],
            'priority': row[3],
            'done': row[4]
        })
    
    conn.close()
    return tasks

def get_all_categories():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM tasks ORDER BY category')
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories

def mark_task_done(task_id):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('UPDATE tasks SET done = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()