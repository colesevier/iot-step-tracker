# server/analytics.py
from collections import defaultdict
from datetime import datetime, date, timedelta
from typing import List, Tuple

from .database import activity_data

# ---- helpers to fetch entries -------------------------------------------

def _get_device_entries(device_id: str):
    """
    Return a shallow copy of the device's activity entries list.
    """
    return list(activity_data.get(device_id, []))


# ---- pace estimation (steps per minute) ---------------------------------

def _entries_in_window(entries: List[dict], window_seconds: int):
    if not entries:
        return []
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=window_seconds)
    return [e for e in entries if e["timestamp"] >= cutoff]


def compute_pace_spm(device_id: str, window_seconds: int = 60) -> float:
    entries = _get_device_entries(device_id)
    recent = _entries_in_window(entries, window_seconds)
    if not recent:
        return 0.0
    steps_in_window = sum(int(e.get("steps", 0)) for e in recent)
    pace_spm = (steps_in_window / max(window_seconds, 1)) * 60.0
    return round(float(pace_spm), 2)


# ---- calories estimation (MET-based) -----------------------------------

def estimate_met_from_pace(pace_spm: float) -> float:
    if pace_spm < 20:
        return 1.5
    if pace_spm < 100:
        return 2.0 + (pace_spm - 20) * (3.0 / (100 - 20))
    return 6.0 + (pace_spm - 100) * 0.02


def compute_calories_today(device_id: str, weight_kg: float = 75.0) -> float:
    entries = _get_device_entries(device_id)
    if not entries:
        return 0.0
    today = date.today()
    todays = [e for e in entries if e["timestamp"].date() == today]
    if not todays:
        return 0.0
    t0 = min(e["timestamp"] for e in todays)
    t1 = max(e["timestamp"] for e in todays)
    duration_minutes = max((t1 - t0).total_seconds() / 60.0, 1.0)
    pace = compute_pace_spm(device_id, window_seconds=300)
    met = estimate_met_from_pace(pace)
    kcal_per_min = met * 3.5 * weight_kg / 200.0
    calories = kcal_per_min * duration_minutes
    return round(float(calories), 2)


# ---- undercount correction (heuristic) ---------------------------------

def _per_minute_totals(entries: List[dict]):
    per_min = defaultdict(int)
    for e in entries:
        minute = e["timestamp"].replace(second=0, microsecond=0)
        per_min[minute] += int(e.get("steps", 0))
    return per_min


def estimate_accel_variance_proxy(device_id: str) -> float:
    entries = _get_device_entries(device_id)
    pm = list(_per_minute_totals(entries).values())
    if len(pm) < 2:
        return 0.0
    mean = sum(pm) / len(pm)
    var = sum((x - mean) ** 2 for x in pm) / (len(pm) - 1)
    return float(var)


def correct_step_count(device_id: str, raw_steps_today: int) -> int:
    var = estimate_accel_variance_proxy(device_id)
    factor = 1.0 + min(var * 0.02, 0.30)  # cap to +30%
    corrected = int(round(raw_steps_today * factor))
    return corrected


# ---- daily prediction (simple heuristic) --------------------------------

def _historical_daily_totals(device_id: str, days_back: int = 21) -> List[Tuple[date, int]]:
    entries = _get_device_entries(device_id)
    by_day = defaultdict(int)
    for e in entries:
        by_day[e["timestamp"].date()] += int(e.get("steps", 0))
    today = date.today()
    results = []
    for d, total in by_day.items():
        age = (today - d).days
        if 0 <= age <= days_back:
            results.append((d, total))
    return sorted(results, key=lambda x: x[0])


def predict_daily_steps(device_id: str) -> int:
    hist = _historical_daily_totals(device_id, days_back=21)
    entries = _get_device_entries(device_id)
    today_entries = [e for e in entries if e["timestamp"].date() == date.today()]
    raw_today = sum(int(e.get("steps", 0)) for e in today_entries)
    corrected_today = correct_step_count(device_id, raw_today)

    if not hist:
        now = datetime.utcnow()
        hour = now.hour or 1
        predicted = int(corrected_today * (24.0 / max(hour, 1.0)))
        return max(predicted, corrected_today)

    totals = [t for (d, t) in hist if d != date.today()]
    if not totals:
        totals = [t for (d, t) in hist]

    hist_avg = sum(totals) / max(len(totals), 1)
    now = datetime.utcnow()
    current_hour = now.hour + now.minute / 60.0
    predicted = int(round(0.5 * hist_avg + 0.5 * corrected_today * (24.0 / max(current_hour, 1.0))))
    return max(predicted, corrected_today)


# ---- combined payload ---------------------------------------------------

def analytics_for_device(device_id: str, weight_kg: float = 75.0):
    entries = _get_device_entries(device_id)
    today = date.today()
    today_entries = [e for e in entries if e["timestamp"].date() == today]
    raw_today = sum(int(e.get("steps", 0)) for e in today_entries)
    pace = compute_pace_spm(device_id, window_seconds=60)
    corrected = correct_step_count(device_id, raw_today)
    calories = compute_calories_today(device_id, weight_kg=weight_kg)
    predicted = predict_daily_steps(device_id)
    return {
        "pace_spm": pace,
        "raw_steps_today": raw_today,
        "corrected_steps_today": corrected,
        "calories_today": calories,
        "predicted_daily_steps": predicted,
    }
