"""Small reusable geometry and timing helpers."""
import math
import time
from collections import deque

def euclidean(a, b):
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))

def eye_aspect_ratio(points):
    """EAR for six points ordered [outer, upper1, upper2, inner, lower2, lower1]."""
    if len(points) != 6:
        return 0.0
    horizontal = euclidean(points[0], points[3])
    if horizontal <= 1e-6:
        return 0.0
    vertical = euclidean(points[1], points[5]) + euclidean(points[2], points[4])
    return vertical / (2.0 * horizontal)

class FPSCounter:
    def __init__(self):
        self.samples = deque(maxlen=30)
    def tick(self):
        now = time.perf_counter()
        self.samples.append(now)
    @property
    def fps(self):
        if len(self.samples) < 2:
            return 0.0
        elapsed = self.samples[-1] - self.samples[0]
        return (len(self.samples) - 1) / elapsed if elapsed > 0 else 0.0
