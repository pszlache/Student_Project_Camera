from core.handlers.db_handler import DBHandler
from core.events import PresenceStartEvent, PresenceEndEvent

def test_db_handler_start_and_end(monkeypatch):
    
    fake_start_called = []
    fake_end_called = []

    def fake_log_start(name):
        fake_start_called
        return 123
    
    def fake_log_end(event_id, snapshot_path):
        fake_end_called

    monkeypatch.setattr("core.handlers.db_handler.log_presence_start", fake_log_start)
    monkeypatch.setattr("core.handlers.db_handler.log_presence_end", fake_log_end)

    handler = DBHandler()

    start_event = PresenceStartEvent(0, "Cam1", None)
    handler.handle(start_event)

    end_event = PresenceEndEvent(0, "Cam1")
    handler

    assert fake_start_called == ["Cam1"]
    assert fake_end_called[0][0] == 123