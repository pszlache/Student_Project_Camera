import cv2
from datetime import datetime

def draw_overlay(frame, presence_active):
    h, w = frame.shape[:2]

    # TOP LEFT STATUS
    status_text = "ACTIVE" if presence_active else "NO ACTIVE"
    status_color = (0, 255, 0) if presence_active else (0, 0, 255)

    cv2.rectangle(frame, (5, 5), (180, 45), (0, 0, 0), -1)
    cv2.putText(
        frame,
        status_text,
        (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        status_color,
        2,
        cv2.LINE_AA
    )

    # DATE TOP RIGHT STATUS
    now = datetime.now()
    date_text = now.strftime("%Y-%m-%d")
    time_text = now.strftime("%H:%M:%S")

    cv2.rectangle(frame, (w - 210, 5), (w - 5, 65), (0, 0, 0), -1)
    cv2.putText(
        frame,
        date_text,
        (w - 200, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )
    cv2.putText(
        frame,
        time_text,
        (w - 200, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    return frame
