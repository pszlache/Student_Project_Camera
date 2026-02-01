import cv2
import os
import time
from datetime import datetime
from core.events import EventType, PresenceStartEvent, PresenceEndEvent


VIDEO_DIR = "recordings"


class VideoRecorderHandler:

    def __init__(self):
        self.active_recordings = {}

        os.makedirs(VIDEO_DIR, exist_ok=True)

    # PRESENCE START
    def handle_presence_start(self, event: PresenceStartEvent):
        cam_id = event.cam_id
        frame = event.frame

        if frame is None:
            return

        height, width = frame.shape[:2]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"camera_{cam_id}_{timestamp}.mp4"
        filepath = os.path.join(VIDEO_DIR, filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        writer = cv2.VideoWriter(
            filepath,
            fourcc,
            15.0,
            (width, height)
        )

        self.active_recordings[cam_id] = {
            "writer": writer,
            "path": filepath
        }

        print(f"[VIDEO] Recording started: {filepath}")


    # PRESENCE END
    def handle_presence_end(self, event: PresenceEndEvent):
        cam_id = event.cam_id

        recording = self.active_recordings.get(cam_id)

        if not recording:
            return

        recording["writer"].release()

        print(f"[VIDEO] Recording finished: {recording['path']}")

        event.snapshot_path = recording["path"]

        del self.active_recordings[cam_id]

    # FRAME UPDATE (write frame)
    def write_frame(self, cam_id, frame):
        recording = self.active_recordings.get(cam_id)

        if recording:
            recording["writer"].write(frame)
