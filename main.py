import time
from camera.usb_camera import USBCamera
from motion.motion_detector import MotionDetector
from utils.snapshot import save_snapshot
from config import *

def main():
    cam = USBCamera(
        CAMERA_INDEX,
        FRAME_WIDITH,
        FRAME_HEIGHT,
        FPS
    )

    cam.start()

    motion = MotionDetector(
        BLUR_SIZE,
        MIN_DELTA,
        MOTION_THRESHOLD
    )

    last_snapshot = 0

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            if motion.detect(frame):
                now = time.time()
                if now - last_snapshot > SNAPSHOT_COOLDOWN:
                    print("Ruch Wykryty")
                    save_snapshot(frame)
                    last_snapshot = now

            time.sleep(0.05)

    finally:
        cam.stop()

if __name__ == "__main__":
    main()