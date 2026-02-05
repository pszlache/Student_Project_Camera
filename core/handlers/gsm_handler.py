from core.events import EventType


class GSMHandler:

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
            f"[GSM] SMS SEND -> Presence detected on "
            f"{event.camera_name} (cam_id={event.cam_id})"
        )

        # Docelowo:
        # self._send_sms(message)

    def _handle_presence_end(self, event):

        print(
            f"[GSM] Presence ended on "
            f"{event.camera_name} (cam_id={event.cam_id})"
        )

    def _send_sms(self, message):
        """
        Future production implementation
        using SIM7070G via UART.
        """
        print("[GSM] Sending SMS:", message)
