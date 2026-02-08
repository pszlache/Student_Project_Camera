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

# Test 1
def test_presence_start_emitted():
    motion = FakeMotionDetector(True)
    person = FakePersonDetector(True)
    bus = FakeEventBus()

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

# Test 2
def test_presence_start_not_emitted_twice():
    motion = FakeMotionDetector(True)
    person = FakePersonDetector(True)
    bus = FakeEventBus()

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
    service.update(frame=None)

    start_events = [e for e in bus.events if e.type == EventType.PRESENCE_START]
    assert len(start_events) == 1

# Test 3
def test_presence_end_emitted_after_timeout():
    motion = FakeMotionDetector(True)
    person = FakePersonDetector(True)
    bus = FakeEventBus()

    service = PresenceService(
        cam_id=0,
        camera_name="TestCam",
        motion_detector=motion,
        person_detector=person,
        event_bus=bus,
        ai_frame_skip=1,
        presence_timeout=0.1
    )

    service.update(frame=None)
    time.sleep(0.2)

    motion.result = False
    service.update(frame=None)

    end_events = [e for e in bus.events if e.type == EventType.PRESENCE_END]
    assert len(end_events) == 1

# Test 4
def test_update_rate_limit():
    motion = FakeMotionDetector(True)
    person = FakePersonDetector(True)
    bus = FakeEventBus()

    service = PresenceService(
        cam_id=0,
        camera_name="TestCam",
        motion_detector=motion,
        person_detector=person,
        event_bus=bus,
        ai_frame_skip=1,
        presence_timeout=3
    )

    service.update(frame=None)  # Processed
    service.presence_active = True # Simulate active presence
    
    for _ in range(5):
        service.update(frame=None)  # Should be skipped due to rate limit

    update_events = [e for e in bus.events if e.type == EventType.PRESENCE_UPDATE]

    assert len(bus.events) <= 1  # Should only emit for processed frames