from logs.db import log_presence_start, log_presence_end
from core.events import EventType


class DBHandler:

    def __init__(self):
        self._active_events = {}

    def handle(self, event):

        if event.type == EventType.PRESENCE_START:
            self._handle_start(event)

        elif event.type == EventType.PRESENCE_END:
            self._handle_end(event)

    def _handle_start(self, event):

        event_id = log_presence_start(event.camera_name)
        self._active_events[event.cam_id] = event_id

        print(f"[DB] START logged for {event.camera_name} (id={event_id})")

    def _handle_end(self, event):

        event_id = self._active_events.get(event.cam_id)

        if event_id is None:
            return

        log_presence_end(event_id, event.snapshot_path)

        print(f"[DB] END logged for {event.camera_name} (id={event_id})")

        del self._active_events[event.cam_id]
