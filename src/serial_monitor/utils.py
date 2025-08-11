# src/serial_monitor/utils.py
from typing import List

from serial.tools import list_ports


def list_serial_ports() -> List[str]:
    """Return a list of available serial port device names (strings)."""
    ports = list_ports.comports()
    return [p.device for p in ports]


def simple_baud_guess(samples: list[str]) -> int | None:
    """
    (Optional) Very naive heuristic to guess a baud rate from samples.
    Real auto-baud is complicated; this function just inspects common markers.
    """
    if not samples:
        return None
    joined = " ".join(samples).lower()
    if "status" in joined:
        return 9600
    return None
