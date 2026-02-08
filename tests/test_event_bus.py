from core.events import EventBus, Event, EventType

# Test 1: Basic Event Emission
class FakeHandelr:
    def __init__(self):
        self.received = []
    
    def handle(self, event):
        self.received.append(event)

    def test_event_bus_dispatch():
        bus = EventBus()
        handler = FakeHandelr()

        bus.register(handler)

        event = Event(type=EventType.SYSTEM_ERROR, source="test")
        bus.emit(event)

        assert len(handler.received) == 1
        assert handler.received[0].type == EventType.SYSTEM_ERROR