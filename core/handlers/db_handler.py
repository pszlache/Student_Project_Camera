from logs.db import log_presence_start, log_presence_end
from core.events import (
    EventType, 
    PresenceStartEvent,
    PresenceEndEvent,
    SnapshotSavetEvent,
)

class DBHandler:
    def __init__(self):
        self._active_events = {}

    def handle_presence_start(self, event: PresenceStartEvent):
        event_id = log_presence_start(event.camera_name)
        self._active_events[event.cam_id] = event_id

        print(f"[DB] START logged for {event.camera_name} (id={event_id})")

    def handle_presence_end(self, event: PresenceEndEvent):
        event_id = self._active_events.get(event.cam_id)

        if event_id is not None:
            log_presence_end(event_id, event.snapshot_path)
            print(f"[DB] END logged for {event.camera_name} (id={event_id})")

            del self._active_events[event.cam_id]
    
    def handle_snapshot_saved(self, event: SnapshotSavetEvent):
        # snapshot was saved, this is for update path
        event_id = self._active_events.get(event.cam_id)

        if event_id:
            # update snapshots in database
            log_presence_end(event_id, event.snapshot_path)
            print(f"[DB] Snapshot linked to event {event_id}")