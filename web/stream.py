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

        user = auth_service.authenticate(
            email,
            password,
            request.remote_addr
        )

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
        visible_cameras = user_repo.get_user_cameras(user["id"])

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

    admin_button = ""
    if user["role"] == "admin":
        admin_button = "<a href='/admin'>Admin Panel</a>"

    return f"""
    <html>
        <body>
            <div style="display:flex; justify-content:space-between;">
                <h1>Monitoring Dashboard</h1>
                <div>
                    Logged as: {user["email"]} ({user["role"]})
                    | {admin_button}
                    | <a href="/logout">Logout</a>
                </div>
            </div>

            <div style="display:flex; gap:20px;">
                {camera_blocks}
            </div>
        </body>
    </html>
    """

# ADMIN PANEL
@app.route("/admin", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_panel():

    if request.method == "POST":

        action = request.form.get("action")

        # CREATE USER
        if action == "create_user":
            email = request.form.get("email")
            password = request.form.get("password")
            role = request.form.get("role")

            if email and password:
                auth_service.create_user(email, password, role)

        # DELETE USER
        elif action == "delete_user":
            user_id = int(request.form.get("user_id"))

            # Prevent admin from deleting himself
            if session["user"]["id"] != user_id:
                user_repo.delete_user_by_id(user_id)

        # ASSIGN CAMERA
        elif action == "assign_camera":
            user_id = int(request.form.get("user_id"))
            camera_id = int(request.form.get("camera_id"))

            user_repo.assign_camera(user_id, camera_id)

        # REMOVE CAMERA
        elif action == "remove_camera":
            user_id = int(request.form.get("user_id"))
            camera_id = int(request.form.get("camera_id"))

            user_repo.remove_camera(user_id, camera_id)

        # TOGGLE NOTIFICATIONS
        elif action == "toggle_notifications":
            user_id = int(request.form.get("user_id"))
            enabled = int(request.form.get("enabled"))

            if enabled:
                user_repo.enable_notifications(user_id)
            else:
                user_repo.disable_notifications(user_id)

    users = user_repo.get_all_users()

    user_rows = ""

    for user in users:

        assigned_cameras = user_repo.get_user_cameras(user["id"])
        camera_list = ", ".join(map(str, assigned_cameras)) if assigned_cameras else "None"

        # Build remove buttons for each assigned camera
        remove_buttons = ""
        for cam in assigned_cameras:
            remove_buttons += f"""
            <form method="post" style="display:inline;">
                <input type="hidden" name="action" value="remove_camera">
                <input type="hidden" name="user_id" value="{user["id"]}">
                <input type="hidden" name="camera_id" value="{cam}">
                <button type="submit">Remove {cam}</button>
            </form>
            """

        user_rows += f"""
        <tr>
            <td>{user["email"]}</td>
            <td>{user["role"]}</td>
            <td>{'ON' if user["notifications_enabled"] else 'OFF'}</td>
            <td>{camera_list}</td>

            <td>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="action" value="assign_camera">
                    <input type="hidden" name="user_id" value="{user["id"]}">
                    <input name="camera_id" placeholder="Camera ID">
                    <button type="submit">Assign</button>
                </form>
            </td>

            <td>
                {remove_buttons}
            </td>

            <td>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="action" value="toggle_notifications">
                    <input type="hidden" name="user_id" value="{user["id"]}">
                    <input type="hidden" name="enabled" value="{0 if user["notifications_enabled"] else 1}">
                    <button type="submit">
                        {'Disable' if user["notifications_enabled"] else 'Enable'}
                    </button>
                </form>
            </td>

            <td>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="action" value="delete_user">
                    <input type="hidden" name="user_id" value="{user["id"]}">
                    <button type="submit"
                        {'disabled' if session["user"]["id"] == user["id"] else ''}>
                        Delete
                    </button>
                </form>
            </td>
        </tr>
        """

    return f"""
    <html>
        <body>
            <h2>Admin Panel</h2>
            <a href="/">Back</a>
            <hr>

            <h3>Create User</h3>
            <form method="post">
                <input type="hidden" name="action" value="create_user">

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
                    <th>Assigned Cameras</th>
                    <th>Assign Camera</th>
                    <th>Remove Camera</th>
                    <th>Toggle Notifications</th>
                    <th>Delete</th>
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

    user_id = session["user"]["id"]

    # Permission check
    if not user_repo.user_has_access_to_camera(user_id, cam_id):
        return "Forbidden", 403

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
