import subprocess
import re
import cv2


def detect_cameras():

    try:
        result = subprocess.run(
            ["v4l2-ctl", "--list-devices"],
            capture_output=True,
            text=True,
            timeout=3
        )
    except Exception as e:
        print(f"[CAM DETECT] v4l2-ctl error: {e}")
        return {}

    if result.returncode != 0:
        print("[CAM DETECT] v4l2-ctl failed")
        return {}

    cameras = {}
    cam_id = 0
    blocks = result.stdout.split("\n\n")

    for block in blocks:

        lines = block.strip().splitlines()
        if not lines:
            continue

        name = lines[0].rstrip(":")

        for line in lines[1:]:

            match = re.search(r"/dev/video(\d+)", line)
            if not match:
                continue

            index = int(match.group(1))

            cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
            if not cap.isOpened():
                cap.release()
                continue

            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                continue

            cameras[cam_id] = {
                "name": name,
                "index": index
            }

            cam_id += 1
            break

    return cameras
