# Morse Code Detection Using Machine Learning

A real-time webcam-based Morse code detection and assistive communication prototype. It estimates eye openness using MediaPipe Face Mesh and Eye Aspect Ratio (EAR), classifies blink duration as Morse dots/dashes, and decodes letters into a live text panel.

## Features
- Webcam-based eye landmark tracking
- Smoothed EAR-based blink detection
- Open-eye calibration
- Morse alphabet and digit decoding
- Letter and word pause handling
- Accessible, high-contrast Tkinter dashboard with large message text
- Keyboard shortcuts: `Space` pause/resume, `Esc` stop, `Ctrl+S` save, `Ctrl++`/`Ctrl+-` adjust decoded text size, `Ctrl+0` reset text size
- Adjustable decoded-message text (11–30 pt) with visible A− / A+ / Reset controls
- Save output to `output/decoded_message.txt`
- Timestamped logs in `logs/app.log`

## Requirements
- Windows 10/11
- Python 3.10 (recommended)
- Webcam
- Good, even lighting

## Setup (PowerShell)
```powershell
cd "W:\Major project\AI-Enabled Assistive Communication Through Eye Blink Pattern Analysis"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```
If your existing environment has a newer incompatible MediaPipe/OpenCV, use the clean install below.

### Recommended clean dependency install
```powershell
python -m pip uninstall -y mediapipe opencv-python opencv-contrib-python numpy scipy pillow
pip install -r requirements.txt
```
Do not install `opencv-python` and `opencv-contrib-python` together in this environment; they both provide the `cv2` module.

## Run
```powershell
python app.py
```
Click **Start Camera**, look at the webcam, and keep your eyes open while the calibration runs. Blink naturally:
- Short blink: dot
- Longer blink: dash
- Pause about 1.2 seconds to finish a letter
- Pause about 2.5 seconds to insert a word space

Use **Calibrate** with eyes open if the threshold needs adjustment. Change the values in `config.py` for your camera/lighting.

## Troubleshooting
- **Camera unavailable:** close Teams/Zoom/Camera app; verify Windows Settings → Privacy & security → Camera access; try `CAMERA_INDEX = 1`.
- **MediaPipe has no `solutions`:** reinstall the pinned version: `pip install --force-reinstall mediapipe==0.10.21`.
- **Low detection quality:** face the camera, avoid backlighting, and keep the camera close to eye level.
- **The first calibration:** keep eyes comfortably open; do not stare painfully or force your eyes open.

## Accessibility notes
The app provides a high-contrast palette, large decoded text, adjustable text sizing, keyboard shortcuts, visible status feedback, and state labels. Controls can be reached using normal Tkinter keyboard focus traversal (Tab/Shift+Tab); button focus styling is emphasized.

**Accessibility validation status:** These are accessibility-supporting design features, not a claim of WCAG 2.0 or Section 508 conformance. Tkinter screen-reader behavior depends on the operating system and accessibility tooling. Before making a standards-based claim, manually evaluate applicable criteria (for example, text contrast, keyboard operation, focus visibility, and text resizing) and document the test results. A future web front end should use semantic HTML, visible focus, ARIA live regions, and WCAG testing.

## Architecture
```mermaid
flowchart LR
    A[Webcam] --> B[OpenCV Frame Capture]
    B --> C[MediaPipe Face Mesh]
    C --> D[Eye Landmark Coordinates]
    D --> E[EAR + Smoothing]
    E --> F[Blink Duration Classifier]
    F --> G[Morse Decoder]
    G --> H[Accessible Tkinter UI]
    H --> I[Save Text / Logs]
```

## Resume description
**AI-Enabled Assistive Communication Through Eye Blink Pattern Analysis** — Developed a real-time webcam-based assistive communication prototype using Python, OpenCV, and MediaPipe Face Mesh. Implemented EAR-based eye-state estimation, calibration and blink-duration classification, Morse-code decoding, and a high-contrast Tkinter interface with keyboard controls, live status metrics, and text export.

## Limitations
This is a learning/resume prototype, not a clinically validated assistive device. Blink timing varies by user and environment. It should not be used as the sole method for emergency or critical communication.

## License
MIT — see `LICENSE`.
