# server/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional

from .models import StepData
from .database import store_activity, get_activity, push_alert, pop_alert, reset_device_data
from .analytics import analytics_for_device

app = FastAPI(title="IoT Step Tracker API")

# Allow local UI to fetch from different origin during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INACTIVITY_THRESHOLD_MINUTES = 3


@app.get("/")
def root():
    return {"status": "server running"}


@app.post("/data")
def receive_step_data(payload: StepData):
    """
    Receive step packets from phones.
    payload.timestamp is parsed by Pydantic into datetime.
    """
    store_activity(payload.device_id, int(payload.steps), payload.timestamp)

    # check inactivity between last two samples
    last_entries = get_activity(payload.device_id)
    if len(last_entries) >= 2:
        last = last_entries[-1]["timestamp"]
        prev = last_entries[-2]["timestamp"]
        delta = last - prev
        if delta > timedelta(minutes=INACTIVITY_THRESHOLD_MINUTES):
            push_alert(payload.device_id, "Move! You've been inactive for a while.")

    return {"ok": True}


@app.get("/user/{device_id}/activity")
def user_activity(device_id: str):
    entries = get_activity(device_id)
    # Return entries (datetime will be serialized automatically).
    return entries or []


@app.post("/user/{device_id}/reset")
def reset_user(device_id: str):
    """
    Clear stored data for the device. Used by phone UI reset.
    """
    reset_device_data(device_id)
    return {"ok": True}


@app.get("/alert/{device_id}")
def get_alert(device_id: str):
    msg = pop_alert(device_id)
    return {"alert": msg}


@app.get("/analytics/{device_id}/today")
def analytics_today(device_id: str, weight_kg: Optional[float] = 75.0):
    """
    Returns pace, corrected steps, calories, and predicted daily steps.
    """
    # Even if no data exists, return zeros for UX.
    payload = analytics_for_device(device_id, weight_kg=float(weight_kg))
    return payload
