from core.events import (
    EventType,
    SnapshotSavedEvent
)

from utils.snapshot import save_snapshot


class SnapshotHandler:

    def __init__(self, event_bus):
        self.event_bus = event_bus

    def handle(self, event):

        # Snapshot przy rozpoczęciu wtargnięcia
        if event.type == EventType.PRESENCE_START:
            self._handle_snapshot(event)

        # Snapshot co 15 sekund
        elif event.type == EventType.SNAPSHOT_TIMER:
            self._handle_snapshot(event)

    def _handle_snapshot(self, event):

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
                event.camera_name if hasattr(event, "camera_name") else None,
                path
            )
        )