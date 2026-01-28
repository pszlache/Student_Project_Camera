from core.events import PresenceStartEvent


def handle_presence_start(event: PresenceStartEvent):
    print(f"[GSM] Sending SMS for {event.camera_name}")
