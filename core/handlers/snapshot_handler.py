from core.events import EventType, SnapshotSavedEvent
from utils.snapshot import save_snapshot


class SnapshotHandler:

    def __init__(self, event_bus):
        self.event_bus = event_bus

    def handle(self, event):

        if event.type == EventType.PRESENCE_START:
            self._handle_start(event)

    def _handle_start(self, event):

        if event.frame is None:
            return

        path = save_snapshot(
            event.frame,
            prefix=f"presence_cam{event.cam_id}"
        )

        print(f"[SNAPSHOT] Saved: {path}")

        # Emit snapshot event
        self.event_bus.emit(
            SnapshotSavedEvent(
                event.cam_id,
                event.camera_name,
                path
            )
        )