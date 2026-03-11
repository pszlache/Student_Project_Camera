import cv2
import time


# CAMERA DETECTION
def detect_cameras(max_index=10, warmup_time=0.2):

    cameras = {}
    cam_id = 0

    print("[CAM DETECT] Scanning for cameras...")

    for index in range(max_index):

        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

        if not cap.isOpened():
            cap.release()
            continue

        # CAMERA WARMUP
        time.sleep(warmup_time)

        ret, frame = cap.read()

        cap.release()

        # INVALID FRAME
        if not ret or frame is None:
            print(f"[CAM DETECT] Camera index {index} returned no frame")
            continue

        height, width = frame.shape[:2]

        if height == 0 or width == 0:
            print(f"[CAM DETECT] Camera index {index} invalid frame size")
            continue

        # IMPORTANT CHANGE
        cameras[cam_id] = {
            "name": f"Camera {cam_id}",
            "index": index
        }

        print(
            f"[CAM DETECT] Found camera: system_id={cam_id}, device_index={index}"
        )

        cam_id += 1

    print(f"[CAM DETECT] Total cameras detected: {len(cameras)}")

    return cameras