from flask import (
    Flask,
    Response,
    stream_with_context,
    request,
    redirect,
    session,
    url_for,
    render_template,
    jsonify,
    send_from_directory
)
from functools import wraps
from utils.overlay import draw_overlay
from web.logs import logs_bp
from core.services.auth_service import AuthService
from core.repositories.user_repository import UserRepository
from logs.db import _get_connection
from core.services.system_state import SystemState
from core.services.runtime_config import RuntimeConfig

import sqlite3
import cv2
import threading
import time
import os
import glob
import json

from datetime import timedelta


#FLASK INIT
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

app.secret_key = os.getenv("SECRET_KEY", "dev_secret")


#SESSION SECURITY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

app.register_blueprint(logs_bp)

auth_service = AuthService()
user_repo = UserRepository()

shared_cameras = {}


#AUTH DECORATORS
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


#CAMERA SHARING
def set_shared_cameras(cameras):
    global shared_cameras
    shared_cameras = cameras


#STREAM
def generate_frames(cam_id):
    while True:

        data = shared_cameras.get(cam_id)

        if data is None:
            time.sleep(0.1)
            continue

        if not SystemState.cameras_enabled:
            time.sleep(0.1)
            continue

        frame = data["camera"].read()

        if frame is None:
            time.sleep(0.01)
            continue

        presence_active = data["presence_service"].presence_active

        overlay = draw_overlay(
            frame.copy(),
            presence_active
        )

        ret, buffer = cv2.imencode(
            ".jpg",
            overlay,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        )

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

        time.sleep(0.05)


#STATUS API
@app.route("/api/status")
@login_required
def api_status():

    cameras_online = len(shared_cameras)

    return jsonify({
        "ai": True,
        "gsm": True,
        "cameras": cameras_online
    })


#MAIL CONFIG (ADMIN)
@app.route("/admin/mail_config", methods=["POST"])
@login_required
@role_required("admin")
def update_mail_config():

    host = request.form.get("smtp_host")
    port = request.form.get("smtp_port")
    username = request.form.get("smtp_username")
    password = request.form.get("smtp_password")

    RuntimeConfig.update_mail(
        host,
        int(port),
        username,
        password
    )

    print("[ADMIN] SMTP configuration updated")

    return redirect(url_for("admin_panel"))


#AUTH
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


#DASHBOARD
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

    return render_template(
        "dashboard.html",
        cameras=cameras_data
    )

#ADMIN
@app.route("/admin", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_panel():

    if request.method == "POST":

        action = request.form.get("action")

        #CREATE USER
        if action == "create_user":

            email = request.form.get("email")
            phone = request.form.get("phone")
            password = request.form.get("password")
            role = request.form.get("role")

            print(f"[ADMIN] Create user: {email}")

            if email and password:
                auth_service.create_user(email, password, role, phone)

        #DELETE USER
        elif action == "delete_user":

            user_id = int(request.form.get("user_id"))

            if session["user"]["id"] != user_id:
                user_repo.delete_user_by_id(user_id)

        #ASSIGN CAMERA
        elif action == "assign_camera":

            user_id = int(request.form.get("user_id"))
            camera_id_raw = request.form.get("camera_id")

            if camera_id_raw == "":
                user_repo.remove_all_cameras(user_id)

            else:

                camera_id = int(camera_id_raw)

                user_repo.remove_all_cameras(user_id)
                user_repo.assign_camera(user_id, camera_id)

        #REMOVE CAMERA
        elif action == "remove_camera":

            user_id = int(request.form.get("user_id"))
            camera_id = int(request.form.get("camera_id"))

            user_repo.remove_camera(user_id, camera_id)

        #TOGGLE NOTIFICATIONS
        elif action == "toggle_notifications":

            user_id = int(request.form.get("user_id"))
            enabled = int(request.form.get("enabled"))

            if enabled:
                user_repo.enable_notifications(user_id)
            else:
                user_repo.disable_notifications(user_id)

    users = user_repo.get_all_users()
    login_logs = user_repo.get_login_logs(50)

    return render_template(
        "admin.html",
        users=users,
        login_logs=login_logs
    )

#CAMERA DETAIL
@app.route("/camera/<int:cam_id>")
@login_required
def camera_detail(cam_id):

    if cam_id not in shared_cameras:
        return "Camera not found", 404

    user_id = session["user"]["id"]

    if not user_repo.user_has_access_to_camera(user_id, cam_id):
        return "Forbidden", 403

    presence = shared_cameras[cam_id]["presence_service"].presence_active

    return render_template(
        "camera_detail.html",
        cam_id=cam_id,
        presence=presence
    )


#VIDEO STREAM
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


#LIVE EVENTS (SSE)
@app.route("/api/events")
@login_required
def live_events():

    def event_stream():

        last_event_id = None

        while True:

            conn = _get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, camera_name, start_time
                FROM presence_events
                ORDER BY id DESC
                LIMIT 1
            """)

            row = cursor.fetchone()

            conn.close()

            if row:

                event_id = row["id"]

                if event_id != last_event_id:

                    last_event_id = event_id

                    payload = json.dumps({
                        "camera": row["camera_name"],
                        "time": row["start_time"]
                    })

                    yield f"data: {payload}\n\n"

            time.sleep(1)

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream"
    )

#EVENTS
@app.route("/events")
@login_required
def events_page():

    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT camera_name, start_time, end_time
        FROM presence_events
        ORDER BY id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()

    conn.close()

    events = []

    for row in rows:

        start = row["start_time"]
        end = row["end_time"]

        duration = None

        try:

            if start and end:
                duration = float(end) - float(start)

        except:
            duration = None

        events.append({
            "camera_id": row["camera_name"],
            "start_time": start,
            "end_time": end,
            "duration": duration
        })

    return render_template(
        "events.html",
        events=events
    )

#SYSTEM
@app.route("/system")
@login_required
def system_page():

    import psutil
    import shutil

    cpu_usage = psutil.cpu_percent(interval=0.2)

    ram = psutil.virtual_memory()
    ram_usage = ram.percent

    disk = shutil.disk_usage("/")
    disk_usage = round((disk.used / disk.total) * 100)

    uptime_seconds = time.time() - psutil.boot_time()

    uptime = str(timedelta(seconds=int(uptime_seconds)))

    return render_template(
        "system.html",
        cameras_count=len(shared_cameras),
        cpu_usage=cpu_usage,
        ram_usage=ram_usage,
        disk_usage=disk_usage,
        uptime=uptime
    )

#START
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