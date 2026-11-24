# AirDraw v0.1.0 — First Prototype

AirDraw is a webcam-based drawing prototype that lets you draw in the air by raising your index finger. It uses MediaPipe hand tracking to find your fingertip and OpenCV to display the live camera canvas.

## Features

- Draw in the air with one raised index finger.
- Toggle between the webcam view and a white canvas.
- Save your current drawing as a PNG image.
- Clear the canvas without restarting the program.
- Automatically downloads the required MediaPipe hand-tracking model on the first run.

## Requirements

Before running the project, install:

- Python 3.10 or newer
- A working webcam
- Internet access for the first launch, so the hand-tracking model can download

The following Python packages are installed using `requirements.txt`:

- **OpenCV** — opens the webcam window, draws lines, and saves images.
- **MediaPipe** — detects your hand and index-finger position.
- **NumPy** — handles image and drawing-canvas data.

## Installation

1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Run the program:

```bash
python "Air draw.py"
```

> On the first launch, the `hand_landmarker.task` model downloads automatically. Keep the file in the same folder as the program after it downloads.

## Controls

| Action | Control |
| --- | --- |
| Draw | Raise your index finger |
| Stop drawing | Lower your index finger |
| Toggle white canvas / webcam | `B` |
| Save drawing | `S` |
| Clear canvas | `C` |
| Quit | `Q` |

Saved images are named `airdraw_1.png`, `airdraw_2.png`, and so on.

## Version history

### v0.1.0 — First Prototype

- Initial webcam hand-tracking drawing application.
- Index-finger drawing gesture.
- Blank canvas mode, saving, and clearing.

## Planned improvements

- Multiple brush colours and sizes.
- Eraser gesture.
- More drawing gestures and an on-screen toolbar.
- Better stroke editing and movement.

## Credits

Built with [OpenCV](https://opencv.org/) and [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker).
