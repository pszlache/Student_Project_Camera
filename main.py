import time
import signal
import sys

from camera.usb_camera import USBCamera
from camera.detect import detect_cameras

from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector

from web.stream import start_stream, set_shared_cameras

from core.events import EventBus
from core.services.presence_service import PresenceService

from core.handlers.db_handler import DBHandler
from core.handlers.video_handler import VideoRecorderHandler
from core.handlers.snapshot_handler import SnapshotHandler

from logs.db import init_db
from config import *


def main():

    print("=== SYSTEM STARTING ===")

    # INIT DB
    init_db()

    event_bus = EventBus()

    # HANDLERS
    db_handler = DBHandler()
    video_handler = VideoRecorderHandler(fps=FPS)
    snapshot_handler = SnapshotHandler(event_bus)

    event_bus.register(db_handler)
    event_bus.register(video_handler)
    event_bus.register(snapshot_handler)

    # CAMERA DETECTION
    detected = detect_cameras()

    if not detected:
        print("No cameras detected")
        return

    cameras = {}

    for cam_id, cfg in detected.items():

        print(f"[MAIN] Initializing camera {cfg['index']}")

        cam = USBCamera(
            cfg["index"],
            FRAME_WIDTH,
            FRAME_HEIGHT,
            FPS
        )
        cam.start()

        presence_service = PresenceService(
            cam_id,
            cfg["name"],
            MotionDetector(
                BLUR_SIZE,
                MIN_DELTA,
                MOTION_THRESHOLD
            ),
            PersonDetector(
                AI_MODEL_DIR,
                AI_CONFIDENCE
            ),
            event_bus,
            AI_FRAME_SKIP,
            PRESENCE_TIMEOUT
        )

        cameras[cam_id] = {
            "camera": cam,
            "presence_service": presence_service,
            "name": cfg["name"]
        }

    # STREAM
    set_shared_cameras(cameras)
    start_stream()

    print("=== SYSTEM RUNNING ===")

    running = True

    # SIGNAL HANDLER
    def shutdown_handler(signum, frame):
        nonlocal running
        print("\n=== SHUTDOWN SIGNAL RECEIVED ===")
        running = False

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # MAIN LOOP
    try:
        while running:

            for cam_id, data in cameras.items():

                frame = data["camera"].read()
                if frame is None:
                    continue

                data["presence_service"].update(frame)

            time.sleep(0.01)

    finally:
        print("=== STOPPING CAMERAS ===")

        for data in cameras.values():
            data["camera"].stop()

        print("=== SYSTEM SHUTDOWN COMPLETE ===")
        sys.exit(0)


if __name__ == "__main__":
    main()


