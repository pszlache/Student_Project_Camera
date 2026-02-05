import time

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

    # INIT
    init_db()

    event_bus = EventBus()

    # Handlers
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

    # MAIN LOOP
    try:
        while True:

            for cam_id, data in cameras.items():

                frame = data["camera"].read()
                if frame is None:
                    continue

                data["presence_service"].update(frame)

            time.sleep(0.01)
    finally:
        for data in cameras.values():
            data["camera"].stop()


if __name__ == "__main__":
    main()


