from utils.snapshot import save_snapshot
from core.events import PresenceStartEvent, SnapshotSavedEvent


def handle_presence_start(event: PresenceStartEvent):
    path = save_snapshot(
        event.frame,
        prefix=f"presence_cam{event.cam_id}"
    )

    event.snapshot_path = path
