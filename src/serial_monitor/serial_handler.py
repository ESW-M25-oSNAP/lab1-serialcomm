# src/serial_monitor/serial_handler.py
import threading
from typing import Optional

import serial
from serial import SerialException


class SerialReader(threading.Thread):
    """
    Reads lines from a serial port in a background thread and puts raw lines into out_queue.
    out_queue: a queue.Queue
    """

    def __init__(self, port: str, baudrate: int, out_queue, timeout: float = 1.0):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.out_queue = out_queue
        self.timeout = timeout
        self._stop_event = threading.Event()
        self._ser: Optional[serial.Serial] = None

    def open_serial(self):
        try:
            self._ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            return True
        except (SerialException, OSError) as e:
            self.out_queue.put(f"ERROR: could not open serial port: {e}\n")
            return False

    def stop(self):
        self._stop_event.set()
        if self._ser and self._ser.is_open:
            try:
                self._ser.close()
            except Exception:
                pass

    def run(self):
        if not self.open_serial():
            return
        self.out_queue.put(f"INFO: serial opened {self.port}@{self.baudrate}\n")
        while not self._stop_event.is_set():
            try:
                raw = self._ser.readline()
                if not raw:
                    continue
                try:
                    line = raw.decode(errors="replace")
                except Exception:
                    line = str(raw)
                self.out_queue.put(line)
            except SerialException as e:
                self.out_queue.put(f"ERROR: serial read failed: {e}\n")
                break
            except Exception as e:
                self.out_queue.put(f"ERROR: unexpected error: {e}\n")
                break
        self.out_queue.put("INFO: serial thread exiting\n")
