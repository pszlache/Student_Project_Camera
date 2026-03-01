# CAMERA_SETUP
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 15

# Motion Detection
MOTION_THRESHOLD = 2000
BLUR_SIZE = (21, 21)
MIN_DELTA = 25

# SNAPSHOTS
SNAPSHOT_DIR = "snapshots"

# AI Configuration
AI_MODEL_DIR = "models"
AI_CONFIDENCE = 0.4
AI_FRAME_SKIP = 1

# MULTI-CAMERA CONFIG
CAMERAS = {
    0:{
        "name": "FirstCam",
        "index": 0
    },
    1:{
        "name": "SecondCam",
        "index": 1
    }
}

PRESENCE_TIMEOUT = 3  # seconds

# SMTP CONFIGURATION
SMTP_USE_SSL = True
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

SMTP_USERNAME = "twojmail@gmail.com"
SMTP_PASSWORD = "tutaj_wklej_haslo_aplikacyjne"

MAIL_COOLDOWN = 60

# GSM CONFIG
GSM_ENABLED = True
GSM_PORT = "/dev/serial0"
GSM_BAUDRATE = 115200
GSM_COOLDOWN = 300 # per camera, in seconds