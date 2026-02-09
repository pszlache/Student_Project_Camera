import time
import pytest

from core.handlers.mail_handler import MailHandler
from core.events import PresenceStartEvent, EventType


# Fake NotificationService
class FakeNotificationService:
    def __init__(self, emails):
        self.emails = emails

    def get_recipients_for_camera(self, cam_id):
        return self.emails


# Test: Mail triggered on PRESENCE_START
def test_mail_sent_on_presence_start(monkeypatch):

    fake_service = FakeNotificationService(["test@example.com"])

    handler = MailHandler(
        smtp_host="localhost",
        smtp_port=25,
        username="user",
        password="pass",
        notification_service=fake_service,
        cooldown=60,
        smtp_use_ssl=False
    )

    sent_calls = []

    def fake_send_email(task):
        sent_calls.append(task)

    # Patch internal send method
    monkeypatch.setattr(handler, "_send_email", fake_send_email)

    event = PresenceStartEvent(0, "Cam1", None)

    handler.handle(event)

    # Give worker thread time to process queue
    time.sleep(0.1)

    assert len(sent_calls) == 1
    assert sent_calls[0]["recipients"] == ["test@example.com"]


# Test: Cooldown prevents second email
def test_mail_cooldown(monkeypatch):

    fake_service = FakeNotificationService(["test@example.com"])

    handler = MailHandler(
        smtp_host="localhost",
        smtp_port=25,
        username="user",
        password="pass",
        notification_service=fake_service,
        cooldown=5,
        smtp_use_ssl=False
    )

    sent_calls = []

    def fake_send_email(task):
        sent_calls.append(task)

    monkeypatch.setattr(handler, "_send_email", fake_send_email)

    event = PresenceStartEvent(0, "Cam1", None)

    handler.handle(event)
    time.sleep(0.1)

    handler.handle(event)  # second call within cooldown
    time.sleep(0.1)

    assert len(sent_calls) == 1
