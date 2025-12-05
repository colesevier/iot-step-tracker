from collections import defaultdict
from datetime import datetime

# activity_data[device_id] = list of {timestamp, steps}
activity_data = defaultdict(list)

# alerts[device_id] = queue/list of messages
alerts = defaultdict(list)


def store_activity(device_id: str, steps: int, timestamp: datetime):
    activity_data[device_id].append({
        "timestamp": timestamp,
        "steps": steps
    })


def get_activity(device_id: str):
    return activity_data[device_id]


def push_alert(device_id: str, message: str):
    alerts[device_id].append(message)


def pop_alert(device_id: str):
    if alerts[device_id]:
        return alerts[device_id].pop(0)
    return None


def reset_user(device_id: str):
    """Clear all activity + alerts for a given device."""
    if device_id in activity_data:
        activity_data[device_id].clear()
    if device_id in alerts:
        alerts[device_id].clear()