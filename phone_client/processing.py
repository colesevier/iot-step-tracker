import math
import time
from collections import deque
from typing import Deque, Optional


class StepDetector:

    def __init__(
        self,
        sample_rate_hz: float,
        window_size: int = 20,
        threshold: float = 0.8,
        min_step_interval_s: float = 0.3,
    ):
        self.sample_rate_hz = sample_rate_hz
        self.sample_period = 1.0 / sample_rate_hz
        self.window_size = window_size
        self.threshold = threshold
        self.min_step_interval_s = min_step_interval_s

        self._mag_window: Deque[float] = deque(maxlen=window_size)
        self._last_step_time: Optional[float] = None

    def update(self, ax: float, ay: float, az: float) -> int:
        now = time.time()
        mag = math.sqrt(ax * ax + ay * ay + az * az)
        self._mag_window.append(mag)

        if len(self._mag_window) < self.window_size:
            return 0

        avg_mag = sum(self._mag_window) / len(self._mag_window)
        filtered = mag - avg_mag

        if filtered > self.threshold:
            if (
                self._last_step_time is None
                or (now - self._last_step_time) >= self.min_step_interval_s
            ):
                self._last_step_time = now
                return 1

        return 0