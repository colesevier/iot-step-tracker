# server/database.py
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any

# activity_data[device_id] = list of {"timestamp": datetime, "steps": int}
activity_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

# alerts[device_id] = list of messages (FIFO)
alerts: Dict[str, List[str]] = defaultdict(list)


def store_activity(device_id: str, steps: int, timestamp: datetime):
    """
    Append an activity sample for device_id.
    """
    activity_data[device_id].append({
        "timestamp": timestamp,
        "steps": int(steps)
    })


def get_activity(device_id: str):
    """
    Return the list of entries (may be empty).
    """
    return activity_data.get(device_id, [])


def push_alert(device_id: str, message: str):
    alerts[device_id].append(str(message))


def pop_alert(device_id: str):
    if alerts.get(device_id):
        return alerts[device_id].pop(0)
    return None


def reset_device_data(device_id: str):
    """
    Clear the stored activity and alerts for the device.
    """
    activity_data.pop(device_id, None)
    alerts.pop(device_id, None)
