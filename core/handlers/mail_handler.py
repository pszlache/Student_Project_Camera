import threading
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

from core.events import EventType


class MailHandler:

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

    def handle(self, event):
        if event.type != EventType.PRESENCE_START:
            return

        recipients = self.notification_service.get_recipients_for_camera(event.cam_id)

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

        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = ", ".join(task["recipients"])
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            if self.smtp_use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()

            server.login(self.username, self.password)
            server.sendmail(
                self.username,
                task["recipients"],
                msg.as_string()
            )
            server.quit()

            print(f"[MAIL] Sent to {len(task['recipients'])} recipient(s)")

        except Exception as e:
            print(f"[MAIL] SMTP error: {e}")