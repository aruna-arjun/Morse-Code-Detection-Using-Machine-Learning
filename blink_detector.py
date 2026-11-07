"""MediaPipe-based face landmarks and blink duration classification."""
import time
from collections import deque
import cv2
import mediapipe as mp
import config
from utils import eye_aspect_ratio
from logger import get_logger

log = get_logger()

class BlinkDetector:
    def __init__(self):
        # Use the legacy FaceMesh API. The pinned requirements version includes mp.solutions.
        if not hasattr(mp, "solutions"):
            raise RuntimeError(
                "This MediaPipe build does not expose mp.solutions. "
                "Reinstall the pinned dependency with: pip install mediapipe==0.10.21"
            )
        self.mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.55, min_tracking_confidence=0.55
        )
        self.closed_since = None
        self.was_closed = False
        self.ear_values = deque(maxlen=config.SMOOTHING_WINDOW)
        self.threshold = config.EAR_THRESHOLD
        self.blink_count = 0
        self.calibration_started = None
        self.open_ears = []
        self.calibrated = False

    def begin_calibration(self):
        self.calibration_started = time.monotonic()
        self.open_ears.clear()
        self.calibrated = False

    def process(self, frame, calibrate=False):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mesh.process(rgb)
        ear = None
        landmarks = None
        blink_duration = None
        now = time.monotonic()

        if result.multi_face_landmarks:
            face = result.multi_face_landmarks[0]
            h, w = frame.shape[:2]
            landmarks = face.landmark
            left = [(int(landmarks[i].x*w), int(landmarks[i].y*h)) for i in config.LEFT_EYE]
            right = [(int(landmarks[i].x*w), int(landmarks[i].y*h)) for i in config.RIGHT_EYE]
            raw = (eye_aspect_ratio(left) + eye_aspect_ratio(right)) / 2.0
            self.ear_values.append(raw)
            ear = sum(self.ear_values) / len(self.ear_values)

            if calibrate and self.calibration_started is not None:
                if ear > 0.18:
                    self.open_ears.append(ear)
                if now - self.calibration_started >= config.CALIBRATION_SECONDS:
                    if self.open_ears:
                        # Threshold at a conservative fraction of average open-eye EAR.
                        self.threshold = max(0.14, min(0.32, sum(self.open_ears)/len(self.open_ears)*0.72))
                    self.calibrated = True
                    self.calibration_started = None
                    log.info("Calibration finished; EAR threshold %.3f", self.threshold)

            is_closed = ear < self.threshold
            if is_closed and not self.was_closed:
                self.closed_since = now
            elif not is_closed and self.was_closed and self.closed_since is not None:
                blink_duration = now - self.closed_since
                self.closed_since = None
                if blink_duration >= config.MIN_BLINK_SECONDS:
                    self.blink_count += 1
            self.was_closed = is_closed

            # Draw selected eye landmarks.
            for point in left + right:
                cv2.circle(frame, point, 2, (80, 230, 150), -1)
        else:
            self.was_closed = False
            self.closed_since = None

        return frame, ear, blink_duration, bool(result.multi_face_landmarks)

    def close(self):
        self.mesh.close()
