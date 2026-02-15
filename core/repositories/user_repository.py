import sqlite3
from logs import db


class UserRepository:

    # CONNECTION
    def _get_connection(self):
        conn = sqlite3.connect(db.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # USER READ OPERATIONS
    def get_all_users(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, role, notifications_enabled
                FROM users
            """)
            users = [dict(row) for row in cursor.fetchall()]

            # attach assigned cameras
            for user in users:
                user["cameras"] = self.get_user_cameras(user["id"])

            return users
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

            if not row:
                return None

            user = dict(row)
            user["cameras"] = self.get_user_cameras(user_id)

            return user
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

            if not row:
                return None

            user = dict(row)
            user["cameras"] = self.get_user_cameras(user["id"])

            return user
        finally:
            conn.close()

    # USER MANAGEMENT
    def delete_user(self, user_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # remove camera mappings first (FK safety)
            cursor.execute("""
                DELETE FROM user_cameras WHERE user_id = ?
            """, (user_id,))

            cursor.execute("""
                DELETE FROM users WHERE id = ?
            """, (user_id,))

            conn.commit()
            return cursor.rowcount > 0
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

    def user_has_camera_access(self, user_id, camera_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM user_cameras
                WHERE user_id = ? AND camera_id = ?
            """, (user_id, camera_id))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    # NOTIFICATIONS
    def get_notification_emails(self, camera_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT u.email
                FROM users u
                LEFT JOIN user_cameras uc ON u.id = uc.user_id
                WHERE u.notifications_enabled = 1
                AND (
                    u.role = 'admin'
                    OR uc.camera_id = ?
                )
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

    def user_has_access_to_camera(self, user_id, camera_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Admin has access to everything
            cursor.execute("""
                SELECT role FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()

            if not row:
                return False

            if row["role"] == "admin":
                return True

            # Check camera assignment
            cursor.execute("""
                SELECT 1 FROM user_cameras
                WHERE user_id = ? AND camera_id = ?
            """, (user_id, camera_id))

            return cursor.fetchone() is not None

        finally:
            conn.close()

