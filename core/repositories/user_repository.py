import sqlite3
from logs import db


class UserRepository:

    def get_notification_emails(self, cam_id):
        conn = sqlite3.connect(db.DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT email FROM users 
                WHERE notifications_enabled = 1 
                AND (camera_id IS NULL OR camera_id = ?)
            """, (cam_id,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()


    def add_user(self, email, role='user', camera_id=None):
        conn = sqlite3.connect(db.DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, role, camera_id)
                VALUES (?, ?, ?)
            """, (email, role, camera_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Email already exists
            return False
        finally:
            conn.close()


    def delete_user(self, email):
        conn = sqlite3.connect(db.DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM users WHERE email = ?
            """, (email,))
            conn.commit()
        finally:
            conn.close()


    def disable_notifications(self, email):
        conn = sqlite3.connect(db.DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET notifications_enabled = 0 
                WHERE email = ?
            """, (email,))
            conn.commit()
        finally:
            conn.close()


    def enable_notifications(self, email):
        conn = sqlite3.connect(db.DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET notifications_enabled = 1 
                WHERE email = ?
            """, (email,))
            conn.commit()
        finally:
            conn.close()
