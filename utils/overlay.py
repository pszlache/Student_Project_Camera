import cv2

def draw_overlay(frame, camera_name, presence, person_bbox=None):
    cv2.putText(
        frame,
        camera_name,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0) if presence else (0, 0, 255),
        2
    )

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

    if person_bbox:
        x, y, w, h = person_bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return frame