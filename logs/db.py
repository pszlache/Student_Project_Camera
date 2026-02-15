import sqlite3
import os
from datetime import datetime

DB_PATH = "logs/events.db"


def _get_connection():
    return sqlite3.connect(DB_PATH, timeout=5)


def init_db():

    # MAKE DIR FOR DB IF NEEDED
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                notifications_enabled INTEGER NOT NULL DEFAULT 1
            )
        """)

        # User-Camera permissions (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_cameras (
                user_id INTEGER NOT NULL,
                camera_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, camera_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Login logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                success INTEGER NOT NULL,
                ip_address TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        conn.commit()

    finally:
        conn.close()


def log_presence_start(camera_name):

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        start_time = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO presence_events (camera_name, start_time)
            VALUES (?, ?)
        """, (camera_name, start_time))

        event_id = cursor.lastrowid

        conn.commit()
        return event_id

    except sqlite3.Error as e:
        print(f"[DB] START error: {e}")
        return None

    finally:
        conn.close()


def log_presence_end(event_id, snapshot_path=None):

    if event_id is None:
        return

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        end_time = datetime.now().isoformat()

        cursor.execute("""
            UPDATE presence_events
            SET end_time = ?, snapshot_path = ?
            WHERE id = ?
        """, (end_time, snapshot_path, event_id))

        conn.commit()

    except sqlite3.Error as e:
        print(f"[DB] END error: {e}")

    finally:
        conn.close()

def log_login_attempt(email, success, ip_address=None):

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO login_logs (email, success, ip_address, timestamp)
            VALUES (?, ?, ?, ?)
        """, (email, int(success), ip_address, timestamp))

        conn.commit()

    finally:
        conn.close()


