# IoT Step Tracker

A simple multi-node IoT project that turns a phone into a motion sensor and visualizes activity patterns using a FastAPI backend and a browser-based dashboard.

This project includes:

- **Node A – Phone Client** (sends step data; optional for testing)
- **Node B – FastAPI Server** (collects & stores data, sends inactivity alerts)
- **Node C – Web Dashboard** (visualizes activity in real time)

---

##  Project Structure

iot-step-tracker/
│
├── server/ # FastAPI backend
│ ├── main.py
│ ├── models.py
│ ├── database.py
│ └── requirements.txt
│
└── ui/ # Web dashboard
├── index.html
├── dashboard.js
└── styles.css


---

## Running the Server (Node B)

### 1. Enter the server directory

cd server

### 2. Create & activate virtual environment
Mac/Linux:

python3 -m venv venv
source venv/bin/activate

Windows:

python -m venv venv
venv\Scripts\activate


### 3. Install dependencies

pip install -r requirements.txt

### 4. Start the FastAPI server

uvicorn main:app --reload

The server will be live at:
http://127.0.0.1:8000/

---

## Running the Dashboard (Node C)

### 1. Navigate to UI folder

cd ui

### 2. Open the dashboard
Open `index.html` in your browser  
(double-click it or right-click → “Open With Browser”).

The dashboard automatically pulls data from:
http://127.0.0.1:8000


---

## Testing Without a Phone

You can manually send step data to the server:

curl -X POST http://127.0.0.1:8000/data

-H "Content-Type: application/json"
-d '{"device_id":"phone1","steps":10,"timestamp":"2025-01-01T10:00:00"}'

