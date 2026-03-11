import time
import queue
import threading

from core.events import EventType


class GSMHandler:

    def __init__(self, gsm_client, sms_service):

        self.gsm_client = gsm_client
        self.sms_service = sms_service

        self.queue = queue.Queue()

        self.last_sms = 0

        self.worker = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self.worker.start()


    def handle(self, event):

        print("[GSM] Handler received event:", event.type)

        if event.type != EventType.PRESENCE_START:
            return

        if not self.sms_service.intrusion_manager.handle_presence_start(event.cam_id):
            return

        numbers = self.sms_service.get_numbers_for_camera(event.cam_id)

        if not numbers:
            print("[GSM] No phone numbers configured")
            return

        camera_name = getattr(event, "camera_name", f"Camera {event.cam_id}")

        print(f"[GSM] Queueing SMS for {len(numbers)} recipients")

        self.queue.put({
            "numbers": numbers,
            "camera_name": camera_name,
            "timestamp": event.timestamp
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

        message = (
            f"ALERT: Wykryto wtargniecie\n"
            f"Kamera: {task['camera_name']}\n"
            f"Czas: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task['timestamp']))}"
        )

        for number in task["numbers"]:

            try:

                print(f"[GSM] Sending SMS to {number}")

                response = self.gsm_client.send_sms(number, message)

                print(f"[GSM] Modem response: {response}")

            except Exception as e:

                print(f"[GSM] Failed sending SMS to {number}: {e}")