import time

from core.handlers.gsm_handler import GSMHandler
from core.events import PresenceStartEvent


# Fake GSMClient
class FakeGSMClient:
    def __init__(self):
        self.sent = []

    def send_sms(self, number, message):
        self.sent.append((number, message))
        return "OK"


# Fake SMSService
class FakeSMSService:
    def __init__(self, numbers):
        self.numbers = numbers

    def get_numbers_for_camera(self, cam_id):
        return self.numbers


# Test: SMS sent on PRESENCE_START
def test_sms_sent_on_presence_start():

    fake_client = FakeGSMClient()
    fake_service = FakeSMSService(["+48123456789"])

    handler = GSMHandler(
        gsm_client=fake_client,
        sms_service=fake_service,
        cooldown=60
    )

    event = PresenceStartEvent(0, "Cam1", None)

    handler.handle(event)

    time.sleep(0.1)  # allow worker to process queue

    assert len(fake_client.sent) == 1
    assert fake_client.sent[0][0] == "+48123456789"


# Test: Cooldown works
def test_sms_cooldown():

    fake_client = FakeGSMClient()
    fake_service = FakeSMSService(["+48123456789"])

    handler = GSMHandler(
        gsm_client=fake_client,
        sms_service=fake_service,
        cooldown=5
    )

    event = PresenceStartEvent(0, "Cam1", None)

    handler.handle(event)
    time.sleep(0.1)

    handler.handle(event)
    time.sleep(0.1)

    assert len(fake_client.sent) == 1
