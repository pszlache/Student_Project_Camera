import cv2
import time
from camera.usb_camera import USBCamera
from config import *

def main():
    cam = USBCamera(
        CAMERA_INDEX,
        FRAME_WIDITH,
        FRAME_HEIGHT,
        FPS
    )

    cam.start()
    print("Starting Camera..")

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            cv2.imshow("Camera test", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

            time.sleep(0.02)

    finally:
        cam.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()