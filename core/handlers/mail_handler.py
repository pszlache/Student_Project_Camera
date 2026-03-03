import threading
import queue
import time

from core.events import EventType


class MailHandler:

    def __init__(self, email_provider, notification_service, cooldown=60):
        self.email_provider = email_provider
        self.notification_service = notification_service
        self.cooldown = cooldown

        self.queue = queue.Queue()
        self.last_sent = {}

        self.worker = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self.worker.start()

    def handle(self, event):
        if event.type != EventType.PRESENCE_START:
            return

        recipients = self.notification_service.get_recipients_for_camera(
            event.cam_id
        )

        if not recipients:
            return

        now = time.time()
        last = self.last_sent.get(event.cam_id, 0)

        if now - last < self.cooldown:
            return

        self.last_sent[event.cam_id] = now

        self.queue.put({
            "recipients": recipients,
            "camera_name": event.camera_name,
            "cam_id": event.cam_id,
            "timestamp": event.timestamp
        })

    def _worker_loop(self):
        while True:
            task = self.queue.get()
            try:
                self._send_email(task)
            except Exception as e:
                print(f"[MAIL] Error sending email: {e}")
            finally:
                self.queue.task_done()

    def _send_email(self, task):
        subject = f"ALERT: Presence detected on camera {task['camera_name']}"
        body = (
            f"Intrusion detected.\n\n"
            f"Camera: {task['camera_name']}\n"
            f"Camera ID: {task['cam_id']}\n"
            f"Timestamp: {task['timestamp']}\n"
        )

        self.email_provider.send(
            task["recipients"],
            subject,
            body
        )

        print(f"[MAIL] Sent to {len(task['recipients'])} recipient(s)")