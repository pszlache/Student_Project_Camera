# Attendance Monitoring / Intrusion Detection System

## Overview

This project implements a **camera-based monitoring system** capable of detecting motion and identifying human presence using computer vision techniques.

The system captures video from a camera, detects motion, performs AI-based person detection, and triggers events such as logging, snapshot capture, video recording, or notifications.

The architecture follows a **modular and event-driven design**, making it easy to extend with new sensors, notification systems, or AI models.

This project was developed as part of an **engineering thesis in Computer Science**.

---

# Features

* 📷 Camera video capture
* 🧠 AI-based person detection
* 🚶 Motion detection
* 🧾 Event-driven system architecture
* 📸 Automatic snapshot capture
* 🎥 Video recording
* 🌐 Web interface for monitoring
* 📊 Logging system
* ⚙ Modular architecture (handlers, services, repositories)

---

# System Architecture

The application is divided into several modules:

### Camera Module

Handles camera initialization and frame capture.

### Motion Detection

Detects movement in video frames.

### AI Detection

Uses a neural network model to detect people.

### Event System

Triggers actions when specific events occur (e.g., motion detected).

### Handlers

Handle events such as:

* saving snapshots
* recording video
* logging
* notifications

### Web Interface

Provides monitoring functionality via a web interface.

---

# Project Structure

```
PROJECT_1
│
├── data
│
├── models
│ ├── MobileNetSSD_deploy.caffemodel
│ └── MobileNetSSD_deploy.prototxt
│
├── src
│ │
│ ├── ai
│ │ └── person_detector.py
│ │
│ ├── camera
│ │ ├── detect.py
│ │ └── usb_camera.py
│ │
│ ├── core
│ │ ├── events.py
│ │ ├── handlers
│ │ ├── services
│ │ └── repositories
│ │
│ ├── logs
│ │
│ ├── motion
│ │ └── motion_detector.py
│ │
│ ├── utils
│ │
│ └── web
│ ├── static
│ ├── templates
│ ├── logs.py
│ └── stream.py
│
├── tests
│
├── .gitignore
├── .pre-commit-config.yaml
│
├── config.py
├── main.py
├── justfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# Technologies Used

* **Python**
* **OpenCV**
* **NumPy**
* **Flask (web interface)**
* **Machine Learning model (MobileNet SSD)**

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd PROJECT_1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

or using `pyproject.toml`:

```bash
pip install .
```

---

# Running the Application

Start the system:

```bash
python main.py
```

The system will:

1. Initialize the camera
2. Start motion detection
3. Run AI person detection
4. Trigger events when activity is detected

---

# Configuration

Application configuration can be modified in:

```
config.py
```

Possible settings include:

* camera parameters
* detection thresholds
* logging options
* storage directories

---

# Future Improvements

Possible extensions of the system:

* GSM/SMS notifications
* email alerts
* multiple camera support
* database storage
* improved AI detection models
* authentication system for the web interface

---

# License

This project is intended for educational purposes as part of an engineering thesis.

---

# Author

Piotr Szlachetka
