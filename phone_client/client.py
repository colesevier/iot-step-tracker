# phone_client/client.py

import time
from datetime import datetime, timezone

import requests

from config import (
    SERVER_BASE_URL,
    DEVICE_ID,
    SAMPLE_RATE_HZ,
    SEND_INTERVAL_SECONDS,
    ALERT_POLL_INTERVAL_SECONDS,
)
from processing import StepDetector
from sensors import read_accelerometer


def main():
    detector = StepDetector(sample_rate_hz=SAMPLE_RATE_HZ)
    unsent_steps = 0
    last_send_time = time.time()
    last_alert_poll_time = time.time()

    print(f"[phone_client] device_id={DEVICE_ID}")
    print(f"[phone_client] server={SERVER_BASE_URL}")

    try:
        while True:
            ax, ay, az = read_accelerometer()

            # 2. Run through step detector
            unsent_steps += detector.update(ax, ay, az)

            now = time.time()

            # 3. Send step data every SEND_INTERVAL_SECONDS
            if now - last_send_time >= SEND_INTERVAL_SECONDS:
                if unsent_steps > 0:
                    payload = {
                        "device_id": DEVICE_ID,
                        "steps": unsent_steps,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    try:
                        resp = requests.post(
                            f"{SERVER_BASE_URL}/data",
                            json=payload,
                            timeout=3,
                        )
                        resp.raise_for_status()
                        print(
                            f"[phone_client] Sent {unsent_steps} steps at {payload['timestamp']}"
                        )
                    except requests.RequestException as e:
                        print(f"[phone_client] Error sending data: {e}")

                    unsent_steps = 0

                last_send_time = now

            # 4. Poll for alerts every ALERT_POLL_INTERVAL_SECONDS
            if now - last_alert_poll_time >= ALERT_POLL_INTERVAL_SECONDS:
                try:
                    resp = requests.get(
                        f"{SERVER_BASE_URL}/alert/{DEVICE_ID}",
                        timeout=3,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    if data.get("alert"):
                        print(f"[phone_client] ALERT: {data['alert']}")
                        
                        # TODO: on real phone, vibrate / show notification here
                except requests.RequestException as e:
                    print(f"[phone_client] Error checking alerts: {e}")

                last_alert_poll_time = now

            # 5. Sleep for next sensor sample
            time.sleep(detector.sample_period)

    except KeyboardInterrupt:
        print("\n[phone_client] Stopped by user.")


if __name__ == "__main__":
    main()