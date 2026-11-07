# Morse Code Detection Using Machine Learning

A real-time, webcam-based Morse code detection and assistive communication system that converts eye blinks into readable text. The application uses **MediaPipe Face Mesh, Eye Aspect Ratio (EAR), and Python-based blink classification** to detect Morse code signals and decode them into letters, numbers, and words.

## Key Features

- **Real-Time Eye Tracking:** Uses MediaPipe Face Mesh to detect facial landmarks and track eye movements through a webcam.
- **Blink Detection:** Implements Eye Aspect Ratio (EAR) with smoothing techniques to identify eye blinks accurately.
- **Morse Code Classification:** Classifies short and long blinks into Morse dots and dashes.
- **Automatic Decoding:** Converts Morse sequences into letters and digits using Morse code mapping.
- **Pause-Based Recognition:** Detects letter and word boundaries using configurable time intervals.
- **Open-Eye Calibration:** Provides an initial calibration process to adapt detection thresholds to individual users.
- **Accessible Dashboard:** Features a high-contrast Tkinter interface with large, adjustable decoded text.
- **Message Management:** Supports saving decoded messages to a text file.
- **Keyboard Accessibility:** Includes shortcuts for pausing, resuming, saving messages, and adjusting text size.

## Technology Stack

- **Programming Language:** Python 3.10
- **Computer Vision:** OpenCV
- **Facial Landmark Detection:** MediaPipe Face Mesh
- **Blink Detection:** Eye Aspect Ratio (EAR)
- **Graphical User Interface:** Tkinter
- **Data Storage:** Text files and application logs

## System Workflow

1. Capture real-time video through the webcam.
2. Detect facial and eye landmarks using MediaPipe Face Mesh.
3. Calculate the Eye Aspect Ratio to estimate eye openness.
4. Identify blink duration and classify signals as dots or dashes.
5. Decode Morse sequences into corresponding characters.
6. Display the decoded message in the live dashboard.

## Installation and Execution

### Requirements

- Windows 10/11
- Python 3.10 (recommended)
- Webcam
- Proper lighting conditions

### Run the Application
```
python app.py
```

Click **Start Camera** and keep your eyes open during calibration. Once calibration is complete, blink naturally to communicate using Morse code.

### Morse Code Input

- Short blink: Dot (.)
- Long blink: Dash (-)
- Approximately 1.2-second pause: Complete current letter
- Approximately 2.5-second pause: Insert a word space

Use the **Calibrate** option to adjust the eye-openness threshold when required.


## Accessibility Features

- High-contrast user interface.
- Large and adjustable decoded-message text.
- Keyboard-accessible controls.
- Visible application status and feedback.
- Emphasized keyboard focus styling.

## Limitations and Future Improvements

This project is an educational prototype and has not been clinically validated as an assistive communication device. Blink duration may vary depending on individual users, lighting, and environmental conditions.

Potential future enhancements include:

- Personalized blink-duration calibration.
- Improved noise filtering and blink classification.
- Multilingual message decoding.
- Speech-to-text and text-to-speech integration.
- Web-based deployment for broader accessibility.

## Project Objective

The primary objective is to explore how computer vision and machine learning techniques can support accessible communication by translating eye-blink patterns into meaningful text.