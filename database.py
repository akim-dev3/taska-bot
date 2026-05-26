import sqlite3
from datetime import datetime

DB_PATH = "tasks.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_task(user_id: int, text: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, text, done, created_at) VALUES (?, ?, 0, ?)",
        (user_id, text, datetime.now().isoformat())
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def get_tasks(user_id: int, done: int = 0) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, text, created_at FROM tasks WHERE user_id = ? AND done = ? ORDER BY id ASC",
        (user_id, done)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def complete_task(user_id: int, task_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ? AND done = 0",
        (task_id, user_id)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_task(user_id: int, task_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def clear_done(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tasks WHERE user_id = ? AND done = 1",
        (user_id,)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected


def get_stats(user_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND done = 0", (user_id,))
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND done = 1", (user_id,))
    completed = cursor.fetchone()[0]
    conn.close()
    return {"pending": pending, "completed": completed}
