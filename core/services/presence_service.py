import time

from core.events import (
    PresenceStartEvent,
    PresenceEndEvent,
    SnapshotTimerEvent
)


class PresenceService:

    def __init__(
        self,
        cam_id,
        camera_name,
        motion_detector,
        person_detector,
        event_bus,
        ai_frame_skip,
        presence_timeout
    ):

        self.cam_id = cam_id
        self.camera_name = camera_name
        self.motion_detector = motion_detector
        self.person_detector = person_detector
        self.event_bus = event_bus

        self.ai_frame_skip = ai_frame_skip
        self.presence_timeout = presence_timeout

        self.presence_active = False
        self.last_presence_time = 0

        self.ai_counter = 0

        self.last_snapshot_time = 0
        self.snapshot_interval = 15


    def update(self, frame):

        now = time.time()

        motion = self.motion_detector.detect(frame)

        if motion:

            self.ai_counter += 1

            if self.ai_counter % self.ai_frame_skip == 0:

                detected = self.person_detector.detect(frame)

                if detected:

                    self.last_presence_time = now

                    # ================= START =================

                    if not self.presence_active:

                        self.presence_active = True
                        self.last_snapshot_time = now

                        self.event_bus.emit(
                            PresenceStartEvent(
                                self.cam_id,
                                self.camera_name,
                                frame
                            )
                        )

                    # ================= SNAPSHOT TIMER =================

                    elif now - self.last_snapshot_time >= self.snapshot_interval:

                        self.last_snapshot_time = now

                        self.event_bus.emit(
                            SnapshotTimerEvent(
                                self.cam_id,
                                frame
                            )
                        )

        else:
            self.ai_counter = 0


        # ================= END =================

        if self.presence_active:

            if now - self.last_presence_time > self.presence_timeout:

                self.presence_active = False
                self.ai_counter = 0

                self.event_bus.emit(
                    PresenceEndEvent(
                        self.cam_id,
                        self.camera_name
                    )
                )