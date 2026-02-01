import time

from camera.usb_camera import USBCamera
from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector
from utils.snapshot import save_snapshot
from web.stream import start_stream, set_shared_cameras
from logs.db import init_db
from config import *

# EVENT SYSTEM
from core.events import (
    EventBus,
    EventType,
    PresenceStartEvent,
    PresenceEndEvent,
    SnapshotSavedEvent
)

# HANDLERS
from core.handlers.db_handler import (
    handle_presence_start,
    handle_presence_end
)

from core.handlers.video_handler import VideoRecorderHandler  # NEW


def main():
    # INIT SYSTEM
    init_db()

    event_bus = EventBus()

    # Register DB handlers
    event_bus.register(EventType.PRESENCE_START, handle_presence_start)
    event_bus.register(EventType.PRESENCE_END, handle_presence_end)

    # Video recorder handler
    video_handler = VideoRecorderHandler()
    event_bus.register(EventType.PRESENCE_START, video_handler.handle_presence_start)
    event_bus.register(EventType.PRESENCE_END, video_handler.handle_presence_end)

    # CAMERA SETUP
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
            "last_presence_time": 0,
            "ai_counter": 0,
            "snapshot_taken": False,
            "snapshot_delay": 0,
            "last_snapshot_path": None
        }

    PRESENCE_TIMEOUT = 30

    # STREAMING
    set_shared_cameras(cameras)
    start_stream()
    print("Camera streaming on http://<IP_RPI>:5000")

    # MAIN LOOP
    try:
        while True:
            now = time.time()

            for cam_id, data in cameras.items():

                frame = data["camera"].read()
                if frame is None:
                    continue

                video_handler.write_frame(cam_id, frame)

                # MOTION
                if data["motion"].detect(frame):
                    data["ai_counter"] += 1

                    # AI DETECTION
                    if data["ai_counter"] % AI_FRAME_SKIP == 0:
                        person_detected = data["detector"].detect(frame)

                        if person_detected:
                            data["last_presence_time"] = now

                            if not data["presence_active"]:
                                data["presence_active"] = True
                                data["snapshot_taken"] = False
                                data["snapshot_delay"] = 2
                                print(f"{data['name']} - Presence START")

                                event_bus.emit(
                                    PresenceStartEvent(
                                        cam_id,
                                        data["name"],
                                        frame
                                    )
                                )

                        # SNAPSHOT DELAY
                        elif not data["snapshot_taken"]:
                            data["snapshot_delay"] -= 1

                            if data["snapshot_delay"] <= 0:
                                snapshot_path = save_snapshot(
                                    frame,
                                    prefix=f"presence_cam{cam_id}"
                                )

                                data["last_snapshot_path"] = snapshot_path
                                data["snapshot_taken"] = True

                                event_bus.emit(
                                    SnapshotSavedEvent(
                                        cam_id,
                                        data["name"],
                                        snapshot_path
                                    )
                                )

                else:
                    data["ai_counter"] = 0

                # PRESENCE END
                if (
                    data["presence_active"]
                    and now - data["last_presence_time"] > PRESENCE_TIMEOUT
                ):
                    data["presence_active"] = False
                    data["snapshot_taken"] = False
                    data["snapshot_delay"] = 0

                    print(f"{data['name']} - Presence END")

                    # NEW: emit end event
                    event_bus.emit(
                        PresenceEndEvent(
                            cam_id,
                            data["name"],
                            data["last_snapshot_path"]
                        )
                    )

                    data["last_snapshot_path"] = None

            time.sleep(0.05)

    finally:
        print("Close System...")
        for data in cameras.values():
            data["camera"].stop()


if __name__ == "__main__":
    main()
