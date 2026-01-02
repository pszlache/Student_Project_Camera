import os
import cv2
from datetime import datetime
from config import SNAPSHOT_DIR

def save_snapshot(frame, prefix="motion"):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{prefix}_{ts}.jpg"
    path = os.path.join(SNAPSHOT_DIR, filename)

    cv2.imwrite(path, frame)
    return path