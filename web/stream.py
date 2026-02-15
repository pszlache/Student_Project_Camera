from flask import (
    Flask,
    Response,
    stream_with_context,
    request,
    redirect,
    session,
    url_for
)
from functools import wraps
from utils.overlay import draw_overlay
from web.logs import logs_bp
from core.services.auth_service import AuthService
from core.repositories.user_repository import UserRepository

import cv2
import threading
import time

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

app.register_blueprint(logs_bp)

auth_service = AuthService()
user_repo = UserRepository()

shared_cameras = {}

# AUTH DECORATORS
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))
            if session["user"]["role"] != role:
                return "Forbidden", 403
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# CAMERA SHARING
def set_shared_cameras(cameras):
    global shared_cameras
    shared_cameras = cameras

# VIDEO STREAM GENERATOR
def generate_frames(cam_id):
    while True:
        data = shared_cameras.get(cam_id)
        if data is None:
            time.sleep(0.1)
            continue

        frame = data["camera"].read()
        if frame is None:
            time.sleep(0.01)
            continue

        presence_active = data["presence_service"].presence_active

        overlay = draw_overlay(frame.copy(), presence_active)

        ret, buffer = cv2.imencode(
            ".jpg",
            overlay,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        )

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

        time.sleep(0.03)

# AUTH ROUTES
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = auth_service.authenticate(email, password)

        if user:
            session["user"] = user
            return redirect(url_for("index"))

        return """
            <h3>Invalid credentials</h3>
            <a href="/login">Try again</a>
        """, 401

    return """
        <h2>Login</h2>
        <form method="post">
            <input name="email" placeholder="Email"><br><br>
            <input name="password" type="password" placeholder="Password"><br><br>
            <button type="submit">Login</button>
        </form>
    """


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# DASHBOARD
@app.route("/")
@login_required
def index():

    user = session["user"]

    if user["role"] == "admin":
        visible_cameras = shared_cameras.keys()
    else:
        allowed = user_repo.get_user_cameras(user["id"])
        visible_cameras = allowed

    camera_blocks = ""

    for cam_id in visible_cameras:
        if cam_id not in shared_cameras:
            continue

        camera_blocks += f"""
        <div>
            <h3>Camera {cam_id}</h3>
            <img src='/video/{cam_id}'>
        </div>
        """

    return f"""
    <html>
        <body>
            <h1>Dashboard</h1>
            {camera_blocks}
        </body>
    </html>
    """

# ADMIN PANEL
@app.route("/admin", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_panel():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        if email and password:
            auth_service.create_user(email, password, role)

    users = user_repo.get_all_users()

    user_rows = ""
    for user in users:
        user_rows += f"""
        <tr>
            <td>{user["email"]}</td>
            <td>{user["role"]}</td>
            <td>{user["notifications_enabled"]}</td>
        </tr>
        """

    return f"""
    <html>
        <body>
            <h2>Admin Panel</h2>
            <a href="/">Back</a>
            <hr>

            <h3>Add User</h3>
            <form method="post">
                Email:<br>
                <input name="email"><br><br>

                Password:<br>
                <input name="password" type="password"><br><br>

                Role:<br>
                <select name="role">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select><br><br>

                <button type="submit">Create User</button>
            </form>

            <hr>

            <h3>Users</h3>
            <table border="1">
                <tr>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Notifications</th>
                </tr>
                {user_rows}
            </table>
        </body>
    </html>
    """

# VIDEO ROUTE
@app.route("/video/<int:cam_id>")
@login_required
def video(cam_id):
    if cam_id not in shared_cameras:
        return "Camera not found", 404

    return Response(
        stream_with_context(generate_frames(cam_id)),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# START SERVER
def start_stream():
    threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    ).start()
