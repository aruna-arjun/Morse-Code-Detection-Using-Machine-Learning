"""Thin camera wrapper with explicit error handling."""
import cv2
import config

class Camera:
    def __init__(self, index=config.CAMERA_INDEX):
        self.index = index
        self.capture = None

    def open(self):
        # DirectShow often behaves better for Windows webcams.
        self.capture = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            self.capture.release()
            self.capture = cv2.VideoCapture(self.index)
        if not self.capture.isOpened():
            self.capture = None
            raise RuntimeError(
                "Could not open webcam. Close other camera apps, check Windows camera permissions, "
                "or change CAMERA_INDEX in config.py."
            )
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        return self

    def read(self):
        if self.capture is None:
            return False, None
        return self.capture.read()

    def release(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
