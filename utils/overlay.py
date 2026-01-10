import cv2
from datetime import datetime

def draw_overlay(frame, camera_name, presence, person_bbox=None):
    # PREVENTING THE TEXT FROM BLINDING
    cv2.rectangle(frame, (5, 5), (320, 90), (0, 0, 0), -1)

    # CAMERA NAME
    cv2.putText(
        frame,
        camera_name,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0) if presence else (0, 0, 255),
        2
    )

    # STATUS
    status = "PRESENCE" if presence else "NO PRESENCE"
    cv2.putText(
        frame,
        status,
        (10, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0) if presence else (0, 0, 255),
        2
    )

    # DATE AND HOURS
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(
        frame,
        timestamp,
        (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0,6,
        (255, 255, 255),
        2
    )

    # BBOX PERSON
    if person_bbox:
        x, y, w, h = person_bbox
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    return frame