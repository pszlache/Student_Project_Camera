import cv2
import time

def detect_cameras(max_index=10):

    cameras = {}
    cam_id = 0

    for index in range(max_index):

        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

        if not cap.isOpened():
            cap.release()
            continue

        time.sleep(0.2)

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            continue

        cameras[cam_id] = {
            "name": f"Camera{index}",
            "index": index
        }

        print(f"[CAM DETECT] Found camera at index {index}")
        cam_id += 1

    return cameras
