import threading
import queue

from core.events import EventType


class MailHandler:

    def __init__(self, email_provider, notification_service, intrusion_manager, cooldown=60):

        self.email_provider = email_provider
        self.notification_service = notification_service
        self.intrusion_manager = intrusion_manager
        self.cooldown = cooldown

        self.queue = queue.Queue()

        self.worker = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self.worker.start()


    def handle(self, event):

        # reagujemy tylko na start wtargnięcia
        if event.type != EventType.PRESENCE_START:
            return

        # IntrusionManager decyduje czy to pierwszy alarm
        should_notify = self.intrusion_manager.handle_presence_start(event.cam_id)

        if not should_notify:
            return

        recipients = self.notification_service.get_recipients_for_camera(
            event.cam_id
        )

        if not recipients:
            return

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
            f"First camera: {task['camera_name']}\n"
            f"Camera ID: {task['cam_id']}\n"
            f"Timestamp: {task['timestamp']}\n"
        )

        self.email_provider.send(
            task["recipients"],
            subject,
            body
        )

        print(f"[MAIL] Sent to {len(task['recipients'])} recipient(s)")