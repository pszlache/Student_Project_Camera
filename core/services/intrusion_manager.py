import time
import threading


class IntrusionManager:

    def __init__(self, reset_timeout=60):

        self.reset_timeout = reset_timeout

        # stan alarmu
        self.intrusion_active = False
        self.first_camera = None
        self.last_activity = 0

        # aktywne kamery podczas wtargnięcia
        self.active_cameras = set()

        # ochrona przed race condition (handlers działają w wątkach)
        self._lock = threading.Lock()


    def handle_presence_start(self, cam_id):

        now = time.time()

        with self._lock:

            self.last_activity = now
            self.active_cameras.add(cam_id)

            # pierwszy alarm
            if not self.intrusion_active:

                self.intrusion_active = True
                self.first_camera = cam_id

                print(f"[INTRUSION] Started by camera {cam_id}")

                return True

            # kolejne kamery
            return False


    def handle_presence_end(self, cam_id):

        with self._lock:

            if cam_id in self.active_cameras:
                self.active_cameras.remove(cam_id)

            self.last_activity = time.time()


    def should_reset(self):

        with self._lock:

            if not self.intrusion_active:
                return False

            # jeśli jakaś kamera nadal widzi ruch → nie resetujemy
            if self.active_cameras:
                return False

            now = time.time()

            if now - self.last_activity > self.reset_timeout:

                print("[INTRUSION] System reset")

                self.intrusion_active = False
                self.first_camera = None
                self.active_cameras.clear()

                return True

        return False


    def get_first_camera(self):

        with self._lock:
            return self.first_camera