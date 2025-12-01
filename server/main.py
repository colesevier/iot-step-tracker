from fastapi import FastAPI
from datetime import datetime, timedelta

from models import StepData
from database import store_activity, get_activity, push_alert, pop_alert, activity_data


app = FastAPI()

INACTIVITY_THRESHOLD_MINUTES = 3


@app.get("/")
def root():
    return {"status": "server running"}


@app.post("/data")
def receive_step_data(payload: StepData):
    """
    Node A (phone) sends steps:
        {
            "device_id": "abc123",
            "steps": 10,
            "timestamp": "2025-01-01T10:00:00"
        }
    """
    store_activity(
        device_id=payload.device_id,
        steps=payload.steps,
        timestamp=payload.timestamp
    )

    # Check inactivity
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
    """
    UI requests the user’s activity data.
    """
    return get_activity(device_id)


@app.get("/alert/{device_id}")
def get_alert(device_id: str):
    """
    Phone polls this endpoint just to check for alerts.
    """
    msg = pop_alert(device_id)
    return {"alert": msg}
