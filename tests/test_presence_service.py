import time
import pytest

from core.services.presence_service import PresenceService
from core.events import EventType

# Fake components for testing
class FakeMotionDetector:
    def __init__(self, result=True):
        self.result = result
    
    def detect(self, frame):
        return self.result
    
class FakePersonDetector:
    def __init__(self, result=True):
        self.result = result
    
    def detect(self, frame):
        return self.result
    
class FakeEventBus:
    def __init__(self):
        self.events = []
    
    def emit(self, event):
        self.events.append(event)

# Tests
def test_presence_start_emitted():
    motion = FakeMotionDetector(True)
    person = FakePersonDetector(True)
    bus = FakeEventBus

    service = PresenceService(
        cam_id=0,
        camera_name="TestCam",
        motion_detector=motion,
        person_detector=person,
        event_bus=bus,
        ai_frame_skip=1,
        presence_timeout=3,
    )

    service.update(frame=None)

    assert len(bus.events) == 1
    assert bus.events[0].type == EventType.PRESENCE_START