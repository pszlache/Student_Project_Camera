from src.core.events import (
    EventType,
    SnapshotSavedEvent
)

from utils.snapshot import save_snapshot


class SnapshotHandler:

    def __init__(self, event_bus):
        self.event_bus = event_bus


    def handle(self, event):

        if event.type == EventType.PRESENCE_START:
            self._save(event.frame, event.cam_id, event.camera_name)

        elif event.type == EventType.SNAPSHOT_TIMER:
            self._save(event.frame, event.cam_id, None)


    def _save(self, frame, cam_id, camera_name):

        if frame is None:
            return

        path = save_snapshot(
            frame,
            prefix=f"presence_cam{cam_id}"
        )

        print(f"[SNAPSHOT] Saved: {path}")

        self.event_bus.emit(
            SnapshotSavedEvent(
                cam_id,
                camera_name,
                path
            )
        )