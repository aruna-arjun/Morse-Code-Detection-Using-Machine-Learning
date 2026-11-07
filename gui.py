"""Tkinter UI. Camera processing runs on a worker thread; UI updates stay on Tk thread."""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import queue
import time
from pathlib import Path
import config
from camera import Camera
from blink_detector import BlinkDetector
from morse_decoder import MorseDecoder
from utils import FPSCounter
from logger import get_logger
from audio import beep

log = get_logger()

class AssistiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.PROJECT_NAME)
        self.root.geometry("1080x800")
        self.root.minsize(900, 700)
        self.root.configure(bg="#101820")
        self.queue = queue.Queue()
        self.worker = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.camera = None
        self.detector = None
        self.decoder = MorseDecoder(config.LETTER_GAP_SECONDS, config.WORD_GAP_SECONDS)
        self.fps = FPSCounter()
        self.started_at = None
        self.blink_count = 0
        self.last_ear = 0.0
        self.camera_present = False
        self.message_font_size = 15
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Escape>", lambda _e: self.stop())
        self.root.bind("<space>", lambda _e: self.toggle_pause())
        self.root.bind("<Control-s>", lambda _e: self.save_text())
        # Use bind_all so shortcuts work regardless of which widget currently has focus.
        self.root.bind_all("<KeyPress>", self._handle_accessibility_key, add="+")
        # Explicit focus traversal for consistent Tab / Shift+Tab behavior.
        self.root.bind_all("<Tab>", self._focus_next, add="+")
        self.root.bind_all("<Shift-Tab>", self._focus_previous, add="+")
        self.root.after(40, self._poll_queue)

    def _build_ui(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("TButton", font=("Segoe UI", 11), padding=8,
                        focuscolor="#F9C74F", focusthickness=2)
        style.map("TButton",
                  focuscolor=[("focus", "#F9C74F")],
                  relief=[("pressed", "sunken"), ("focus", "solid"), ("!pressed", "raised")])
        style.configure("TLabel", background="#101820", foreground="#EAF2F8", font=("Segoe UI", 11))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#FFFFFF")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#B9C7D3")
        style.configure("TFrame", background="#101820")

        header = ttk.Frame(self.root, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="Morse Code Detection Using Machine Learning", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Accessible real-time assistive communication prototype • Space: pause/resume • Esc: stop • Ctrl+S: save",
                  style="Sub.TLabel").pack(anchor="w", pady=(4, 0))

        main = ttk.Frame(self.root, padding=(14, 0, 14, 12))
        main.pack(fill="both", expand=True)
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = ttk.Frame(main, width=330)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self.video_label = tk.Label(left, text="Camera is stopped\nSelect Start Camera to begin",
                                   bg="#17232E", fg="#EAF2F8", font=("Segoe UI", 15),
                                   relief="flat", justify="center")
        self.video_label.pack(fill="both", expand=True)
        self.status_var = tk.StringVar(value="Status: Ready")
        ttk.Label(left, textvariable=self.status_var, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=8)

        ttk.Label(right, text="Live metrics", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        self.ear_var = tk.StringVar(value="EAR: —")
        self.fps_var = tk.StringVar(value="FPS: —")
        self.blinks_var = tk.StringVar(value="Blinks: 0")
        self.pattern_var = tk.StringVar(value="Morse: —")
        self.cal_var = tk.StringVar(value="Calibration: not started")
        for var in (self.ear_var, self.fps_var, self.blinks_var, self.pattern_var, self.cal_var):
            ttk.Label(right, textvariable=var, wraplength=300).pack(anchor="w", pady=2)

        ttk.Label(right, text="Decoded message", style="Header.TLabel").pack(anchor="w", pady=(8, 4))
        self.text_box = tk.Text(right, height=6, wrap="word", font=("Consolas", 15),
                                bg="#F4F7FA", fg="#17232E", insertbackground="#17232E",
                                padx=10, pady=8, relief="flat")
        self.text_box.pack(fill="both", expand=True)
        self.text_box.configure(state="disabled")
        self.text_box.bind("<Control-a>", self._select_all)
        self.text_box.configure(takefocus=True)

        # Visible text-size controls make the output easier to read; keyboard
        # shortcuts provide an alternative to mouse interaction.
        text_size_row = ttk.Frame(right)
        text_size_row.pack(fill="x", pady=(4, 0))
        ttk.Label(text_size_row, text="Decoded text size", style="Sub.TLabel").pack(side="left")
        self.decrease_font_btn = ttk.Button(
            text_size_row, text="A−", width=4,
            command=lambda: self._change_message_font(-1), takefocus=True)
        self.decrease_font_btn.pack(side="right", padx=(4, 0))
        self.increase_font_btn = ttk.Button(
            text_size_row, text="A+", width=4,
            command=lambda: self._change_message_font(1), takefocus=True)
        self.increase_font_btn.pack(side="right", padx=(4, 0))
        self.reset_font_btn = ttk.Button(
            text_size_row, text="Reset", width=6,
            command=self._reset_message_font, takefocus=True)
        self.reset_font_btn.pack(side="right", padx=(4, 0))

        controls = ttk.Frame(right)
        controls.pack(fill="x", pady=(6, 0))
        self.start_btn = ttk.Button(controls, text="Start Camera", command=self.start)
        self.start_btn.pack(fill="x", pady=3)
        self.pause_btn = ttk.Button(controls, text="Pause", command=self.toggle_pause, state="disabled")
        self.pause_btn.pack(fill="x", pady=3)
        ttk.Button(controls, text="Calibrate", command=self.calibrate).pack(fill="x", pady=2)
        ttk.Button(controls, text="Reset message", command=self.reset).pack(fill="x", pady=2)
        ttk.Button(controls, text="Save message", command=self.save_text).pack(fill="x", pady=2)
        self.stop_btn = ttk.Button(controls, text="Stop camera", command=self.stop, takefocus=True)
        self.stop_btn.pack(fill="x", pady=3)

        # Ordered focus chain mirrors the controls' visual order.
        self._focus_widgets = [
            self.reset_font_btn, self.increase_font_btn, self.decrease_font_btn,
            self.start_btn, self.pause_btn,
            *[child for child in controls.winfo_children() if isinstance(child, ttk.Button)][2:],
        ]

        ttk.Label(right, text="Blink timing: short = dot • long = dash\nWait briefly to finish a letter; longer pause inserts a space.\nThis prototype is not a medical device.",
                  style="Sub.TLabel", wraplength=300).pack(anchor="w", pady=(5, 0))

    def _handle_accessibility_key(self, event):
        """Handle scaling shortcuts across keyboard layouts and focused widgets."""
        ctrl_pressed = bool(event.state & 0x4)
        if not ctrl_pressed:
            return None

        key = event.keysym.lower()
        if key in ("plus", "equal", "kp_add"):
            self._change_message_font(1)
            return "break"
        if key in ("minus", "underscore", "kp_subtract"):
            self._change_message_font(-1)
            return "break"
        if key in ("0", "kp_0"):
            self._reset_message_font()
            return "break"
        return None

    def _focus_next(self, event=None):
        """Move focus forward through enabled interactive controls."""
        self._move_focus(1)
        return "break"

    def _focus_previous(self, event=None):
        """Move focus backward through enabled interactive controls."""
        self._move_focus(-1)
        return "break"

    def _move_focus(self, direction):
        widgets = [w for w in self._focus_widgets
                   if w.winfo_exists() and str(w.cget("state")) != "disabled"]
        if not widgets:
            return
        current = self.root.focus_get()
        try:
            index = widgets.index(current)
        except ValueError:
            index = -1 if direction > 0 else 0
        widgets[(index + direction) % len(widgets)].focus_set()

    def _select_all(self, event):
        event.widget.tag_add("sel", "1.0", "end")
        return "break"

    def _change_message_font(self, delta):
        """Increase/decrease decoded text size within a comfortable range."""
        self.message_font_size = max(11, min(30, self.message_font_size + delta))
        self.text_box.configure(font=("Consolas", self.message_font_size))
        self.status_var.set(f"Status: Decoded text size {self.message_font_size} pt")
        return "break"

    def _reset_message_font(self):
        self.message_font_size = 15
        self.text_box.configure(font=("Consolas", self.message_font_size))
        self.status_var.set("Status: Decoded text size reset to 15 pt")
        return "break"

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        self.stop_event.clear()
        self.pause_event.clear()
        self.worker = threading.Thread(target=self._camera_loop, daemon=True)
        self.worker.start()
        self.started_at = time.monotonic()
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal", text="Pause")
        self.status_var.set("Status: Starting camera…")

    def _camera_loop(self):
        try:
            self.camera = Camera().open()
            self.detector = BlinkDetector()
            self.detector.begin_calibration()
            self.queue.put(("status", "Status: Camera active — keep eyes open for calibration"))
            calibration = True
            while not self.stop_event.is_set():
                if self.pause_event.is_set():
                    time.sleep(0.08)
                    continue
                ok, frame = self.camera.read()
                if not ok:
                    self.queue.put(("status", "Status: Camera frame unavailable"))
                    time.sleep(0.1)
                    continue
                frame = cv2.flip(frame, 1)
                frame, ear, duration, face_found = self.detector.process(frame, calibrate=calibration)
                if self.detector.calibrated:
                    calibration = False
                    self.queue.put(("cal", f"Calibration: complete • threshold {self.detector.threshold:.3f}"))
                if ear is not None:
                    self.queue.put(("ear", f"EAR: {ear:.3f} • threshold {self.detector.threshold:.3f}"))
                if duration is not None and duration >= config.MIN_BLINK_SECONDS:
                    symbol = "." if duration <= config.DOT_MAX_SECONDS else "-"
                    if duration > config.DASH_MAX_SECONDS:
                        self.queue.put(("status", "Status: Blink was too long; ignored"))
                    else:
                        self.decoder.add_symbol(symbol, time.monotonic())
                        self.queue.put(("pattern", f"Morse: {self.decoder.pattern or '—'}"))
                        self.queue.put(("blinks", f"Blinks: {self.detector.blink_count}"))
                        beep(symbol)
                decoded = self.decoder.update(time.monotonic())
                if decoded:
                    self.queue.put(("text", self.decoder.text))
                    self.queue.put(("pattern", f"Morse: {self.decoder.pattern or '—'}"))
                self.fps.tick()
                self.queue.put(("fps", f"FPS: {self.fps.fps:.1f}"))
                if not face_found:
                    self.queue.put(("status", "Status: No face detected — adjust lighting/position"))
                small = cv2.resize(frame, (800, 450))
                self.queue.put(("frame", small))
        except Exception as exc:
            log.exception("Camera worker failed")
            self.queue.put(("error", str(exc)))
        finally:
            if self.detector:
                try: self.detector.close()
                except Exception: pass
                self.detector = None
            if self.camera:
                self.camera.release()
                self.camera = None
            self.queue.put(("stopped", None))

    def _poll_queue(self):
        try:
            while True:
                kind, value = self.queue.get_nowait()
                if kind == "frame":
                    rgb = cv2.cvtColor(value, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(rgb)
                    photo = ImageTk.PhotoImage(image=image)
                    self.video_label.configure(image=photo, text="")
                    self.video_label.image = photo
                elif kind == "text":
                    self.text_box.configure(state="normal")
                    self.text_box.delete("1.0", "end")
                    self.text_box.insert("1.0", value)
                    self.text_box.configure(state="disabled")
                elif kind == "status": self.status_var.set(value)
                elif kind == "ear": self.ear_var.set(value)
                elif kind == "fps": self.fps_var.set(value)
                elif kind == "blinks": self.blinks_var.set(value)
                elif kind == "pattern": self.pattern_var.set(value)
                elif kind == "cal": self.cal_var.set(value)
                elif kind == "error":
                    self.status_var.set("Status: Error")
                    messagebox.showerror("Camera / detection error", value)
                elif kind == "stopped":
                    self.start_btn.configure(state="normal")
                    self.pause_btn.configure(state="disabled", text="Pause")
                    self.status_var.set("Status: Stopped")
                    self.video_label.configure(image="", text="Camera is stopped\nSelect Start Camera to begin")
                    self.video_label.image = None
        except queue.Empty:
            pass
        self.root.after(40, self._poll_queue)

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_btn.configure(text="Pause")
            self.status_var.set("Status: Resumed")
        else:
            self.pause_event.set()
            self.pause_btn.configure(text="Resume")
            self.status_var.set("Status: Paused")

    def calibrate(self):
        if self.detector:
            self.queue.put(("cal", "Calibration: keep eyes open for 4 seconds"))
            self.detector.begin_calibration()
            self.status_var.set("Status: Calibration started")
        else:
            messagebox.showinfo("Calibration", "Start the camera first.")

    def reset(self):
        self.decoder.reset()
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.configure(state="disabled")
        self.pattern_var.set("Morse: —")
        self.blinks_var.set("Blinks: 0")
        self.status_var.set("Status: Message reset")

    def save_text(self):
        config.SAVE_PATH.parent.mkdir(exist_ok=True)
        self.decoder.flush()
        config.SAVE_PATH.write_text(self.decoder.text, encoding="utf-8")
        self.status_var.set(f"Status: Saved to {config.SAVE_PATH}")
        messagebox.showinfo("Saved", f"Message saved to:\n{config.SAVE_PATH}")

    def stop(self):
        self.stop_event.set()
        self.pause_event.clear()

    def on_close(self):
        self.stop()
        self.root.after(200, self.root.destroy)
