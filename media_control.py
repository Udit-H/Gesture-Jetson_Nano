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

# Cooldowns to prevent command "ghosting"
LAST_ACTION_TIME = 0
VOL_COOLDOWN = 0.2  # Fast for volume
MEDIA_COOLDOWN = 1.0 # Slow for play/pause

# Download model if missing
if not os.path.exists(model_path):
    print("Downloading model...")
    model_url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
    urllib.request.urlretrieve(model_url, model_path)

# --- INITIALIZE MEDIAPIPE ---
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
# NOTE: When moving to Jetson Nano, uncomment the line below for GPU boost:
# base_options = mp.tasks.BaseOptions(model_asset_path=model_path, delegate=mp.tasks.BaseOptions.Delegate.GPU)

options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

# --- GESTURE LOGIC ---
def get_gesture(landmarks):
    """
    Landmark Indices:
    8: Index Tip, 6: Index PIP joint
    12: Middle Tip, 10: Middle PIP joint
    16: Ring Tip, 20: Pinky Tip
    """
    # Check if fingers are extended (y is lower for tips)
    index_up = landmarks[8].y < landmarks[6].y
    middle_up = landmarks[12].y < landmarks[10].y
    ring_up = landmarks[16].y < landmarks[14].y
    pinky_up = landmarks[20].y < landmarks[18].y

    # 1. PALM (All fingers up) -> Play/Pause
    if index_up and middle_up and ring_up and pinky_up:
        return "PALM_PLAY_PAUSE"

    # 2. INDEX UP (Only index up) -> Volume Up
    if index_up and not middle_up and not ring_up:
        return "INDEX_UP_VOL"

    # 3. FIST (All fingers down) -> Mute
    if not index_up and not middle_up and not ring_up:
        return "FIST_MUTE"
    
    return "NONE"

# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)
cap.set(3, CAM_W)
cap.set(4, CAM_H)

prev_frame_time = 0
current_gesture = "NONE"

while cap.isOpened():
    start_inference = time.time()
    
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Process
    results = detector.detect(mp_image)
    
    # Latency calculation
    latency_ms = (time.time() - start_inference) * 1000
    
    current_time = time.time()
    gesture_name = "NONE"

    if results.hand_landmarks:
        hand_landmarks = results.hand_landmarks[0]
        gesture_name = get_gesture(hand_landmarks)
        
        # Trigger Actions with specific cooldowns
        if gesture_name == "PALM_PLAY_PAUSE":
            if current_time - LAST_ACTION_TIME > MEDIA_COOLDOWN:
                pyautogui.press('playpause')
                LAST_ACTION_TIME = current_time
        
        elif gesture_name == "INDEX_UP_VOL":
            if current_time - LAST_ACTION_TIME > VOL_COOLDOWN:
                pyautogui.press('volumeup')
                LAST_ACTION_TIME = current_time
                
        elif gesture_name == "FIST_MUTE":
            if current_time - LAST_ACTION_TIME > MEDIA_COOLDOWN:
                pyautogui.press('volumemute')
                LAST_ACTION_TIME = current_time

        # Draw Landmarks
        #[Image of MediaPipe hand landmark points with ID labels]
        for lm in hand_landmarks:
            x, y = int(lm.x * CAM_W), int(lm.y * CAM_H)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

    # --- UI OVERLAY ---
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time) if (new_frame_time - prev_frame_time) > 0 else 0
    prev_frame_time = new_frame_time

    # Dashboard
    cv2.rectangle(frame, (5, 5), (220, 110), (40, 40, 40), -1)
    cv2.putText(frame, f"FPS: {int(fps)}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Latency: {int(latency_ms)}ms", (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"Action: {gesture_name}", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow('HCI Media Control', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()