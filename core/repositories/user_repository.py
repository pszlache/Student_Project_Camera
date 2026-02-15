import sqlite3
from logs import db


class UserRepository:

    def _get_connection(self):
        conn = sqlite3.connect(db.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # BASIC USER READ
    def get_all_users(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, role, notifications_enabled
                FROM users
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, role, notifications_enabled
                FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_user_by_email(self, email):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, role, notifications_enabled
                FROM users WHERE email = ?
            """, (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # CAMERA PERMISSIONS
    def assign_camera(self, user_id, camera_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO user_cameras (user_id, camera_id)
                VALUES (?, ?)
            """, (user_id, camera_id))
            conn.commit()
        finally:
            conn.close()

    def remove_camera(self, user_id, camera_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM user_cameras
                WHERE user_id = ? AND camera_id = ?
            """, (user_id, camera_id))
            conn.commit()
        finally:
            conn.close()

    def get_user_cameras(self, user_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT camera_id FROM user_cameras
                WHERE user_id = ?
            """, (user_id,))
            return [row["camera_id"] for row in cursor.fetchall()]
        finally:
            conn.close()

    # NOTIFICATIONS
    def get_notification_emails(self, camera_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.email
                FROM users u
                JOIN user_cameras uc ON u.id = uc.user_id
                WHERE u.notifications_enabled = 1
                AND uc.camera_id = ?
            """, (camera_id,))
            return [row["email"] for row in cursor.fetchall()]
        finally:
            conn.close()

    def enable_notifications(self, user_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET notifications_enabled = 1
                WHERE id = ?
            """, (user_id,))
            conn.commit()
        finally:
            conn.close()

    def disable_notifications(self, user_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET notifications_enabled = 0
                WHERE id = ?
            """, (user_id,))
            conn.commit()
        finally:
            conn.close()
