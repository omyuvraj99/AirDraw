import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import time
import math

# 1. Load or download the MediaPipe Hand Landmarker model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "hand_landmarker.task")
if not os.path.exists(model_path):
    print("Downloading MediaPipe Hand Landmarker model...")
    url = "https://googleapis.com"
    urllib.request.urlretrieve(url, model_path)
    print("Model Downloaded!")

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1
)
detector = vision.HandLandmarker.create_from_options(options)

# 2. Setup Webcam & Canvas State
cap = cv2.VideoCapture(0)
width, height = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

blank_mode = False
save_counter = 1

# Stroke storage: each stroke is a dict {"points": [(x, y), ...], "color": (B, G, R), "thickness": int}
strokes = []
current_stroke = None

# Grab/drag state
grabbed_stroke_idx = None
prev_grab_pos = None

# Brush settings
draw_color = (204, 255, 0)  # Cyan-Yellow
brush_thickness = 5
eraser_radius = 25

last_timestamp_ms = 0


def get_finger_states(landmarks):
    # Thumb: compare tip (4) vs IP joint (3) distance from pinky base (17)
    pinky_mcp = landmarks[17]
    thumb_open = math.hypot(landmarks[4].x - pinky_mcp.x, landmarks[4].y - pinky_mcp.y) > \
                 math.hypot(landmarks[3].x - pinky_mcp.x, landmarks[3].y - pinky_mcp.y)

    # Other 4 fingers: tip y < PIP joint y means extended upward
    index_open = landmarks[8].y < landmarks[6].y
    middle_open = landmarks[12].y < landmarks[10].y
    ring_open = landmarks[16].y < landmarks[14].y
    pinky_open = landmarks[20].y < landmarks[18].y

    return [thumb_open, index_open, middle_open, ring_open, pinky_open]


def find_stroke_at(x, y, threshold=25):
    """Finds the topmost stroke near (x, y) for grabbing."""
    for idx in range(len(strokes) - 1, -1, -1):
        for px, py in strokes[idx]["points"]:
            if math.hypot(px - x, py - y) <= threshold:
                return idx
    return None


def erase_at(x, y, radius):
    """Removes points within radius and splits strokes cleanly if erased in the middle."""
    global strokes
    updated_strokes = []
    for stroke in strokes:
        segment = []
        for px, py in stroke["points"]:
            if math.hypot(px - x, py - y) > radius:
                segment.append((px, py))
            else:
                if len(segment) > 1:
                    updated_strokes.append({
                        "points": segment,
                        "color": stroke["color"],
                        "thickness": stroke["thickness"]
                    })
                segment = []
        if len(segment) > 1:
            updated_strokes.append({
                "points": segment,
                "color": stroke["color"],
                "thickness": stroke["thickness"]
            })
    strokes = updated_strokes


