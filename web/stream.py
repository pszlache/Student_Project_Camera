from flask import Flask, Response
import cv2
import threading
import time

app = Flask(__name__)

shared_camera = None

def set_shared_camera(camera):
    global shared_camera
    shared_camera = camera

def generate_frames():
    while True:
        if shared_camera is None:
            time.sleep(0.1)
            continue

        frame = shared_camera.read()
        if frame is None:
            continue

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

@app.route('/')
def index():
    return '''
    <html>
        <head><title>Camera Stream</title></head>
        <body>
            <h1>Podgląd Kamery</h1>
            <img src='/video'>
        </body>
    </html>
    '''
@app.route('/video')
def video():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace;boundary=frame'
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