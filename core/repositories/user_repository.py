import sqlite3
from logs import db


class UserRepository:

    # INTERNAL CONNECTION
    def _get_connection(self):
        conn = sqlite3.connect(db.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # READ OPERATIONS
    def get_all_users(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, role, notifications_enabled, camera_id
                FROM users
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()


    def get_user_by_email(self, email):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, role, notifications_enabled, camera_id
                FROM users
                WHERE email = ?
            """, (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


    def get_notification_emails(self, cam_id=None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            if cam_id is None:
                cursor.execute("""
                    SELECT email FROM users
                    WHERE notifications_enabled = 1
                """)
            else:
                cursor.execute("""
                    SELECT email FROM users 
                    WHERE notifications_enabled = 1 
                    AND (camera_id IS NULL OR camera_id = ?)
                """, (cam_id,))

            rows = cursor.fetchall()
            return [row["email"] for row in rows]
        finally:
            conn.close()

    # WRITE OPERATIONS
    def add_user(self, email, role='user', camera_id=None):
        conn = self._get_connection()
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
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM users WHERE email = ?
            """, (email,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


    def disable_notifications(self, email):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET notifications_enabled = 0 
                WHERE email = ?
            """, (email,))
            conn.commit()
            return True
        finally:
            conn.close()


    def enable_notifications(self, email):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET notifications_enabled = 1 
                WHERE email = ?
            """, (email,))
            conn.commit()
            return True
        finally:
            conn.close()