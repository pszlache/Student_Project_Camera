from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Type
import threading
import time


# =====================================================
# EVENT TYPES
# =====================================================

class EventType(Enum):
    PRESENCE_START = auto()
    PRESENCE_END = auto()
    PRESENCE_UPDATE = auto()
    SNAPSHOT_SAVED = auto()
    SYSTEM_ERROR = auto()


# =====================================================
# BASE EVENT
# =====================================================

@dataclass
class Event:
    type: EventType
    source: str
    timestamp: float = field(default_factory=time.time)


# =====================================================
# SPECIFIC EVENTS
# =====================================================

@dataclass
class PresenceStartEvent(Event):
    cam_id: int = None
    camera_name: str = None
    frame: any = None

    def __init__(self, cam_id: int, camera_name: str, frame=None):
        super().__init__(
            type=EventType.PRESENCE_START,
            source=f"camera_{cam_id}"
        )
        self.cam_id = cam_id
        self.camera_name = camera_name
        self.frame = frame


@dataclass
class PresenceEndEvent(Event):
    cam_id: int = None
    camera_name: str = None
    snapshot_path: str = None

    def __init__(self, cam_id: int, camera_name: str, snapshot_path=None):
        super().__init__(
            type=EventType.PRESENCE_END,
            source=f"camera_{cam_id}"
        )
        self.cam_id = cam_id
        self.camera_name = camera_name
        self.snapshot_path = snapshot_path


@dataclass
class SnapshotSavedEvent(Event):
    cam_id: int = None
    camera_name: str = None
    snapshot_path: str = None

    def __init__(self, cam_id: int, camera_name: str, snapshot_path: str):
        super().__init__(
            type=EventType.SNAPSHOT_SAVED,
            source=f"camera_{cam_id}"
        )
        self.cam_id = cam_id
        self.camera_name = camera_name
        self.snapshot_path = snapshot_path


# =====================================================
# EVENT BUS
# =====================================================

class EventBus:

    def __init__(self):
        self._handlers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._lock = threading.Lock()

    def register(self, event_type: EventType, handler: Callable[[Event], None]):
        """
        Register handler for specific event type.
        """
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []

            self._handlers[event_type].append(handler)

    def emit(self, event: Event):
        """
        Emit event to all registered handlers.
        """
        handlers = self._handlers.get(event.type, [])

        print(f"[EVENT] {event.type.name} | Source: {event.source} | Time: {event.timestamp}")

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[EventBus] Handler error for {event.type.name}: {e}")
