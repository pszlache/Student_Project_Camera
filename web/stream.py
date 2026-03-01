from flask import (
    Flask,
    Response,
    stream_with_context,
    request,
    redirect,
    session,
    url_for,
    render_template,
    jsonify
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

# ================= FLASK INIT =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# ================= SESSION SECURITY =================

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

app.register_blueprint(logs_bp)

auth_service = AuthService()
user_repo = UserRepository()

shared_cameras = {}

# ================= AUTH DECORATORS =================

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

# ================= CAMERA SHARING =================

def set_shared_cameras(cameras):
    global shared_cameras
    shared_cameras = cameras

# ================= STREAM =================

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

        time.sleep(0.05)

# ================= STATUS API =================

@app.route("/api/status")
@login_required
def api_status():
    cameras_online = len(shared_cameras)

    return jsonify({
        "ai": True,
        "gsm": False,
        "cameras": cameras_online > 0
    })

# ================= AUTH ROUTES =================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

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
            session.permanent = True
            return redirect(url_for("index"))

        error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= DASHBOARD =================

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

# ================= EVENTS =================

@app.route("/events")
@login_required
def events_page():
    return render_template("events.html", events=[])

# ================= SYSTEM =================

@app.route("/system")
@login_required
def system_page():
    return render_template(
        "system.html",
        cameras_count=len(shared_cameras),
        disk_usage="—",
        uptime="—"
    )

# ================= RECORDS =================

@app.route("/records/<int:cam_id>")
@login_required
def records_page(cam_id):
    return f"<h2>Records for camera {cam_id} (module coming soon)</h2>"

# ================= VIDEO =================

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

# ================= START =================

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