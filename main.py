import time
import signal
import sys
import threading

from src.camera.usb_camera import USBCamera
from src.camera.detect import detect_cameras

from src.motion.motion_detector import MotionDetector
from src.ai.person_detector import PersonDetector

from src.core.repositories.user_repository import UserRepository
from src.core.services.notification_service import NotificationService
from src.core.services.intrusion_manager import IntrusionManager
from src.core.handlers.mail_handler import MailHandler

from src.core.gsm.gsm_client import GSMClient
from src.core.services.sms_service import SMSService
from src.core.handlers.gsm_handler import GSMHandler

from src.web.stream import start_stream, set_shared_cameras

from src.core.events import EventBus
from src.core.services.presence_service import PresenceService

from src.core.handlers.db_handler import DBHandler
from src.core.handlers.video_handler import VideoRecorderHandler
from src.core.handlers.snapshot_handler import SnapshotHandler

from src.core.services.auth_service import AuthService

from src.logs.db import init_db
from config import *

from src.core.notifications.providers.smtp_provider import SMTPProvider


def main():

    print("=== SYSTEM STARTING ===")

    #DATABASE

    init_db()

    auth_service = AuthService()
    auth_service.ensure_default_admin()

    #EVENT BUS
    event_bus = EventBus()

    intrusion_manager = IntrusionManager()

    #HANDLERS
    db_handler = DBHandler()
    video_handler = VideoRecorderHandler(fps=FPS)
    snapshot_handler = SnapshotHandler(event_bus)

    event_bus.register(db_handler)
    event_bus.register(video_handler)
    event_bus.register(snapshot_handler)

    #MAIL
    user_repo = UserRepository()
    notification_service = NotificationService(user_repo)

    email_provider = SMTPProvider(
        SMTP_HOST,
        SMTP_PORT,
        SMTP_USERNAME,
        SMTP_PASSWORD,
        SMTP_USE_SSL
    )

    mail_handler = MailHandler(
        email_provider,
        notification_service,
        intrusion_manager,
        MAIL_COOLDOWN
    )

    event_bus.register(mail_handler)

    #GSM
    print("[MAIN] Initializing GSM modem")

    gsm_client = GSMClient(GSM_PORT)
    gsm_client.connect()

    sms_service = SMSService(user_repo)

    gsm_handler = GSMHandler(
        gsm_client,
        sms_service
    )

    event_bus.register(gsm_handler)

    #CAMERA DETECTION
    detected = detect_cameras()

    if not detected:
        print("No cameras detected")
        return

    cameras = {}

    for cam_id, cfg in detected.items():

        print(f"[MAIN] Initializing camera index {cfg['index']}")

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

    #WEB STREAM
    set_shared_cameras(cameras)

    threading.Thread(
        target=start_stream,
        daemon=True
    ).start()

    print("=== SYSTEM RUNNING ===")

    running = True

    #SHUTDOWN
    def shutdown_handler(signum, frame):

        nonlocal running

        print("\n=== SHUTDOWN SIGNAL RECEIVED ===")

        running = False

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    #MAIN LOOP
    try:

        while running:

            for cam_id, data in cameras.items():

                try:

                    frame = data["camera"].read()

                    if frame is None:
                        continue

                    # VIDEO SAVE ACTIVE FRAME
                    video_handler.write_frame(cam_id, frame)

                    # AI detection
                    data["presence_service"].update(frame)

                except Exception as e:

                    print("[MAIN] Camera loop error:", e)

            time.sleep(0.01)

    finally:

        print("=== STOPPING CAMERAS ===")

        for data in cameras.values():

            try:
                data["camera"].stop()
            except:
                pass

        print("=== SYSTEM SHUTDOWN COMPLETE ===")

        sys.exit(0)


if __name__ == "__main__":
    main()