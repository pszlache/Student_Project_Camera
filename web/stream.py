from flask import Flask, Response, stream_with_context
from utils.overlay import draw_overlay
import cv2
import threading
import time

app = Flask(__name__)

shared_cameras = {}

def set_shared_cameras(cameras):
    global shared_cameras
    shared_cameras = cameras

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

        overlay = draw_overlay(
            frame.copy(),
            data["name"],
            data["presence_active"],
            data.get("last_bbox")
        )

        ret, buffer = cv2.imencode(
            '.jpg',
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            )
        
        if not ret:
            continue

        yield(
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            buffer.tobytes() +
            b'\r\n'
        )

        time.sleep(0.02)

@app.route('/')
def index():
    return '''
    <html>
        <body>
            <h1>Monitoring</h1>
            <div style="display:flex;">
                <div>
                    <h3>FirstCam</h3>
                    <img src='/video/0'>
                </div>
                <div>
                    <h3>SecondCam</h3>
                    <img src='/video/1'>
                </div>
            </div>
        </body>
    </html>
    '''
@app.route('/video/<int:cam_id>')
def video(cam_id):
    if cam_id not in shared_cameras:
        return "Camera not found", 404
    
    return Response(
        stream_with_context(generate_frames(cam_id)),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def start_stream():
    threading.Thread(
        target=lambda: app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    ).start()