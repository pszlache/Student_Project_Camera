import time
from camera.usb_camera import USBCamera
from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector
from utils.snapshot import save_snapshot
from config import *

def main():
    # Camera Settings
    cam = USBCamera(
        CAMERA_INDEX,
        FRAME_WIDTH,
        FRAME_HEIGHT,
        FPS
    )

    cam.start()

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
                continue

            if motion.detect(frame):
                ai_counter += 1

                # AI every N frames
                if ai_counter % AI_FRAME_SKIP == 0:
                    if detector.detect(frame):
                        now = time.time()
                        if now - last_snapshot > SNAPSHOT_COOLDOWN
                        print("Human Detectet")
                        save_snapshot(frame, prefix="person")
                        last_snapshot = now
        else:
            # Nothing motion -> reset
            ai_counter = 0
        
        time.sleep(0.05)

    finally:
        cam.stop()

        
if __name__ == "__main__":
    main()