import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import time

# 1. Download the MediaPipe Hand Landmarker model if not already present
model_path = "hand_landmarker.task"
if not os.path.exists(model_path):
    print("Downloading MediaPipe Hand Landmarker model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Model Downloaded!")

# 2. Initialize MediaPipe HandLandmarker (matching @mediapipe/tasks-vision)
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1
)
detector = vision.HandLandmarker.create_from_options(options)

# 3. Setup Webcam & Canvas State
cap = cv2.VideoCapture(0)
width, height = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Persistent transparent canvas for drawing strokes
draw_canvas = np.zeros((height, width, 3), dtype=np.uint8)

blank_mode = False
last_x, last_y = None, None
save_counter = 1

print("\n--- Welcome to Airdraw by Om! ---")
print("Controls:")
print("  - Raise index finger to draw; lower it to stop.")
print("  - Press 'b' to Toggle Blank Mode.")
print("  - Press 's' to Download/Save your drawing.")
print("  - Press 'c' to Clear the canvas.")
print("  - Press 'q' to Quit.\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Failed to access webcam.")
        break

    # Flip horizontally for natural mirror view
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert frame to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    timestamp_ms = int(time.time() * 1000)

    # Detect hand landmarks
    detection_result = detector.detect_for_video(mp_image, timestamp_ms)

    if detection_result.hand_landmarks:
        landmarks = detection_result.hand_landmarks[0]
        index_tip = landmarks[8]  # Index finger tip
        index_pip = landmarks[6]  # Index finger middle joint

        x = int(index_tip.x * width)
        y = int(index_tip.y * height)

        # Draw when index finger is raised above its middle joint
        if index_tip.y < index_pip.y:
            if last_x is not None and last_y is not None:
                cv2.line(draw_canvas, (last_x, last_y), (x, y), (204, 255, 0), 5)
            last_x, last_y = x, y
        else:
            last_x, last_y = None, None
    else:
        last_x, last_y = None, None

    # Handle Blank Mode vs. Camera Mode
    if blank_mode:
        background = np.full((height, width, 3), 255, dtype=np.uint8)  # White background
    else:
        background = frame.copy()

    # Merge drawing canvas onto the background
    gray_canvas = cv2.cvtColor(draw_canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    bg_masked = cv2.bitwise_and(background, background, mask=mask_inv)
    fg_masked = cv2.bitwise_and(draw_canvas, draw_canvas, mask=mask)
    output_frame = cv2.add(bg_masked, fg_masked)

    # Display status text on screen
    cv2.putText(output_frame, "Model Loaded! | [B] Blank Mode  [S] Save  [C] Clear  [Q] Quit",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 2)

    cv2.imshow("Airdraw by Om", output_frame)

    # Keyboard Controls (equivalent to the HTML buttons)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('b'):
        blank_mode = not blank_mode
    elif key == ord('s'):
        filename = f"airdraw_{save_counter}.png"
        cv2.imwrite(filename, output_frame)
        print(f"Saved drawing as {filename}")
        save_counter += 1
    elif key == ord('c'):
        draw_canvas = np.zeros((height, width, 3), dtype=np.uint8)
        print("Canvas cleared.")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
