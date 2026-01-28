from logs.db import log_presence_start, log_presence_end
from core.events import EventType, PresenceStartEvent, PresenceEndEvent


def handle_presence_start(event: PresenceStartEvent):
    event_id = log_presence_start(event.camera_name)
    event.event_id = event_id  # zapisujemy w obiekcie eventu


def handle_presence_end(event: PresenceEndEvent):
    log_presence_end(
        event.snapshot_path,
        event.snapshot_path
    )
