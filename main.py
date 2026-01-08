import time
from camera.usb_camera import USBCamera
from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector
from utils.snapshot import save_snapshot
from web.stream import start_stream, set_shared_cameras
from config import *

def main():
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
            "ai_counter": 0,
            "snapshot_taken": False,
            "snapshot_delay": 0
        }

    # Presence Setting
    PRESENCE_TIMEOUT = 30 

    # Local Streaming
    set_shared_cameras(
        {cid: data["camera"] for cid, data in cameras.items()}
    )
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
                                data["snapshot_taken"] = False
                                data["snapshot_delay"] = 2
                                print(f"{data['name']} - New Presence")
                            
                            elif not data["snapshot_taken"]:
                                data["snapshot_delay"] -= 1

                                if data["snapshot_delay"] <= 0:
                                    save_snapshot(
                                        frame,
                                        prefix=f"presence_cam{cam_id}"
                                    )
                                    data["snapshot_taken"] = True
                else:
                    data["ai_counter"] = 0

                if (
                    data["presence_active"]
                    and now - data["last_presence_time"] > PRESENCE_TIMEOUT
                ):
                    data["presence_active"] = False
                    data["snapshot_taken"] = False
                    print(f"{data['name']} - Presence Finish")
            
            time.sleep(0.05)

    finally:
        print("Close System...")
        for data in cameras.values():
            data["camera"].stop()

        
if __name__ == "__main__":
    main()