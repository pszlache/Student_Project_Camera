class SystemState:

    cameras_enabled = True

    @classmethod
    def stop_cameras(cls):

        print("[SYSTEM] Cameras stopped by admin")

        cls.cameras_enabled = False

    @classmethod
    def start_cameras(cls):

        print("[SYSTEM] Cameras started by admin")

        cls.cameras_enabled = True