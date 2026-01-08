# CAMERA_SETUP
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 15

# Motion Detection
MOTION_THRESHOLD = 5000
BLUR_SIZE = (21, 21)
MIN_DELTA = 25

# SNAPSHOTS
SNAPSHOT_DIR = "snapshots"

# AI Configuration
AI_MODEL_DIR = "models"
AI_CONFIDENCE = 0.6
AI_FRAME_SKIP = 3

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