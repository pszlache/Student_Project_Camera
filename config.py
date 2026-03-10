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
EMAIL_PROVIDER = "smtp"

SMTP_USE_SSL = False
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USERNAME = "example@gmail.com"
SMTP_PASSWORD = "my 16 character app password"

MAIL_COOLDOWN = 60

# GSM CONFIG
GSM_ENABLED = True
GSM_PORT = "/dev/ttyUSB2"
GSM_BAUDRATE = 115200
GSM_COOLDOWN = 300 # per camera, in seconds