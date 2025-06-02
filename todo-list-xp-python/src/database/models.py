from .db import connect

def add_task(name, category):
    with connect() as conn:
        conn.execute(
            "INSERT INTO tasks (name, category) VALUES (?, ?)",
            (name, category)
        )

def get_tasks_by_category(category):
    with connect() as conn:
        if category:
            cursor = conn.execute(
                "SELECT id, name, done FROM tasks WHERE category = ?",
                (category,)
            )
        else:
            cursor = conn.execute(
                "SELECT id, name, done FROM tasks"
            )
        return cursor.fetchall()

def mark_task_done(task_id):
    with connect() as conn:
        conn.execute(
            "UPDATE tasks SET done = 1 WHERE id = ?",
            (task_id,)
        )

