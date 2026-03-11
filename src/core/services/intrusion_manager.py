import threading


class IntrusionManager:

    def __init__(self, cooldown=60):

        self.cooldown = cooldown

        # active presence cameras
        self.active_cameras = set()

        # cameras that have already sent an alert and are waiting to be reset
        self.alert_locked = set()

        # reset timers after PRESENCE_END
        self.reset_timers = {}

        self._lock = threading.Lock()


    # START PRESENCE
    def handle_presence_start(self, cam_id):

        with self._lock:

            # cancel reset timer if presence returns
            if cam_id in self.reset_timers:
                self.reset_timers[cam_id].cancel()
                del self.reset_timers[cam_id]

            self.active_cameras.add(cam_id)

            # if alert already sent → block
            if cam_id in self.alert_locked:
                print(f"[INTRUSION] Alert blocked (camera {cam_id})")
                return False

            print(f"[INTRUSION] Alert allowed (camera {cam_id})")

            self.alert_locked.add(cam_id)

            return True


    # END PRESENCE
    def handle_presence_end(self, cam_id):

        with self._lock:

            if cam_id in self.active_cameras:
                self.active_cameras.remove(cam_id)

            print(f"[INTRUSION] Camera {cam_id} cleared")

            # start reset timer
            timer = threading.Timer(
                self.cooldown,
                self._reset_camera,
                args=(cam_id,)
            )

            self.reset_timers[cam_id] = timer
            timer.start()


    # RESET AFTER COOLDOWN
    def _reset_camera(self, cam_id):

        with self._lock:

            if cam_id in self.alert_locked:
                self.alert_locked.remove(cam_id)

            if cam_id in self.reset_timers:
                del self.reset_timers[cam_id]

            print(f"[INTRUSION] Camera {cam_id} reset after cooldown")