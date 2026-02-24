import bcrypt
import sqlite3
from logs.db import DB_PATH
from logs.db import DB_PATH, log_login_attempt

class AuthService:

    def __init__(self):
        pass

    def _get_connection(self):
        return sqlite3.connect(DB_PATH)

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def create_user(self, email: str, password: str, role: str = "user") -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            password_hash = self.hash_password(password)

            cursor.execute("""
                INSERT INTO users (email, password_hash, role)
                VALUES (?, ?, ?)
            """, (email, password_hash, role))

            conn.commit()
            return True

        except sqlite3.IntegrityError:
            return False

        finally:
            conn.close()

    def authenticate(self, email: str, password: str, ip_address: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, password_hash, role
                FROM users
                WHERE email = ?
            """, (email,))

            row = cursor.fetchone()

            if not row:
                log_login_attempt(email, ip_address, False)
                return None

            user_id, password_hash, role = row

            if self.verify_password(password, password_hash):
                log_login_attempt(email, ip_address, True)
                return {
                    "id": user_id,
                    "email": email,
                    "role": role
                }

            log_login_attempt(email, ip_address, False)
            return None

        finally:
            conn.close()


    def ensure_default_admin(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM users WHERE role = 'admin'
            """)
            count = cursor.fetchone()[0]

            if count == 0:
                print("[AUTH] Creating default admin user...")

                default_email = "admin@local"
                default_password = "admin123"

                password_hash = self.hash_password(default_password)

                cursor.execute("""
                    INSERT INTO users (email, password_hash, role)
                    VALUES (?, ?, ?)
                """, (default_email, password_hash, "admin"))

                conn.commit()

                print("[AUTH] Default admin created:")
                print("        email: admin@local")
                print("        password: admin123")

        finally:
            conn.close()