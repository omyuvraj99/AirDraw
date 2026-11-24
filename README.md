# AirDraw v0.2.0 — Gesture Editing Update

AirDraw is a webcam-based gesture drawing application built with Python, OpenCV, and MediaPipe. Version 0.2.0 extends the initial index-finger drawing prototype by adding gesture-controlled stroke movement and erasing, together with an on-screen status display.

## Features

- Draw in the air with an index-finger gesture.
- Move a previously drawn stroke with an index-and-middle-finger gesture.
- Erase portions of strokes with a four-finger gesture while the pinky is folded.
- Use an open palm as a neutral gesture to pause drawing actions.
- Switch between the webcam background and a white canvas.
- Save the current canvas as a PNG image.
- Clear all strokes without restarting the application.
- View the active gesture mode in the on-screen status bar.

## Requirements

Before running the project, install or provide the following:

- Python 3.10 or newer
- A working built-in or USB webcam
- The MediaPipe Hand Landmarker model file, `hand_landmarker.task`

The following Python packages are installed from `requirements.txt`:

- **OpenCV (`opencv-python`)** — provides webcam access, drawing, display, and image saving.
- **MediaPipe** — detects hand landmarks used by the drawing gestures.
- **NumPy** — processes image data and creates the white canvas.

## Installation

Open a terminal in the project folder, then run:

```bash
# Optional but recommended: create a separate Python environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Install the required packages
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Start AirDraw
python Airdraw.py
```

> The v0.2 upload replaces the existing `Airdraw.py` file in this repository.

On macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## Hand Landmarker model

This version expects a file named `hand_landmarker.task` in the same folder as `Airdraw.py`.

Download the official MediaPipe Hand Landmarker model from:

```text
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

Place the downloaded `hand_landmarker.task` file beside `Airdraw.py` before running the program. The file is ignored by Git because it is generated or downloaded locally rather than stored in the repository.

## Gesture controls

| Gesture | Action |
| --- | --- |
| Index finger only | Draw a new stroke |
| Index + middle fingers | Select and move a nearby stroke |
| Index + middle + ring fingers, with pinky folded | Erase near the middle-finger cursor |
| Open palm | Neutral mode; drawing and editing are paused |

The drawing brush in this version uses a fixed cyan-yellow colour and fixed thickness. Brush colour and thickness controls are not included in v0.2.0.

## Keyboard controls

| Action | Key |
| --- | --- |
| Toggle white canvas / webcam background | `B` |
| Save the current image | `S` |
| Clear every stroke | `C` |
| Quit the application | `Q` |

Saved images are named `airdraw_1.png`, `airdraw_2.png`, and so on. They are created in the same folder from which the script is run.

## Project structure

```text
AirDraw/
├── Airdraw.py             # Application entry point for v0.2.0
├── requirements.txt        # Required Python packages
├── .gitignore              # Local files excluded from Git tracking
├── README.md               # Project documentation
└── hand_landmarker.task    # Downloaded locally; not committed to Git
```

## Troubleshooting

| Issue | Recommended action |
| --- | --- |
| `ModuleNotFoundError` | Activate the virtual environment and run `python -m pip install -r requirements.txt`. |
| Model cannot be loaded | Confirm that `hand_landmarker.task` is beside `AirDraw2.py`. |
| Webcam does not open | Close applications such as Zoom, Teams, or Camera, then check camera permissions. |
| Hand tracking is unstable | Use even lighting, keep one hand in view, and reduce background clutter. |
| `python` is not recognized | Reinstall Python with **Add Python to PATH** enabled, then open a new terminal. |

## Version history

### v0.2.0 — Gesture Editing Update

- Added stroke selection and movement with index and middle fingers.
- Added gesture-based partial erasing.
- Added open-palm neutral mode.
- Added an on-screen mode/status bar.
- Improved drawing storage by preserving individual strokes.

### v0.1.0 — First Prototype

- Introduced webcam-based index-finger air drawing.
- Added blank canvas mode, image saving, and canvas clearing.

## Credits

Built with [OpenCV](https://opencv.org/) and [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker).
