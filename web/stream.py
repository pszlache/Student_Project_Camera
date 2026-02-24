from flask import (
    Flask,
    Response,
    stream_with_context,
    request,
    redirect,
    session,
    url_for,
    render_template
)
from functools import wraps
from utils.overlay import draw_overlay
from web.logs import logs_bp
from core.services.auth_service import AuthService
from core.repositories.user_repository import UserRepository

import cv2
import threading
import time
import os
from datetime import timedelta

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# SESSION SECURITY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

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

        ret, buffer = cv2.imencode(".jpg", overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

        time.sleep(0.05)  # PI FRIENDLY FPS

# STATUS API
@app.route("/api/status")
@login_required
def api_status():
    cameras_online = len(shared_cameras)
    return {
        "ai": True,
        "gsm": False,
        "cameras": cameras_online > 0
    }

# AUTH ROUTES
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = auth_service.authenticate(email, password, request.remote_addr)

        if user:
            session["user"] = user
            session.permanent = True
            return redirect(url_for("index"))

        error = "Invalid credentials"

    return render_template("login.html", error=error)


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
        visible_cameras = list(shared_cameras.keys())
    else:
        visible_cameras = user_repo.get_user_cameras(user["id"])

    cameras_data = []

    for cam_id in visible_cameras:
        if cam_id not in shared_cameras:
            continue

        presence = shared_cameras[cam_id]["presence_service"].presence_active

        cameras_data.append({
            "id": cam_id,
            "presence": presence
        })

    return render_template("dashboard.html", cameras=cameras_data)

# ADMIN PANEL
@app.route("/admin", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_panel():

    if request.method == "POST":

        action = request.form.get("action")

        if action == "create_user":
            email = request.form.get("email")
            password = request.form.get("password")
            role = request.form.get("role")
            if email and password:
                auth_service.create_user(email, password, role)

        elif action == "delete_user":
            user_id = int(request.form.get("user_id"))
            if session["user"]["id"] != user_id:
                user_repo.delete_user_by_id(user_id)

        elif action == "assign_camera":
            user_id = int(request.form.get("user_id"))
            camera_id_raw = request.form.get("camera_id")
            if camera_id_raw == "":
                user_repo.remove_all_cameras(user_id)
            else:
                user_repo.assign_camera(user_id, int(camera_id_raw))

        elif action == "remove_camera":
            user_id = int(request.form.get("user_id"))
            camera_id = int(request.form.get("camera_id"))
            user_repo.remove_camera(user_id, camera_id)

        elif action == "toggle_notifications":
            user_id = int(request.form.get("user_id"))
            enabled = int(request.form.get("enabled"))
            if enabled:
                user_repo.enable_notifications(user_id)
            else:
                user_repo.disable_notifications(user_id)

    users = user_repo.get_all_users()
    login_logs = user_repo.get_login_logs(50)

    return render_template("admin.html", users=users, login_logs=login_logs)

# VIDEO ROUTE
@app.route("/video/<int:cam_id>")
@login_required
def video(cam_id):

    if cam_id not in shared_cameras:
        return "Camera not found", 404

    user_id = session["user"]["id"]

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
            use_reloader=False,
            threaded=True
        ),
        daemon=True
    ).start()