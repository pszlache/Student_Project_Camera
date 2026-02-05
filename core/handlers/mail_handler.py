from core.events import EventType


class MailHandler:

    def __init__(self, enabled=True):
        self.enabled = enabled

    def handle(self, event):

        if not self.enabled:
            return

        if event.type == EventType.PRESENCE_START:
            self._handle_presence_start(event)

        elif event.type == EventType.PRESENCE_END:
            self._handle_presence_end(event)

    def _handle_presence_start(self, event):

        print(
            f"[MAIL] Presence detected on {event.camera_name} "
            f"(cam_id={event.cam_id})"
        )

        # Tu docelowo:
        # self._send_email(subject, body, attachment)

    def _handle_presence_end(self, event):

        print(
            f"[MAIL] Presence finished on {event.camera_name} "
            f"(cam_id={event.cam_id})"
        )


    def _send_email(self, subject, body, attachment_path=None):
        """
        Production method (future).
        """
        print(f"[MAIL] Sending email: {subject}")
