from enum import Enum, auto
from dataclasses import dataclass, field
import threading
import time


# EVENT TYPES
class EventType(Enum):
    PRESENCE_START = auto()
    PRESENCE_END = auto()
    PRESENCE_UPDATE = auto()
    SNAPSHOT_SAVED = auto()
    SYSTEM_ERROR = auto()

# BASE EVENT
@dataclass
class Event:
    type: EventType
    source: str
    timestamp: float = field(default_factory=time.time)

# SPECIFIC EVENTS
@dataclass(init=False)
class PresenceStartEvent(Event):
    cam_id: int
    camera_name: str
    frame: any = None

    def __init__(self, cam_id: int, camera_name: str, frame=None):
        super().__init__(
            type=EventType.PRESENCE_START,
            source=f"camera_{cam_id}"
        )
        self.cam_id = cam_id
        self.camera_name = camera_name
        self.frame = frame


@dataclass(init=False)
class PresenceUpdateEvent(Event):
    cam_id: int
    frame: any = None

    def __init__(self, cam_id: int, frame=None):
        super().__init__(
            type=EventType.PRESENCE_UPDATE,
            source=f"camera_{cam_id}"
        )
        self.cam_id = cam_id
        self.frame = frame


@dataclass(init=False)
class PresenceEndEvent(Event):
    cam_id: int
    camera_name: str
    snapshot_path: str = None

    def __init__(self, cam_id: int, camera_name: str, snapshot_path=None):
        super().__init__(
            type=EventType.PRESENCE_END,
            source=f"camera_{cam_id}"
        )
        self.cam_id = cam_id
        self.camera_name = camera_name
        self.snapshot_path = snapshot_path


@dataclass(init=False)
class SnapshotSavedEvent(Event):
    cam_id: int
    camera_name: str
    snapshot_path: str

    def __init__(self, cam_id: int, camera_name: str, snapshot_path: str):
        super().__init__(
            type=EventType.SNAPSHOT_SAVED,
            source=f"camera_{cam_id}"
        )
        self.cam_id = cam_id
        self.camera_name = camera_name
        self.snapshot_path = snapshot_path

# EVENT BUS
class EventBus:

    def __init__(self):
        self._handlers = []
        self._lock = threading.Lock()

    def register(self, handler):
        with self._lock:
            self._handlers.append(handler)

    def emit(self, event: Event):

        print(
            f"[EVENT] {event.type.name} | "
            f"Source: {event.source} | "
            f"Time: {event.timestamp}"
        )

        for handler in self._handlers:
            try:
                handler.handle(event)
            except Exception as e:
                print(
                    f"[EventBus] Handler error "
                    f"({handler.__class__.__name__}): {e}"
                )