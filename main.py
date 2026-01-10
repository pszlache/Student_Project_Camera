import time
from camera.usb_camera import USBCamera
from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector
from utils.snapshot import save_snapshot
from web.stream import start_stream, set_shared_cameras
from logs.db import init_db, log_presence_start, log_presence_end
from config import *

def main():
    # Initialize database
    init_db()

    # Camera Setting
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
            "event_id": None,
            "last_snapshot_path": None,
            "ai_counter": 0,
            "snapshot_taken": False,
            "snapshot_delay": 0
        }

    # Presence Setting
    PRESENCE_TIMEOUT = 30 

    # Local Streaming
    set_shared_cameras(cameras)

    start_stream()
    print("Camera streaming on http://<IP_RPI>:5000")

    try:
        while True:
            now = time.time()

            for cam_id, data in cameras.items():
                frame = data["camera"].read()
                if frame is None:
                    continue
                
                if data["motion"].detect(frame):
                    data["ai_counter"] += 1

                    if data["ai_counter"] % AI_FRAME_SKIP == 0:
                        if data["detector"].detect(frame):
                            data["last_presence_time"] = now

                            if not data["presence_active"]:
                                data["presence_active"] = True
                                data["camera"].presence_active = True

                                data["event_id"] = log_presence_start(data["name"])
                                data["snapshot_taken"] = False
                                data["snapshot_delay"] = 2
                                data["last_snapshot_path"] = None

                                print(f"{data['name']} - New Presence")
                            
                            elif not data["snapshot_taken"]:
                                data["snapshot_delay"] -= 1

                                if data["snapshot_delay"] <= 0:
                                    path = save_snapshot(
                                        frame,
                                        prefix=f"presence_cam{cam_id}"
                                    )
                                    data["last_snapshot_path"] = path
                                    data["snapshot_taken"] = True
                else:
                    data["ai_counter"] = 0

                if (
                    data["presence_active"]
                    and now - data["last_presence_time"] > PRESENCE_TIMEOUT
                ):
                    data["presence_active"] = False
                    data["camera"].presence_active = False
                    data["ai_counter"] = 0

                    if data["event_id"] is not None:
                        log_presence_end(
                            data["event_id"],
                            data["last_snapshot_path"]
                        )
                    
                    data["event_id"] = None
                    data["last_snapshot_path"] = None

                    print(f"{data['name']} - Presence Finish")
            
            time.sleep(0.05)

    finally:
        print("Close System...")
        for data in cameras.values():
            data["camera"].stop()

        
if __name__ == "__main__":
    main()