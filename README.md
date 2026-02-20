# Gesture Control — Jetson Nano HCI Prototype

Real-time hand gesture recognition for **hands-free media control**, powered by **MediaPipe** and **OpenCV**. Works on desktop and embedded systems (Jetson Nano). A minimalist web dashboard streams the camera feed and displays live gesture metrics.

>  **Perfect for:** Living room media centers, presentation mode, accessibility interfaces, and hands-free environments.

---

##  Gestures Supported

| Gesture | Action | Use Case |
|---------|--------|----------|
| 🖐 **Open Palm** | Play / Pause | Toggle media playback |
| ☝️ **Index Finger Up** | Volume Up | Raise audio level |
| ✊ **Fist** | Mute | Silence audio |

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10–3.12** (MediaPipe incompatible with 3.13 on Windows)
- Webcam (USB or built-in)
- ~300 MB disk space (for model download)

### Installation (3 minutes)

```bash
# 1. Clone and enter the repo
git clone https://github.com/Udit-H/Gesture-Jetson_Nano.git
cd Gesture-Jetson_Nano

# 2. Create a virtual environment (Python 3.12 recommended)
py -3.12 -m venv venv                    # Windows
python3.12 -m venv venv                  # macOS / Linux

# 3. Activate and install dependencies
.\venv\Scripts\activate                  # Windows
source venv/bin/activate                 # macOS / Linux
pip install -r requirements.txt

# 4. Launch the dashboard
python app.py
```

🌐 Open **http://localhost:5000** in your browser. The model downloads automatically on first run.

---

##  Usage Modes

### 1️⃣ **Dashboard Mode** (Recommended for Development)
```bash
python app.py
```
- Live camera stream with gesture overlay
- Real-time FPS & latency metrics
- Clean web UI at `http://localhost:5000`

### 2️⃣ **Standalone Media Control** (Headless)
```bash
python media_control.py
```
- No GUI; runs in background
- Direct system media control (Play/Pause, Volume, Mute)
- Ideal for Jetson Nano & server deployments

### 3️⃣ **Cursor Control** (Experimental)
```bash
python cursor.py
```
- Hand position maps to mouse cursor
- Useful for hands-free presentation mode
- Visualizes hand landmarks on screen

---

##  Project Structure

```
Gesture-Jetson_Nano/
├── app.py                        # Flask server + main gesture engine
├── cursor.py                     # Standalone cursor-control script
├── media_control.py              # Standalone media-control script
├── hand_landmarker.task          # MediaPipe model (auto-downloaded)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── PROJECT_REPORT.md             # Detailed technical report
├── static/
│   └── style.css                 # Minimalist dark theme
└── templates/
    └── index.html                # Web dashboard UI
```

---

##  Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Hand Detection** | [MediaPipe](https://mediapipe.dev) | 21-point hand landmark detection |
| **Image Processing** | [OpenCV](https://opencv.org) | Camera capture & frame manipulation |
| **Web Server** | [Flask](https://flask.palletsprojects.com) | MJPEG streaming + REST API |
| **System Control** | [PyAutoGUI](https://pyautogui.readthedocs.io) | Keyboard & system command dispatch |

---

## 📊 Performance Specs

| Metric | Value | Notes |
|--------|-------|-------|
| **Inference Latency** | 20–50 ms | CPU-based (varies by hardware) |
| **FPS** | 20–30 FPS | Dashboard & real-time modes |
| **Gesture Accuracy** | ~95% | Well-lit, frontal poses |
| **Memory Usage** | 200–350 MB | Python runtime + MediaPipe model |
| **Jetson Nano Power** | 3–5W | With GPU delegate enabled |

---

## ⚙️ Configuration

### Camera Settings (in `app.py`)
```python
CAM_W, CAM_H = 640, 480      # Resolution (balance accuracy vs. speed)
JPEG_QUALITY = 70             # Streaming compression (0–100)
```

### Action Cooldowns
```python
MEDIA_COOLDOWN = 1.0          # Play/Pause delay (seconds)
VOL_COOLDOWN = 0.2            # Volume adjust delay (rapid-fire friendly)
```

### Jetson Nano GPU Acceleration
Uncomment in `app.py` or `media_control.py`:
```python
delegate = mp.tasks.BaseOptions.Delegate.GPU  # 3–5× speedup
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"No camera found"** | Check USB connectivity; try `device=1` instead of `device=0` |
| **Low FPS / Latency** | Reduce resolution to 480×360; enable GPU delegate on Jetson |
| **Gesture not detected** | Ensure good lighting (>100 lux); keep hand frontal (avoid side profiles) |
| **Model download fails** | Check internet connection; manually download [hand_landmarker.task](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task) |
| **"MediaPipe not found"** | Verify Python 3.10–3.12 (not 3.13); reinstall: `pip install --upgrade mediapipe` |

---

## 📈 Optimization Tips

1. **For Speed:** Reduce resolution to 480×360 or enable GPU delegate
2. **For Accuracy:** Increase JPEG quality to 80+; improve lighting
3. **For Battery (Jetson):** Enable GPU delegate to reduce CPU usage from 40% → 5%
4. **For Responsiveness:** Lower cooldown timers for frequent actions

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for detailed optimization strategies.

---

##  Use Cases

✅ **Living Room Media Center** – Control TV/audio without remote  
✅ **Presentation Mode** – Navigate slides hands-free  
✅ **Accessibility** – Input method for people with mobility limitations  
✅ **Smart Home Hub** – Gesture-based appliance control  
✅ **Gaming** – Experimental motion control interface

---

## 🚀 Future Enhancements

- [ ] Multi-gesture vocabulary (swipes, pinches, rotations)
- [ ] Hand smoothing with Kalman filter
- [ ] ML-based gesture classification (LSTM/Transformer)
- [ ] Multi-hand simultaneous tracking
- [ ] Voice feedback integration
- [ ] Web API for remote control
- [ ] Dark/Light theme toggle

---

## 📝 Notes

- The `hand_landmarker.task` model (~90 MB) downloads automatically on first run
- For **Jetson Nano deployment**, enable GPU delegate in `app.py` for 3–5× speedup
- Works with any standard USB or built-in webcam
- Compatible with Windows, macOS, and Linux

---

## 📄 Documentation

- **[PROJECT_REPORT.md](PROJECT_REPORT.md)** — Comprehensive technical report (methodology, results, optimization)
- **[MediaPipe Documentation](https://mediapipe.dev)** — Hand landmark detection API
- **[OpenCV Documentation](https://docs.opencv.org)** — Camera & image processing

---

## 📜 License

MIT License © 2026. See LICENSE file for details.

---

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first to discuss your proposal.

