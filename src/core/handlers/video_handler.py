import cv2
import os
from datetime import datetime
from core.events import EventType


VIDEO_DIR = "recordings"


class VideoRecorderHandler:

    def __init__(self, fps=15):

        self.fps = fps
        self._writers = {}

        os.makedirs(VIDEO_DIR, exist_ok=True)


    def handle(self, event):

        if event.type == EventType.PRESENCE_START:
            self._start_recording(event)

        elif event.type == EventType.PRESENCE_END:
            self._stop_recording(event)


    #START
    def _start_recording(self, event):

        frame = event.frame

        if frame is None:
            return

        cam_id = event.cam_id
        height, width = frame.shape[:2]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = f"camera_{cam_id}_{timestamp}.avi"
        path = os.path.join(VIDEO_DIR, filename)

        fourcc = cv2.VideoWriter_fourcc(*"XVID")

        writer = cv2.VideoWriter(
            path,
            fourcc,
            self.fps,
            (width, height)
        )

        if not writer.isOpened():
            print("[VIDEO] Failed to open VideoWriter")
            return

        self._writers[cam_id] = {
            "writer": writer,
            "path": path
        }

        print(f"[VIDEO] Recording started: {path}")


    #WRITE FRAME
    def write_frame(self, cam_id, frame):

        recording = self._writers.get(cam_id)

        if not recording:
            return

        try:
            recording["writer"].write(frame)
        except Exception as e:
            print("[VIDEO] Frame write error:", e)


    #STOP
    def _stop_recording(self, event):

        cam_id = event.cam_id

        recording = self._writers.get(cam_id)

        if not recording:
            return

        recording["writer"].release()

        print(f"[VIDEO] Recording finished: {recording['path']}")

        del self._writers[cam_id]