# src/serial_monitor/data_processing.py
import time
from collections import deque
from typing import Deque, Iterable, Optional, Tuple


def parse_status_line(line: str) -> Optional[dict]:
    """
    Parse lines like "Status:0" or "Status:1" (possibly with whitespace/newline).
    Returns {"status": int, "ts": timestamp} or None if unparseable.
    """
    if not line:
        return None
    s = line.strip()
    if s.lower().startswith("status:"):
        try:
            val = int(s.split(":", 1)[1].strip())
            if val in (0, 1):
                return {"status": val, "ts": time.time()}
        except Exception:
            return None
    return None


class DataProcessor:
    """
    Keeps a fixed-size window of recent status values (0/1) and provides stats.
    """

    def __init__(self, window_size: int = 100):
        self._window: Deque[int] = deque(maxlen=window_size)

    def push(self, value: int, ts: float | None = None):
        # store 0/1 only
        self._window.append(1 if int(value) else 0)

    def window(self) -> Iterable[int]:
        return list(self._window)

    def counts(self) -> Tuple[int, int]:
        ones = sum(self._window)
        zeros = len(self._window) - ones
        return (int(zeros), int(ones))

    def moving_average(self) -> float:
        if not self._window:
            return 0.0
        return float(sum(self._window) / len(self._window))

    def minmax(self) -> Tuple[int, int]:
        if not self._window:
            return (0, 0)
        return (min(self._window), max(self._window))
