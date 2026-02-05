# Smart Monitoring System (Raspberry Pi)

A modular video monitoring system built for Raspberry Pi, using USB cameras, motion detection, AI-based human detection and presence logic.

The system is designed to be efficient, scalable and easy to extend with additional features such as GSM notifications, event logging and face recognition.

---

## Features

- Multi-camera USB support
- Motion detection based on frame differencing
- AI-based human detection
- Presence-based event handling (single event per presence)
- Delayed snapshot capture for better image quality
- MJPEG live video streaming via Flask
- Thread-safe camera handling
- Modular architecture ready for further extensions

---

## Project Structure

camera/ - USB camera handling (thread-safe)
motion/ - Motion detection module
ai/ - AI-based person detection
utils/ - Snapshot helper
web/ - Flask video streaming
config.py - System configuration
main.py - Application entry point

## Requirements

- Raspberry Pi (tested on Raspberry Pi 5)
- Python 3.9+
- USB camera(s)
- OpenCV
- Flask

## Configuration

All system parameters can be adjusted in config.py, including:
- camera resolution and FPS
- motion detection sensitivity
- AI confidence threshold
- number of connected cameras

Example multi-camera configuration:
    CAMERAS = {
    0: {"name": "FirstCam", "index": 0},
    1: {"name": "SecondCam", "index": 1}
    }