# 🏎️ Hand Gesture Racing Controller

Turn your webcam into a virtual steering wheel! This Python project uses computer vision and AI hand-tracking to let you play any PC racing game using nothing but hand gestures. 

## ✨ Features
* **Real-Time Hand Tracking:** Powered by Google's MediaPipe AI.
* **Steering:** Move your hand left or right across the screen to steer.
* **Accelerate & Brake:** Keep an open palm to hit the gas, or close your fist to brake.
* **Nitro Boost:** Pinch your thumb and index finger together to trigger the boost (Shift key).
* **Live HUD Overlay:** An on-screen virtual steering wheel that reacts to your gestures and changes colors.

## 🛠️ Prerequisites
* **Python 3.11 (64-bit)** *(Note: MediaPipe requires 64-bit Python to run on Windows).*
* A working webcam.

## 📦 Installation

1. **Clone or download this repository** to your local machine.
2. **Open your terminal** and navigate to the project folder.
3. **Create and activate a virtual environment** (Highly Recommended):
   ```bash
   python -m venv .venv
   # Activate on Windows:
   .\.venv\Scripts\activate
