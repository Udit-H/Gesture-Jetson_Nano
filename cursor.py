import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import pyautogui
import time
import os
import urllib.request

# --- CONFIGURATION ---
model_path = 'hand_landmarker.task'
CAM_W, CAM_H = 640, 480
# Action cooldown to prevent "spamming" commands (0.8 seconds)
COOLDOWN_TIME = 0.8 
last_action_time = 0

# Download model if missing
if not os.path.exists(model_path):
    print("Downloading model...")
    model_url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
    urllib.request.urlretrieve(model_url, model_path)

# --- INITIALIZE MEDIAPIPE ---
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
# On Jetson Nano, you would add: delegate=mp.tasks.BaseOptions.Delegate.GPU
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

# --- UTILITY FUNCTIONS ---
def get_gesture(landmarks):
    """Simple logic to detect hand state"""
    # Landmark indices: 8=IndexTip, 12=MiddleTip, 4=ThumbTip
    # A finger is "open" if the tip is higher (lower Y) than the PIP joint
    index_open = landmarks[8].y < landmarks[6].y
    middle_open = landmarks[12].y < landmarks[10].y
    ring_open = landmarks[16].y < landmarks[14].y
    
    # 1. Open Palm = Play/Pause
    if index_open and middle_open and ring_open:
        return "PALM"
    # 2. Index Pointing Up = Volume Up
    if index_open and not middle_open:
        return "INDEX_UP"
    # 3. Fist = Mute (All closed)
    if not index_open and not middle_open and not ring_open:
        return "FIST"
    
    return "NONE"

# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)
cap.set(3, CAM_W)
cap.set(4, CAM_H)

prev_frame_time = 0

while cap.isOpened():
    start_time = time.time() # Start latency timer
    
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Inference
    results = detector.detect(mp_image)
    
    # Calculate Latency
    inference_time = (time.time() - start_time) * 1000 # in ms
    
    current_gesture = "NONE"
    
    if results.hand_landmarks:
        hand_landmarks = results.hand_landmarks[0]
        current_gesture = get_gesture(hand_landmarks)
        
        # Trigger Actions based on Gesture + Cooldown
        current_time = time.time()
        if current_time - last_action_time > COOLDOWN_TIME:
            if current_gesture == "PALM":
                pyautogui.press('playpause')
                last_action_time = current_time
            elif current_gesture == "INDEX_UP":
                pyautogui.press('volumeup')
                # Lower cooldown for volume to make it feel responsive
                last_action_time = current_time - 0.5 
            elif current_gesture == "FIST":
                pyautogui.press('volumemute')
                last_action_time = current_time

        # Draw visual feedback
        for lm in hand_landmarks:
            x, y = int(lm.x * CAM_W), int(lm.y * CAM_H)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

    # --- PERFORMANCE OVERLAY ---
    # Calculate FPS
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time

    # Display Metrics
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, f"Latency: {int(inference_time)}ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"Gesture: {current_gesture}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Jetson Nano HCI Prototype', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()