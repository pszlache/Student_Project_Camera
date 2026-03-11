import threading
import queue

from src.core.events import EventType
from src.core.services.runtime_config import RuntimeConfig


class MailHandler:

    def __init__(self, email_provider, notification_service):

        self.email_provider = email_provider
        self.notification_service = notification_service

        self.queue = queue.Queue()

        self.worker = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self.worker.start()


    def handle(self, event):

        #ONLY START TRIGGERS MAIL
        if event.type != EventType.PRESENCE_START:
            return


        #GET RECIPIENTS
        recipients = self.notification_service.get_recipients_for_camera(
            event.cam_id
        )

        if not recipients:
            print("[MAIL] No recipients configured")
            return


        camera_name = getattr(event, "camera_name", f"Camera {event.cam_id}")

        print(f"[MAIL] Queueing mail for {len(recipients)} recipients")


        self.queue.put({
            "recipients": recipients,
            "camera_name": camera_name,
            "cam_id": event.cam_id,
            "timestamp": event.timestamp
        })


    #WORKER
    def _worker_loop(self):

        while True:

            task = self.queue.get()

            try:
                self._send_email(task)

            except Exception as e:
                print(f"[MAIL] Error sending email: {e}")

            finally:
                self.queue.task_done()


    #SEND MAIL
    def _send_email(self, task):

        #CHECK RUNTIME CONFIG
        cfg = RuntimeConfig.get_mail_config()

        if all([
            cfg["host"],
            cfg["port"],
            cfg["username"],
            cfg["password"]
        ]):

            self.email_provider.host = cfg["host"]
            self.email_provider.port = cfg["port"]
            self.email_provider.username = cfg["username"]
            self.email_provider.password = cfg["password"]

            print("[MAIL] Using runtime SMTP config")

        else:

            print("[MAIL] Using default SMTP config")

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