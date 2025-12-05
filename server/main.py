from fastapi import FastAPI
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from models import StepData
from database import (
    store_activity,
    get_activity,
    push_alert,
    pop_alert,
    reset_user,
    activity_data,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve UI from /ui
BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR.parent / "ui"
app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")

INACTIVITY_THRESHOLD_MINUTES = 3


@app.get("/")
def root():
    return {"status": "server running"}


@app.post("/data")
def receive_step_data(payload: StepData):
    store_activity(
        device_id=payload.device_id,
        steps=payload.steps,
        timestamp=payload.timestamp,
    )

    last_entries = get_activity(payload.device_id)
    if len(last_entries) >= 2:
        last = last_entries[-1]["timestamp"]
        prev = last_entries[-2]["timestamp"]
        delta = last - prev

        if delta > timedelta(minutes=INACTIVITY_THRESHOLD_MINUTES):
            push_alert(payload.device_id, "Move! You’ve been inactive.")

    return {"ok": True}


@app.get("/user/{device_id}/activity")
def user_activity(device_id: str):
    return get_activity(device_id)


@app.post("/user/{device_id}/reset")
def reset_user_data(device_id: str):
    """Clear all data + alerts for this user."""
    reset_user(device_id)
    return {"ok": True}


@app.get("/alert/{device_id}")
def get_alert(device_id: str):
    msg = pop_alert(device_id)
    return {"alert": msg}