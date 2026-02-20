"""
Gesture Control Dashboard — Flask + MediaPipe
Real-time hand-gesture recognition for media control on Jetson Nano.
"""

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import pyautogui
import time
import os
import urllib.request
from flask import Flask, render_template, Response, jsonify

# ── App ──────────────────────────────────────────────────────────────
app = Flask(__name__)

# ── Configuration ────────────────────────────────────────────────────
MODEL_PATH = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
CAM_W, CAM_H = 640, 480
JPEG_QUALITY = 70              # Lower = faster streaming, 70 is a good balance
VOL_COOLDOWN = 0.2             # Seconds between volume actions
MEDIA_COOLDOWN = 1.0           # Seconds between play/pause & mute actions

# ── Download model if missing ────────────────────────────────────────
if not os.path.exists(MODEL_PATH):
    print("[INIT] Downloading hand_landmarker model …")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

# ── MediaPipe initialisation ─────────────────────────────────────────
detector = None
mp_error = None

try:
    base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
    )
    detector = vision.HandLandmarker.create_from_options(options)
    print("[INIT] MediaPipe ready.")
except Exception as exc:
    mp_error = str(exc)
    print(f"[INIT] MediaPipe unavailable: {exc}")


# ── Gesture logic ────────────────────────────────────────────────────
GESTURE_MAP = {
    "PLAY_PAUSE": "playpause",
    "VOL_UP":     "volumeup",
    "MUTE":       "volumemute",
}

COOLDOWNS = {
    "PLAY_PAUSE": MEDIA_COOLDOWN,
    "VOL_UP":     VOL_COOLDOWN,
    "MUTE":       MEDIA_COOLDOWN,
}


def classify_gesture(lm):
    """Return gesture name from 21 hand landmarks."""
    index  = lm[8].y < lm[6].y
    middle = lm[12].y < lm[10].y
    ring   = lm[16].y < lm[14].y
    pinky  = lm[20].y < lm[18].y

    if index and middle and ring and pinky:
        return "PLAY_PAUSE"
    if index and not middle and not ring:
        return "VOL_UP"
    if not index and not middle and not ring:
        return "MUTE"
    return "NONE"


# ── Shared state ─────────────────────────────────────────────────────
state = {
    "gesture": "NONE",
    "fps": 0,
    "latency": 0,
    "last_action": 0.0,
}

ENCODE_PARAMS = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]


# ── Camera ───────────────────────────────────────────────────────────
class Camera:
    """Captures frames, runs inference, and triggers system actions."""

    def __init__(self, device=0):
        self.cap = cv2.VideoCapture(device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
        self._prev_t = 0.0

    def release(self):
        self.cap.release()

    def grab_frame(self):
        """Read one frame, run detection, return JPEG bytes or None."""
        if not self.cap.isOpened():
            return None

        ok, frame = self.cap.read()
        if not ok:
            return None

        frame = cv2.flip(frame, 1)
        t0 = time.time()

        # ── Inference ────────────────────────────────────────────────
        gesture = "NONE"
        if detector:
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                results = detector.detect(img)

                if results.hand_landmarks:
                    lm = results.hand_landmarks[0]
                    gesture = classify_gesture(lm)

                    # Draw minimal white dots
                    for pt in lm:
                        x, y = int(pt.x * CAM_W), int(pt.y * CAM_H)
                        cv2.circle(frame, (x, y), 2, (255, 255, 255), -1)

                    # Execute mapped action
                    now = time.time()
                    cd = COOLDOWNS.get(gesture, MEDIA_COOLDOWN)
                    if gesture != "NONE" and now - state["last_action"] > cd:
                        pyautogui.press(GESTURE_MAP[gesture])
                        state["last_action"] = now
            except Exception:
                pass

        # ── Metrics ──────────────────────────────────────────────────
        state["latency"] = int((time.time() - t0) * 1000)
        state["gesture"] = gesture

        now = time.time()
        if self._prev_t > 0:
            state["fps"] = int(1.0 / (now - self._prev_t))
        self._prev_t = now

        # ── Encode ───────────────────────────────────────────────────
        ok, buf = cv2.imencode(".jpg", frame, ENCODE_PARAMS)
        return buf.tobytes() if ok else None


camera = Camera()


# ── Routes ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


def _stream():
    while True:
        frame = camera.grab_frame()
        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )
        else:
            time.sleep(0.05)


@app.route("/video_feed")
def video_feed():
    return Response(_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/status")
def status():
    return jsonify(
        gesture=state["gesture"],
        fps=state["fps"],
        latency=state["latency"],
        error=mp_error,
    )


# ── Entry point ──────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
