## 👋 Hand Gesture Control: Volume and Brightness (macOS)

Control your Mac with hand gestures using your webcam.

- 🖐️ Left hand → Volume (0–100%)
- ✋ Right hand → Brightness (5–100%)
- 🔁 Selfie view with correctly oriented on-screen text

```
[Left Hand] thumb↔index distance  ──> 🎚 Volume
[Right Hand] thumb↔index distance ──> 💡 Brightness
```

### ✨ Features
- Real-time hand detection and landmarks (MediaPipe)
- Handedness detection (Left/Right) with mirror-correct labels
- Smooth mapping from finger distance to system controls
- HUD shows Distance, mapped Volume/Brightness, and active action

### 📦 Requirements
- Python 3.9+
- macOS (tested on Apple Silicon)
- Webcam access

### 🧰 Install
```bash
cd "/Users/eshansaxena/Personal/major project/ComputerVision"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
brew install brightness   # for screen brightness control on built-in display
```

If you control an external monitor, consider:
```bash
brew install ddcctl   # optional; some external displays support DDC/CI
```

### 🔐 macOS Permissions
Grant these to Terminal/your IDE after first run:
- Camera: System Settings → Privacy & Security → Camera
- Input Monitoring: System Settings → Privacy & Security → Input Monitoring

Then restart your terminal/IDE.

### ▶️ Run
```bash
source .venv/bin/activate
python hand_fingers_control.py
```

- Press `q` to quit
- `MIRROR_VIEW` is enabled by default for a selfie view with readable text

### 🕹️ Gestures
- Left hand: move thumb and index apart → volume increases; closer → decreases
- Right hand: move thumb and index apart → brightness increases; closer → decreases

### 🧭 HUD Legend
- Distance: normalized thumb–index distance
- Volume map: the volume value derived from distance
- Brightness map: the brightness value derived from distance
- Hand: detected handedness + last applied action

### 🧩 How it works
1. Reads webcam frames with OpenCV
2. Detects 21 hand landmarks via MediaPipe
3. Uses MediaPipe handedness and optional mirror inversion for labels
4. Maps thumb–index distance to values:
   - Volume: 0–100 (osascript)
   - Brightness: 0.05–1.0 (`brightness` CLI)
5. Overlays a simple HUD with current readings and action

### 🛠️ Troubleshooting
- Brightness errors like `failed to get brightness of display`:
  - The `brightness` CLI controls the built-in display; many external monitors block this.
  - Use `ddcctl` for supported external displays, or adjust brightness via monitor buttons.
- No camera / black window: close other camera apps; try another camera index in the code.
- No volume change: ensure Input Monitoring permission is granted to Terminal/IDE.
- Mirrored left/right confusion: toggle `MIRROR_VIEW = False` in the script.

### 📁 Project Structure
```
ComputerVision/
├─ hand_fingers_control.py   # main app
├─ requirements.txt          # python deps
└─ README.md                 # this guide
```

### ✅ Notes
- Volume uses `osascript` and works on macOS system output
- Brightness uses the `brightness` CLI; success varies on external displays

### 🙋 FAQ
- Q: Can I change which hand controls which?
  - Yes. In `hand_fingers_control.py`, swap the branches where `hand_label == "Left"` vs `"Right"`.
- Q: Text is mirrored.
  - We already mirror before drawing so text is readable. If needed, set `MIRROR_VIEW = False`.

---

Made with 🧠 MediaPipe, 🎥 OpenCV, and a bit of 🍎 AppleScript.
