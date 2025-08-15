# 🚦 AI-Powered Real-Time Accident Detection

This project is an **AI-based accident detection system** built with Python, OpenCV, and YOLOv4.  
It processes live video streams from CCTV cameras or webcams to detect collisions between vehicles or persons.  
Upon detection, the system **plays an alarm sound** and can **send instant alerts** (via Twilio) to improve emergency response times and enhance smart city safety.

---

## ✨ Key Features
- **Real-Time Detection** — Monitors live video feeds for accident events.
- **YOLOv4 Object Recognition** — Detects vehicles and pedestrians accurately.
- **Collision Analysis** — Uses bounding box proximity to determine possible accidents.
- **Instant Alerts** — Audible alarm and optional phone call via Twilio API.
- **Flexible Input** — Works with CCTV footage, webcam streams, or video files.
- **Cross-Platform** — Runs locally or on cloud platforms (e.g., Google Colab).

---

## 🗂 Project Structure
Accident-Detection/
│── main.py # Main script to capture video and detect accidents
│── alarm.wav # Alarm sound file
│── yolov4.cfg # YOLOv4 configuration file
│── yolov4.weights # YOLOv4 pretrained weights
│── coco.names # Object class labels
│── requirements.txt # Python dependencies

---

## 📦 Requirements
- Python 3.7+
- OpenCV
- NumPy
- Twilio (for phone alerts)
- YOLOv4 model files (coco.names`)

**Install dependencies:**
```bash
pip install opencv-python-headless numpy twilio

**▶ How to Run**

**Clone the repository**

git clone https://github.com/Muuussskan23/Accident-Detection.git
cd Accident-Detection

**Download YOLOv4 model files**

Place yolov4.cfg, yolov4.weights, and coco.names in the project directory.

**Run the script**

python main.py

**or in Google Colab:**

!python main.py

**Optional: Configure Twilio credentials in the script for SMS/call alerts.**

export TWILIO_SID="your_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export ALERT_PHONE="your_phone_number"

**How It Works**

1.Captures live frames from a connected camera.
2.Detects vehicles and people (via image processing or YOLOv4).
3.Checks overlap between bounding boxes—if above threshold, it considers it an accident.
4.On Detection:
  Plays alarm
  Optionally initiates a phone call via Twilio.
5.Provides live visual feedback with detection boxes.
