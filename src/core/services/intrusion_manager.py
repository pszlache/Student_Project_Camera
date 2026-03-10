import time
import threading


class IntrusionManager:

    def __init__(self, cooldown=60):

        self.cooldown = cooldown
        self.last_alert = 0
        self.active_cameras = set()
        self._lock = threading.Lock()

    #START PRESENCE
    def handle_presence_start(self, cam_id):

        now = time.time()

        with self._lock:

            self.active_cameras.add(cam_id)
            if now - self.last_alert >= self.cooldown:

                self.last_alert = now

                print(f"[INTRUSION] Alert allowed (camera {cam_id})")

                return True

            print(f"[INTRUSION] Cooldown active (camera {cam_id})")

            return False


    #END PRESENCE
    def handle_presence_end(self, cam_id):

        with self._lock:

            if cam_id in self.active_cameras:
                self.active_cameras.remove(cam_id)

            print(f"[INTRUSION] Camera {cam_id} cleared")