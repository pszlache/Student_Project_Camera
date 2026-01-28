import time

from camera.usb_camera import USBCamera
from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector
<<<<<<< Updated upstream
from logs.db import init_db, log_presence_start, log_presence_end
from utils.snapshot import save_snapshot
from web.stream import start_stream, set_shared_cameras
from config import *
=======
from web.stream import start_stream, set_shared_cameras
from camera.detect import detect_cameras

from logs.db import init_db

from core.events import (
    EventBus,
    EventType,
    PresenceStartEvent,
    PresenceEndEvent
)

from handlers.db_handler import (
    handle_presence_start as db_start,
    handle_presence_end as db_end
)

from handlers.snapshot_handler import (
    handle_presence_start as snapshot_start
)

from handlers.mail_handler import (
    handle_presence_start as mail_start
)

from handlers.gsm_handler import (
    handle_presence_start as gsm_start
)

from config import (
    FRAME_WIDTH, FRAME_HEIGHT, FPS,
    BLUR_SIZE, MIN_DELTA, MOTION_THRESHOLD,
    AI_MODEL_DIR, AI_CONFIDENCE, AI_FRAME_SKIP
)
>>>>>>> Stashed changes


def main():
<<<<<<< Updated upstream
    # Initialize DataBase 
    init_db()

    # Camera Setting
=======

    # ===============================
    # INIT
    # ===============================

    init_db()

    event_bus = EventBus()

    # Rejestracja handlerów
    event_bus.register(EventType.PRESENCE_START, db_start)
    event_bus.register(EventType.PRESENCE_START, snapshot_start)
    event_bus.register(EventType.PRESENCE_START, mail_start)
    event_bus.register(EventType.PRESENCE_START, gsm_start)

    event_bus.register(EventType.PRESENCE_END, db_end)

    # ===============================
    # CAMERA DETECTION
    # ===============================

    detected = detect_cameras()
    if not detected:
        print("No cameras detected")
        return

>>>>>>> Stashed changes
    cameras = {}
    for cam_id, cfg in CAMERAS.items():
        print(f"Starting Camera {cam_id}: {cfg['name']}")

        cam = USBCamera(
            cfg["index"],
            FRAME_WIDTH,
            FRAME_HEIGHT,
            FPS
        )
        cam.start()

        cameras[cam_id] = {
            "name": cfg["name"],
            "camera": cam,
            "motion": MotionDetector(
                BLUR_SIZE,
                MIN_DELTA,
                MOTION_THRESHOLD
            ),
            "detector": PersonDetector(
                AI_MODEL_DIR,
                AI_CONFIDENCE
            ),
            "presence_active": False,
            "last_bbox": None,
            "last_presence_time": 0,
<<<<<<< Updated upstream
            "ai_counter": 0,
            "snapshot_taken": False,
            "snapshot_delay": 0,
            "event_id": None,
            "last_snapshot_path": None
=======
            "ai_counter": 0
>>>>>>> Stashed changes
        }

    # ===============================
    # STREAM
    # ===============================

    set_shared_cameras(cameras)
    start_stream()
    print("Camera streaming on http://<IP_RPI>:5000")

    PRESENCE_TIMEOUT = 30

    # ===============================
    # MAIN LOOP
    # ===============================

    try:
        while True:
            now = time.time()

            for cam_id, data in cameras.items():

                frame = data["camera"].read()
                if frame is None:
                    time.sleep(0.01)
                    continue
<<<<<<< Updated upstream
                # MOTION
                if data["motion"].detect(frame):
                    data["ai_counter"] += 1
                
                # AI FRAME
                    if data["ai_counter"] % AI_FRAME_SKIP == 0:
                        bbox = data["detector"].detect(frame)

                        if bbox:
                            data["last_bbox"] = bbox
=======

                # --- MOTION ---
                if data["motion"].detect(frame):
                    data["ai_counter"] += 1

                    # --- AI ---
                    if data["ai_counter"] % AI_FRAME_SKIP == 0:
                        if data["detector"].detect(frame):

>>>>>>> Stashed changes
                            data["last_presence_time"] = now

                            if not data["presence_active"]:
                                data["presence_active"] = True
<<<<<<< Updated upstream
                                data["snapshot_taken"] = False
                                data["snapshot_delay"] = 2
                                data["event_id"] = log_presence_start(data["name"])
                                print(f"{data['name']} - New Presence")
                            
                            elif not data["snapshot_taken"]:
                                data["snapshot_delay"] -= 1

                                if data["snapshot_delay"] <= 0:
                                    snapshot_path = save_snapshot(
                                        frame,
                                        prefix=f"presence_cam{cam_id}"
                                    )
                                    data["last_snapshot_path"] = snapshot_path
                                    data["snapshot_taken"] = True
=======
                                data["camera"].presence_active = True

                                event = PresenceStartEvent(
                                    cam_id,
                                    data["name"],
                                    frame
                                )

                                event_bus.emit(event)

>>>>>>> Stashed changes
                else:
                    data["ai_counter"] = 0
                    data["last_bbox"] = None

                # --- TIMEOUT ---
                if (
                    data["presence_active"]
                    and now - data["last_presence_time"] > PRESENCE_TIMEOUT
                ):
                    data["presence_active"] = False
<<<<<<< Updated upstream
                    data["snapshot_taken"] = False

                    if data["event_id"] is not None:
                        log_presence_end(
                            data["event_id"],
                            data["last_snapshot_path"]
                        )

                    data["event_id"] = None
                    data["last_snapshot_path"] = None
                    data["last_bbox"] = None
                    print(f"{data['name']} - Presence Finish")
                
=======
                    data["camera"].presence_active = False
                    data["ai_counter"] = 0

                    event = PresenceEndEvent(
                        cam_id,
                        data["name"],
                        snapshot_path=None
                    )

                    event_bus.emit(event)

>>>>>>> Stashed changes
            time.sleep(0.05)

    finally:
        print("Close System...")
        for data in cameras.values():
            data["camera"].stop()


if __name__ == "__main__":
    main()