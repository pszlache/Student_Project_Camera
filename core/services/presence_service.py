import time
from core.events import (
    PresenceStartEvent,
    PresenceEndEvent
)
class PresenceServices:
    
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

    def update(self, frame):
        now = time.time()

        #MOTION
        if self.motion_detect(frame):
            self.ai_counter += 1

            #AI
            if self.ai_counter % self.ai_frame_skip == 0:
                detected = self.detector.detect(frame)

                if detected:
                    self.last_presence_time = now

                    if not self.presence_active:
                        self. presence_active = True

                        self.event_bus.emit(
                            PresenceStartEvent(
                                self.cam_id,
                                self.camera_name,
                                frame
                            )
                        )
        else:
            self.ai_counter = 0

        #TIMEOUT
        if(
            self.presence_active
            and now - self.last_presence_time > self.presence_timeout
        ):
            self.presence_active = False

            self.event_bus.emit(
                PresenceEndEvent(
                    self.cam_id,
                    self.camera_name
                )
            )