# Gesture Control — Jetson Nano HCI Prototype

Real-time hand gesture recognition for media control, powered by **MediaPipe** and **OpenCV**.  
A minimalist web dashboard streams the camera feed and displays live gesture metrics.

---

## Gestures

| Gesture | Action | Key |
|---------|--------|-----|
| 🖐 Open Palm | Play / Pause | `playpause` |
| ☝️ Index Up | Volume Up | `volumeup` |
| ✊ Fist | Mute | `volumemute` |

## Quick Start

> **Requires Python 3.10 – 3.12** (MediaPipe is not yet compatible with 3.13 on Windows).

```bash
# 1. Clone and enter the repo
git clone https://github.com/Udit-H/Gesture-Jetson_Nano.git
cd Gesture-Jetson_Nano

# 2. Create a venv with a compatible Python version
py -3.12 -m venv venv        # Windows
python3.12 -m venv venv      # macOS / Linux

# 3. Activate and install
.\venv\Scripts\activate       # Windows
source venv/bin/activate      # macOS / Linux
pip install -r requirements.txt

# 4. Run the dashboard
python app.py
```

Open **http://localhost:5000** in your browser.

## Project Structure

```
├── app.py                  # Flask server + gesture engine
├── cursor.py               # Standalone cursor-control script
├── media_control.py        # Standalone media-control script
├── requirements.txt
├── static/
│   └── style.css           # Minimalist black & white theme
└── templates/
    └── index.html          # Dashboard UI
```

## Tech Stack

- **MediaPipe** — Hand landmark detection (21-point model)
- **OpenCV** — Camera capture & frame processing
- **Flask** — Lightweight MJPEG streaming server
- **PyAutoGUI** — System-level keyboard simulation

## Notes

- The `hand_landmarker.task` model is downloaded automatically on first run.
- For Jetson Nano deployment, enable the GPU delegate in `app.py` for better performance.
