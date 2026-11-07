"""Central configuration for Morse Code Detection Using Machine Learning."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

PROJECT_NAME = "Morse Code Detection Using Machine Learning"
CAMERA_INDEX = 0
FRAME_WIDTH = 960
FRAME_HEIGHT = 540
EAR_THRESHOLD = 0.23
CALIBRATION_SECONDS = 4.0
DOT_MAX_SECONDS = 0.35
DASH_MAX_SECONDS = 1.25
LETTER_GAP_SECONDS = 1.15
WORD_GAP_SECONDS = 2.5
MIN_BLINK_SECONDS = 0.08
SMOOTHING_WINDOW = 5
CAMERA_FPS_TARGET = 30
SAVE_PATH = OUTPUT_DIR / "decoded_message.txt"
LOG_PATH = LOG_DIR / "app.log"

# MediaPipe Face Mesh eye contour landmarks: six points each.
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
