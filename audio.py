"""Optional non-blocking system beep feedback; safe if unavailable."""
import threading
try:
    import winsound
except ImportError:
    winsound = None

def beep(symbol="."):
    if winsound is None:
        return
    duration = 100 if symbol == "." else 250
    frequency = 850 if symbol == "." else 600
    threading.Thread(target=lambda: winsound.Beep(frequency, duration), daemon=True).start()
