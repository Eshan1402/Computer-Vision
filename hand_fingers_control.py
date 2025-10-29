import cv2
import mediapipe as mp
import numpy as np
import subprocess

MIRROR_VIEW = True

# Initialize MediaPipe Hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Initialize the drawing utilities
mp_drawing = mp.solutions.drawing_utils

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

# Function to map distance to volume level
def distance_to_volume(distance, min_dist=0.05, max_dist=0.4, min_vol=0, max_vol=100):
    return np.clip(np.interp(distance, [min_dist, max_dist], [min_vol, max_vol]), min_vol, max_vol)

# Function to set system volume on macOS
def set_volume_mac(volume_level):
    volume_level = int(volume_level)
    subprocess.run(["osascript", "-e", f"set volume output volume {volume_level}"])

# Function to set screen brightness on macOS using `brightness` CLI (0.0 - 1.0)
def set_brightness_mac(brightness_value):
    try:
        brightness_value = float(np.clip(brightness_value, 0.0, 1.0))
        subprocess.run(["brightness", f"{brightness_value:.3f}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

# Map distance to brightness level (0.05 - 1.0) to avoid total black
def distance_to_brightness(distance, min_dist=0.05, max_dist=0.4, min_bri=0.05, max_bri=1.0):
    return float(np.clip(np.interp(distance, [min_dist, max_dist], [min_bri, max_bri]), min_bri, max_bri))

# Start capturing video from the webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Mirror early so drawings/text are not reversed
    if MIRROR_VIEW:
        frame = cv2.flip(frame, 1)

    # Convert the frame to RGB as Mediapipe works with RGB images
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and detect hand landmarks
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        # If handedness info is available, it aligns with the landmarks list order
        handedness_list = results.multi_handedness if results.multi_handedness else []
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Draw hand landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get coordinates of thumb tip and index finger tip
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate the distance between thumb tip and index finger tip
            distance = calculate_distance((thumb_tip.x, thumb_tip.y), (index_tip.x, index_tip.y))

            # Map distance and control based on handedness
            # Left hand => Volume, Right hand => Brightness
            volume_level = distance_to_volume(distance)
            brightness_value = distance_to_brightness(distance)

            # Determine handedness label if present
            hand_label = "Unknown"
            if idx < len(handedness_list):
                try:
                    hand_label = handedness_list[idx].classification[0].label  # "Left" or "Right"
                except Exception:
                    hand_label = "Unknown"

            # If we are showing a mirrored view, invert the label so it matches the visual
            if MIRROR_VIEW and hand_label in ("Left", "Right"):
                hand_label = "Left" if hand_label == "Right" else "Right"

            last_action = ""
            if hand_label == "Left":
                set_volume_mac(volume_level)
                last_action = f"Left→Volume {volume_level:.0f}%"
            elif hand_label == "Right":
                ok = set_brightness_mac(brightness_value)
                suffix = "✓" if ok else "✕"
                last_action = f"Right→Brightness {int(brightness_value*100)}% {suffix}"

            # Display the distance, volume/brightness, and handedness on the frame
            cv2.putText(frame, f'Distance: {distance:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Volume map: {volume_level:.0f}%', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Brightness map: {int(brightness_value*100)}%', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 215, 255), 2)
            cv2.putText(frame, f'Hand: {hand_label}  {last_action}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 215, 255), 2)

    # Display the output frame (already mirrored earlier if enabled)
    cv2.imshow('Hand Gesture Volume Control', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the OpenCV window
video_capture.release()
cv2.destroyAllWindows()
