import time
import queue
import threading

from core.events import EventType


class GSMHandler:

    def __init__(self, gsm_client, sms_service, intrusion_manager, cooldown=60):

        self.gsm_client = gsm_client
        self.sms_service = sms_service
        self.intrusion_manager = intrusion_manager
        self.cooldown = cooldown

        self.queue = queue.Queue()

        self.worker = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self.worker.start()


    def handle(self, event):

        print("[GSM] Handler received event:", event.type)

        # ================= PRESENCE END =================

        if event.type == EventType.PRESENCE_END:

            self.intrusion_manager.handle_presence_end(event.cam_id)
            return


        # ================= ONLY START TRIGGERS SMS =================

        if event.type != EventType.PRESENCE_START:
            return


        # ================= INTRUSION DECISION =================

        should_notify = self.intrusion_manager.handle_presence_start(event.cam_id)

        if not should_notify:
            print("[GSM] IntrusionManager blocked notification")
            return


        # ================= GET PHONE NUMBERS =================

        numbers = self.sms_service.get_numbers_for_camera(event.cam_id)

        if not numbers:
            print("[GSM] No phone numbers configured")
            return


        print(f"[GSM] Queueing SMS for {len(numbers)} recipients")

        self.queue.put({
            "numbers": numbers,
            "camera_name": event.camera_name
        })


    # ================= WORKER =================

    def _worker_loop(self):

        while True:

            task = self.queue.get()

            try:

                self._send_sms(task)

            except Exception as e:

                print(f"[GSM] Error sending SMS: {e}")

            finally:

                self.queue.task_done()


    # ================= SEND SMS =================

    def _send_sms(self, task):

        message = f"⚠ ALERT: Wykryto wtargnięcie - kamera {task['camera_name']}"

        for number in task["numbers"]:

            try:

                print(f"[GSM] Sending SMS to {number}")

                response = self.gsm_client.send_sms(number, message)

                print(f"[GSM] Modem response: {response}")

            except Exception as e:

                print(f"[GSM] Failed sending SMS to {number}: {e}")