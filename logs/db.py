import sqlite3
from datetime import datetime

DB_PATH = "logs/events.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS presence_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_name TEXT,
            start_time TEXT,
            end_time TEXT,
            snapshot_path TEXT
        )
    """)

    conn.commit()
    conn.close()

def log_presence_start(camera_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    start_time = datetime.now().isoformat()

    c.execute("""
        INSERT INTO presence_events (camera_name, start_time)
        VALUES (?, ?)
    """, (camera_name, start_time))

    event_id = c.lastrowid

    conn.commit()
    conn.close()

    return event_id

def log_presence_end(event_id, snapshot_path=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    end_time = datetime.now().isoformat()

    c.execute("""
        UPDATE presence_events
        SET end_time = ?, snapshot_path = ?
        WHERE id = ?    
    """, (end_time, snapshot_path, event_id))

    conn.commit()
    conn.close()