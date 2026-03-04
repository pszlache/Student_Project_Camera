import sqlite3
import os
from datetime import datetime

# ================= DB CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "events.db")


def _get_connection():
    return sqlite3.connect(DB_PATH, timeout=5)


# ================= INIT DATABASE =================

def init_db():

    # MAKE DIR FOR DB IF NEEDED
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        # ================= USERS =================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                notifications_enabled INTEGER NOT NULL DEFAULT 1
            )
        """)

        # ================= USER-CAMERA PERMISSIONS =================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_cameras (
                user_id INTEGER NOT NULL,
                camera_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, camera_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ================= LOGIN LOGS =================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                ip_address TEXT,
                success INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        # ================= PRESENCE EVENTS =================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presence_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                snapshot_path TEXT
            )
        """)

        conn.commit()

    finally:
        conn.close()


# ================= PRESENCE START =================

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


# ================= PRESENCE END =================

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


# ================= LOGIN ATTEMPTS =================

def log_login_attempt(email, ip_address, success):

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO login_logs (email, ip_address, success, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            email,
            ip_address,
            1 if success else 0,
            datetime.now().isoformat()
        ))

        conn.commit()

    finally:
        conn.close()


