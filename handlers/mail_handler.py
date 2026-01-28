from core.events import PresenceStartEvent


def handle_presence_start(event: PresenceStartEvent):
    print(f"[MAIL] Sending mail for {event.camera_name}")