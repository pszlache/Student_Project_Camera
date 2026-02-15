import time
import signal
import sys

from camera.usb_camera import USBCamera
from camera.detect import detect_cameras

from motion.motion_detector import MotionDetector
from ai.person_detector import PersonDetector

from core.repositories.user_repository import UserRepository
from core.services.notification_service import NotificationService
from core.handlers.mail_handler import MailHandler

from core.gsm.gsm_client import GSMClient
from core.services.sms_service import SMSService
from core.handlers.gsm_handler import GSMHandler

from web.stream import start_stream, set_shared_cameras

from core.events import EventBus
from core.services.presence_service import PresenceService

from core.handlers.db_handler import DBHandler
from core.handlers.video_handler import VideoRecorderHandler
from core.handlers.snapshot_handler import SnapshotHandler

from core.services.auth_service import AuthService

from logs.db import init_db
from config import *


def main():

    print("=== SYSTEM STARTING ===")

    # INIT DB
    init_db()

    auth_service = AuthService()
    auth_service.ensure_default_admin()
    event_bus = EventBus()

    # HANDLERS
    db_handler = DBHandler()
    video_handler = VideoRecorderHandler(fps=FPS)
    snapshot_handler = SnapshotHandler(event_bus)

    event_bus.register(db_handler)
    event_bus.register(video_handler)
    event_bus.register(snapshot_handler)

    # CAMERA DETECTION
    detected = detect_cameras()

    if not detected:
        print("No cameras detected")
        return

    cameras = {}

    # MAILER
    user_repo = UserRepository()
    notification_service = NotificationService(user_repo)

    mail_handler = MailHandler(
        SMTP_HOST,
        SMTP_PORT,
        SMTP_USERNAME,
        SMTP_PASSWORD,
        notification_service,
        MAIL_COOLDOWN,
        SMTP_USE_SSL
    )
    event_bus.register(mail_handler)

    if GSM_ENABLED:
        gsm_client = GSMClient(GSM_PORT, GSM_BAUDRATE)
        # gsm_client.connect()

        sms_service = SMSService("+48123456789") # test number
        gsm_handler = GSMHandler(
            gsm_client, 
            sms_service, 
            GSM_COOLDOWN
        )

        event_bus.register(gsm_handler)

    for cam_id, cfg in detected.items():

        print(f"[MAIN] Initializing camera {cfg['index']}")

        cam = USBCamera(
            cfg["index"],
            FRAME_WIDTH,
            FRAME_HEIGHT,
            FPS
        )
        cam.start()

        presence_service = PresenceService(
            cam_id,
            cfg["name"],
            MotionDetector(
                BLUR_SIZE,
                MIN_DELTA,
                MOTION_THRESHOLD
            ),
            PersonDetector(
                AI_MODEL_DIR,
                AI_CONFIDENCE
            ),
            event_bus,
            AI_FRAME_SKIP,
            PRESENCE_TIMEOUT
        )

        cameras[cam_id] = {
            "camera": cam,
            "presence_service": presence_service,
            "name": cfg["name"]
        }

    # STREAM
    set_shared_cameras(cameras)
    start_stream()

    print("=== SYSTEM RUNNING ===")

    running = True

    # SIGNAL HANDLER
    def shutdown_handler(signum, frame):
        nonlocal running
        print("\n=== SHUTDOWN SIGNAL RECEIVED ===")
        running = False

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # MAIN LOOP
    try:
        while running:

            for cam_id, data in cameras.items():

                frame = data["camera"].read()
                if frame is None:
                    continue

                data["presence_service"].update(frame)

            time.sleep(0.01)

    finally:
        print("=== STOPPING CAMERAS ===")

        for data in cameras.values():
            data["camera"].stop()

        print("=== SYSTEM SHUTDOWN COMPLETE ===")
        sys.exit(0)


if __name__ == "__main__":
    main()


