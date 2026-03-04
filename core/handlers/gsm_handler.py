import threading
import queue
import time

from core.events import EventType


class GSMHandler:

    def __init__(self, gsm_client, sms_service, cooldown=60, notification_service=None):

        self.gsm_client = gsm_client
        self.sms_service = sms_service
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

        numbers = self.sms_service.get_numbers_for_camera(event.cam_id)

        if not numbers:
            return

        now = time.time()
        last = self.last_sent.get(event.cam_id, 0)

        if now - last < self.cooldown:
            return

        self.last_sent[event.cam_id] = now

        self.queue.put({
            "numbers": numbers,
            "camera_name": event.camera_name,
            "cam_id": event.cam_id
        })

    def _worker_loop(self):

        while True:
            task = self.queue.get()

            try:
                self._send_sms(task)

            except Exception as e:
                print(f"[GSM] Error sending SMS: {e}")

            finally:
                self.queue.task_done()

    def _send_sms(self, task):

        message = f"ALERT: Intrusion detected on camera {task['camera_name']}"

        for number in task["numbers"]:

            try:

                response = self.gsm_client.send_sms(number, message)

                print(f"[GSM] SMS sent to {number}: {response}")

            except Exception as e:

                print(f"[GSM] Failed sending to {number}: {e}")