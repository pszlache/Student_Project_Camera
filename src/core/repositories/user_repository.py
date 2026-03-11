import sqlite3
from logs import db


class UserRepository:

    #CONNECTION
    def _get_connection(self):
        conn = sqlite3.connect(db.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


    #USER READ
    def get_all_users(self):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, email, phone, role, notifications_enabled
                FROM users
            """)

            users = [dict(row) for row in cursor.fetchall()]

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
                SELECT id, email, phone, role, notifications_enabled
                FROM users
                WHERE id = ?
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
                SELECT id, email, phone, role, notifications_enabled
                FROM users
                WHERE email = ?
            """, (email,))

            row = cursor.fetchone()

            if not row:
                return None

            user = dict(row)
            user["cameras"] = self.get_user_cameras(user["id"])

            return user

        finally:
            conn.close()


    #USER MANAGEMENT
    def delete_user_by_id(self, user_id):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM user_cameras
                WHERE user_id = ?
            """, (user_id,))

            cursor.execute("""
                DELETE FROM users
                WHERE id = ?
            """, (user_id,))

            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()


    #CAMERA PERMISSIONS
    def assign_camera(self, user_id, camera_id):

        if camera_id is None:
            return

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


    def remove_all_cameras(self, user_id):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM user_cameras
                WHERE user_id = ?
            """, (user_id,))

            conn.commit()

        finally:
            conn.close()


    def get_user_cameras(self, user_id):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT camera_id
                FROM user_cameras
                WHERE user_id = ?
            """, (user_id,))

            return [row["camera_id"] for row in cursor.fetchall()]

        finally:
            conn.close()


    def user_has_access_to_camera(self, user_id, camera_id):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT role
                FROM users
                WHERE id = ?
            """, (user_id,))

            row = cursor.fetchone()

            if not row:
                return False

            if row["role"] == "admin":
                return True

            cursor.execute("""
                SELECT 1
                FROM user_cameras
                WHERE user_id = ? AND camera_id = ?
            """, (user_id, camera_id))

            return cursor.fetchone() is not None

        finally:
            conn.close()


    #CAMERAS
    def get_all_cameras(self):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT camera_id
                FROM user_cameras
            """)

            return [row["camera_id"] for row in cursor.fetchall()]

        finally:
            conn.close()


    #NOTIFICATIONS
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


    def get_notification_phones(self, camera_id):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT u.phone
                FROM users u
                LEFT JOIN user_cameras uc ON u.id = uc.user_id
                WHERE u.notifications_enabled = 1
                AND u.phone IS NOT NULL
                AND u.phone != ''
                AND (
                    u.role = 'admin'
                    OR uc.camera_id = ?
                )
            """, (camera_id,))

            return [row["phone"] for row in cursor.fetchall()]

        finally:
            conn.close()


    def enable_notifications(self, user_id):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET notifications_enabled = 1
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
                UPDATE users
                SET notifications_enabled = 0
                WHERE id = ?
            """, (user_id,))

            conn.commit()

        finally:
            conn.close()


    #LOGIN LOGS
    def log_login_attempt(self, email, ip_address, success):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO login_logs (email, ip_address, success, timestamp)
                VALUES (?, ?, ?, datetime('now'))
            """, (email, ip_address, 1 if success else 0))

            conn.commit()

        finally:
            conn.close()


    def get_login_logs(self, limit=50):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT email, ip_address, success, timestamp
                FROM login_logs
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        finally:
            conn.close()


    #EVENTS
    def get_recent_events(self, limit=50):

        conn = self._get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT camera_name, start_time, end_time
                FROM presence_events
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

            events = []

            for row in rows:

                events.append({
                    "camera_id": row["camera_name"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"]
                })

            return events

        finally:
            conn.close()