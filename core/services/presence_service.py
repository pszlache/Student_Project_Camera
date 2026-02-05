import time

from core.events import (
    PresenceStartEvent,
    PresenceEndEvent,
    PresenceUpdateEvent
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

        # Presence state tracking
        self.presence_active = False
        self.last_presence_time = 0
        self.ai_counter = 0

        # Limit how often PRESENCE_UPDATE events are emitted
        self.last_update_emit = 0
        self.update_interval = 0.5  # seconds between update events


    def update(self, frame):

        now = time.time()

        # MOTION DETECTION
        if self.motion_detector.detect(frame):

            self.ai_counter += 1

            # AI CHECK (every N frames)
            if self.ai_counter % self.ai_frame_skip == 0:

                detected = self.person_detector.detect(frame)

                if detected:

                    # Update last detected timestamp
                    self.last_presence_time = now

                    # PRESENCE START
                    if not self.presence_active:
                        self.presence_active = True

                        self.event_bus.emit(
                            PresenceStartEvent(
                                self.cam_id,
                                self.camera_name,
                                frame
                            )
                        )

                    # PRESENCE UPDATE (rate limited)
                    else:
                        if now - self.last_update_emit >= self.update_interval:
                            self.last_update_emit = now

                            self.event_bus.emit(
                                PresenceUpdateEvent(
                                    self.cam_id,
                                    frame
                                )
                            )

        else:
            # Reset AI counter if no motion is detected
            self.ai_counter = 0

        # PRESENCE TIMEOUT CHECK
        if (
            self.presence_active and
            now - self.last_presence_time > self.presence_timeout
        ):
            self.presence_active = False
            self.ai_counter = 0

            self.event_bus.emit(
                PresenceEndEvent(
                    self.cam_id,
                    self.camera_name
                )
            )
