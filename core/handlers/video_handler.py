import cv2
import os
from datetime import datetime
from core.events import EventType


VIDEO_DIR = "recordings"


class VideoRecorderHandler:

    def __init__(self, fps=15.0):
        self._active_recordings = {}
        self.fps = fps
        os.makedirs(VIDEO_DIR, exist_ok=True)

    def handle(self, event):

        if event.type == EventType.PRESENCE_START:
            self._start_recording(event)

        elif event.type == EventType.PRESENCE_UPDATE:
            self._write_frame(event)

        elif event.type == EventType.PRESENCE_END:
            self._stop_recording(event)

    def _start_recording(self, event):

        frame = event.frame
        if frame is None:
            return

        cam_id = event.cam_id
        height, width = frame.shape[:2]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"camera_{cam_id}_{timestamp}.mp4"
        path = os.path.join(VIDEO_DIR, filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        writer = cv2.VideoWriter(
            path,
            fourcc,
            self.fps,
            (width, height)
        )

        if not writer.isOpened():
            print("[VIDEO] Failed to open VideoWriter")
            return

        self._active_recordings[cam_id] = {
            "writer": writer,
            "path": path
        }

        print(f"[VIDEO] Recording started: {path}")

    def _write_frame(self, event):

        recording = self._active_recordings.get(event.cam_id)

        if recording and event.frame is not None:
            recording["writer"].write(event.frame)

    def _stop_recording(self, event):

        recording = self._active_recordings.get(event.cam_id)

        if not recording:
            return

        recording["writer"].release()

        print(f"[VIDEO] Recording finished: {recording['path']}")

        del self._active_recordings[event.cam_id]

