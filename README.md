# IoT Step Tracker
Cole Sevier and Archit Garg 

Turn a phone into a motion sensor, collect steps on a FastAPI backend, and visualize activity with a web dashboard.

Components:
- Server (FastAPI) at `server/`
- Web UI (dashboard + browser phone client) at `ui/`
- Python phone simulator at `phone_client/`
- Native iOS client at `StepPhoneClient/`

---

## Prerequisites
- Python 3.10+ recommended
- pip
- iOS development (optional): Xcode 15+
- A phone and your computer on the same Wi‑Fi if you want to stream from the phone/browser to your laptop’s server

---

## Quick Start
1) Start the backend server
2) Open the dashboard in a browser
3) Send steps from:
   - the browser phone page, or
   - the Python simulator, or
   - the iOS app

Details below.

---

## 1) Run the FastAPI Server
From the project root:
```bash
cd server
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Local only
uvicorn main:app --reload

# If you want phones on your LAN to connect, use your machine IP
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Server will be available at:
- http://127.0.0.1:8000 (local)
- http://YOUR_LAN_IP:8000 (from other devices on the same network)

The server also serves the UI at `/ui`, e.g.:
- Dashboard: `http://127.0.0.1:8000/ui/`
- Browser phone client: `http://127.0.0.1:8000/ui/phone.html`

If accessing from your phone, replace `127.0.0.1` with your computer’s LAN IP.

---

## 2) Web Dashboard
Open:
- Local: `http://127.0.0.1:8000/ui/`
- From phone/another device: `http://YOUR_LAN_IP:8000/ui/`

It displays a chart and some summary stats. Use the user dropdown to switch devices and the button to reset user data.

Endpoints used by the UI:
- `GET /user/{device_id}/activity` — returns time-series steps
- `POST /user/{device_id}/reset` — clears activity for a device

---

## 3) Send Steps (Choose one or more)

### A) Browser Phone Client
Use your phone’s browser:
- Go to `http://YOUR_LAN_IP:8000/ui/phone.html`
- Tap “Enable Motion” to grant motion permissions (iOS Safari requires user action)
- Tap “Start” to begin sampling; “Stop” to stop; “Reset Session” to clear
- Optional: change the Device ID at the top

This page sends:
- `POST /data` with `{ device_id, steps, timestamp }` every few seconds
- Polls `GET /alert/{device_id}` every few seconds for inactivity alerts

### B) Python Simulator
From the project root:
```bash
cd phone_client
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure server/device if needed
# Edit config.py:
# SERVER_BASE_URL = "http://127.0.0.1:8000"
# DEVICE_ID = "phone_1"

python client.py
```
This simulates accelerometer data and periodically sends step counts to the server and polls for alerts.

### C) iOS App
Open the Xcode project at `StepPhoneClient/StepPhoneClient.xcodeproj`.

Update the server base URL:
- File: `StepPhoneClient/StepPhoneClient/ApiClient.swift`
- Change `BASE_URL_STRING` to `http://YOUR_LAN_IP:8000`

Build and run on a device (recommended so motion sensors are available). The app periodically posts steps and checks alerts.

Note: The `Info.plist` includes motion usage permission. You may be prompted on first run.

---

## API Reference (Server)
- `GET /` — health/status
- `POST /data`  
  Body:  
  ```json
  { "device_id": "string", "steps": 10, "timestamp": "2025-01-01T10:00:00Z" }
  ```
- `GET /user/{device_id}/activity` — list of `{ timestamp, steps }`
- `POST /user/{device_id}/reset` — clears data and alerts for device
- `GET /alert/{device_id}` — returns `{ "alert": "Move! …" }` or `{ "alert": null }`

The server currently stores data in memory (`server/database.py`) for simplicity.

---

## Troubleshooting
- Phone cannot reach server: ensure you started uvicorn with `--host 0.0.0.0` and you’re using your computer’s LAN IP from the phone.
- CORS: CORS is open to `*` in this demo.
- Motion permissions: iOS Safari requires a user gesture to request motion access. Use the “Enable Motion” button in the browser phone page.
- Port conflicts: change the `--port` if 8000 is taken and update your client URLs accordingly.

---

## Project Structure
```
iot-step-tracker/
├─ server/                 # FastAPI backend (serves /ui)
│  ├─ main.py
│  ├─ models.py
│  ├─ database.py
│  └─ requirements.txt
├─ ui/                     # Web dashboard + browser phone client
│  ├─ index.html           # dashboard
│  ├─ dashboard.js
│  ├─ phone.html           # phone client (browser)
│  └─ phone.js
├─ phone_client/           # Python phone simulator
│  ├─ client.py
│  ├─ config.py
│  ├─ processing.py
│  └─ sensors.py
└─ StepPhoneClient/        # Native iOS client (Xcode)
   └─ StepPhoneClient.xcodeproj
```