print("\n--- Welcome to Airdraw by Om (Upgraded) ---")
print("Gestures:")
print("  - Open Palm (All 5 fingers): No Function (Neutral)")
print("  - Index Finger Only: Draw")
print("  - Index + Middle Fingers: Select & Grab/Move written strokes")
print("  - Open Palm with Pinky Folded: Eraser")
print("Keyboard:")
print("  - [B] Blank Mode | [S] Save | [C] Clear | [Q] Quit\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Failed to access webcam.")
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Ensure strictly increasing timestamp for MediaPipe VIDEO mode
    timestamp_ms = int(time.monotonic() * 1000)
    if timestamp_ms <= last_timestamp_ms:
        timestamp_ms = last_timestamp_ms + 1
    last_timestamp_ms = timestamp_ms

    detection_result = detector.detect_for_video(mp_image, timestamp_ms)

    mode_label = "NO HAND"
    cursor_info = None  # (x, y, color, radius)

    if detection_result.hand_landmarks:
        landmarks = detection_result.hand_landmarks[0]
        thumb, index, middle, ring, pinky = get_finger_states(landmarks)

        # Coordinates for Index tip (8) and Middle tip (12)
        ix, iy = int(landmarks[8].x * width), int(landmarks[8].y * height)
        mx, my = int(landmarks[12].x * width), int(landmarks[12].y * height)

        # 1. OPEN PALM -> NO FUNCTION
        if thumb and index and middle and ring and pinky:
            mode_label = "PALM (No Function)"
            current_stroke = None
            grabbed_stroke_idx = None
            prev_grab_pos = None

        # 2. PINKY FOLDED (Thumb, Index, Middle, Ring open; Pinky folded) -> ERASER
        elif index and middle and ring and not pinky:
            mode_label = "ERASER"
            current_stroke = None
            grabbed_stroke_idx = None
            prev_grab_pos = None

            # Use middle finger tip (12) as center of palm eraser
            erase_at(mx, my, eraser_radius)
            cursor_info = (mx, my, (0, 0, 255), eraser_radius)

        # 3. INDEX + MIDDLE FINGERS ONLY -> SELECT & GRAB/MOVE
        elif index and middle and not ring and not pinky:
            mode_label = "GRAB / MOVE"
            current_stroke = None

            # Midpoint between index and middle fingertips
            gx, gy = (ix + mx) // 2, (iy + my) // 2
            cursor_info = (gx, gy, (255, 180, 0), 12)

            if grabbed_stroke_idx is None:
                grabbed_stroke_idx = find_stroke_at(gx, gy)
                prev_grab_pos = (gx, gy)
            else:
                dx = gx - prev_grab_pos[0]
                dy = gy - prev_grab_pos[1]
                strokes[grabbed_stroke_idx]["points"] = [
                    (px + dx, py + dy) for (px, py) in strokes[grabbed_stroke_idx]["points"]
                ]
                prev_grab_pos = (gx, gy)

        # 4. INDEX FINGER ONLY -> DRAW
        elif index and not middle and not ring and not pinky:
            mode_label = "DRAW"
            grabbed_stroke_idx = None
            prev_grab_pos = None
            cursor_info = (ix, iy, draw_color, 6)

            if current_stroke is None:
                current_stroke = {
                    "points": [(ix, iy)],
                    "color": draw_color,
                    "thickness": brush_thickness
                }
                strokes.append(current_stroke)
            else:
                current_stroke["points"].append((ix, iy))

        # Any other hand pose -> Neutral
        else:
            mode_label = "NEUTRAL"
            current_stroke = None
            grabbed_stroke_idx = None
            prev_grab_pos = None
    else:
        current_stroke = None
        grabbed_stroke_idx = None
        prev_grab_pos = None

    # Prepare Background
    if blank_mode:
        output_frame = np.full((height, width, 3), 255, dtype=np.uint8)
    else:
        output_frame = frame.copy()

    # Render all saved strokes onto output_frame
    for idx, stroke in enumerate(strokes):
        pts = stroke["points"]
        if len(pts) > 1:
            # Highlight stroke in bright orange when grabbed
            color = (0, 140, 255) if idx == grabbed_stroke_idx else stroke["color"]
            thickness = stroke["thickness"] + 3 if idx == grabbed_stroke_idx else stroke["thickness"]
            for i in range(1, len(pts)):
                cv2.line(output_frame, pts[i - 1], pts[i], color, thickness)

    # Render active gesture cursor
    if cursor_info is not None:
        cx, cy, c_color, c_radius = cursor_info
        cv2.circle(output_frame, (cx, cy), c_radius, c_color, 2)

    # Top Status Bar
    cv2.rectangle(output_frame, (0, 0), (width, 35), (30, 30, 30), -1)
    cv2.putText(
        output_frame,
        f"Mode: {mode_label} | [B] Blank  [S] Save  [C] Clear  [Q] Quit",
        (10, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (0, 255, 180),
        2
    )

    cv2.imshow("Airdraw by Om", output_frame)

    # Keyboard Controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('b'):
        blank_mode = not blank_mode
    elif key == ord('s'):
        filename = f"airdraw_{save_counter}.png"
        cv2.imwrite(filename, output_frame)
        print(f"Saved drawing as {filename}")
        save_counter += 1
    elif key == ord('c'):
        strokes.clear()
        current_stroke = None
        grabbed_stroke_idx = None
        print("Canvas cleared.")
    elif key == ord('q'):
        break

detector.close()
cap.release()
cv2.destroyAllWindows()
