import time
from camera.usb_camera import USBCamera
from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector
from utils.snapshot import save_snapshot
from web.stream import start_stream, set_shared_camera
from config import *

def main():
    # Camera Setting
    cam = USBCamera(
        CAMERA_INDEX,
        FRAME_WIDTH,
        FRAME_HEIGHT,
        FPS
    )

    cam.start()

    # Presence Setting
    presence_active = False
    last_presence_time = 0

    PRESENCE_TIMEOUT = 30 

    # Local Streaming
    set_shared_camera(cam)
    start_stream()
    print("Camera streaming on http://<IP_RPI>:5000")

    # Detection Settings
    motion = MotionDetector(
        BLUR_SIZE,
        MIN_DELTA,
        MOTION_THRESHOLD
    )

    last_snapshot = 0

    # AI Settings
    detector = PersonDetector(
        AI_MODEL_DIR,
        AI_CONFIDENCE
    )

    ai_counter = 0

    try:
        while True:
            frame = cam.read()
            if frame is None:
                time.sleep(0.01)
                continue
                
            now = time.time()
            if motion.detect(frame):
                ai_counter += 1

                if ai_counter % AI_FRAME_SKIP == 0:
                    if detector.detect(frame):
                        last_presence_time = now

                        if not presence_active:
                            presence_active = True
                            print("Human Detectec")

                            save_snapshot(frame, prefix="presence")

            else:
                ai_counter = 0

            if presence_active and (now - last_presence_time > PRESENCE_TIMEOUT):
                presence_active = False
                print("No presence")
        
            time.sleep(0.05)

    finally:
        cam.stop()

        
if __name__ == "__main__":
    main()