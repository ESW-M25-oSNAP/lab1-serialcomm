# src/serial_monitor/main.py
import queue
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .data_processing import DataProcessor, parse_status_line
from .serial_handler import SerialReader
from .utils import list_serial_ports

matplotlib.use(
    "Agg"
)  # ensure non-interactive backend for safe import (Canvas will still work)


APP_TITLE = "Serial Monitor — Lab1"


class SerialMonitorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("880x560")
        root.minsize(700, 420)

        self.queue = queue.Queue()
        self.serial_thread: SerialReader | None = None
        self.processor = DataProcessor(window_size=50)

        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        # Top frame: connection controls
        top = ttk.Frame(self.root, padding=(12, 8))
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Port:").pack(side=tk.LEFT, padx=(0, 6))
        self.port_combo = ttk.Combobox(
            top, values=list_serial_ports(), state="readonly", width=24
        )
        self.port_combo.pack(side=tk.LEFT)
        ttk.Button(top, text="Refresh", command=self._refresh_ports).pack(
            side=tk.LEFT, padx=(6, 12)
        )

        ttk.Label(top, text="Baud:").pack(side=tk.LEFT)
        self.baud_combo = ttk.Combobox(
            top, values=["9600", "115200", "57600", "19200"], width=10
        )
        self.baud_combo.set("9600")
        self.baud_combo.pack(side=tk.LEFT, padx=(6, 12))

        self.connect_btn = ttk.Button(
            top, text="Connect", command=self._toggle_connection
        )
        self.connect_btn.pack(side=tk.LEFT)

        self.status_label = ttk.Label(
            top, text="Status: disconnected", foreground="gray"
        )
        self.status_label.pack(side=tk.RIGHT)

        # Main horizontal split
        main = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Left: text log
        left_frame = ttk.Frame(main)
        self.log = scrolledtext.ScrolledText(
            left_frame, state="disabled", width=46, wrap=tk.NONE
        )
        self.log.pack(fill=tk.BOTH, expand=True)
        main.add(left_frame, weight=1)

        # Right: stats + plot
        right_frame = ttk.Frame(main)
        # Stats labels
        stats_frame = ttk.Frame(right_frame, padding=(8, 8))
        stats_frame.pack(fill=tk.X)
        self.latest_label = ttk.Label(stats_frame, text="Latest: —")
        self.latest_label.pack(anchor=tk.W)
        self.counts_label = ttk.Label(stats_frame, text="Counts: —")
        self.counts_label.pack(anchor=tk.W)
        self.avg_label = ttk.Label(stats_frame, text="Moving avg: —")
        self.avg_label.pack(anchor=tk.W)

        # Matplotlib plot area
        self.fig = Figure(figsize=(4.2, 2.8), tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Sensor (last values)")
        self.ax.set_ylim(-0.1, 1.1)
        self.ax.set_yticks([0, 1])
        (self.line,) = self.ax.plot([], [], lw=2)

        canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.canvas = canvas

        main.add(right_frame, weight=2)

    def _refresh_ports(self):
        ports = list_serial_ports()
        self.port_combo.config(values=ports)
        if ports:
            self.port_combo.set(ports[0])

    def _toggle_connection(self):
        if self.serial_thread and self.serial_thread.is_alive():
            self._disconnect()
        else:
            port = self.port_combo.get()
            baud = int(self.baud_combo.get() or 9600)
            if not port:
                messagebox.showwarning("No port", "Select a serial port first.")
                return
            self._connect(port, baud)

    def _connect(self, port: str, baud: int):
        self.serial_thread = SerialReader(
            port=port, baudrate=baud, out_queue=self.queue
        )
        self.serial_thread.start()
        self.connect_btn.config(text="Disconnect")
        self.status_label.config(
            text=f"Status: connected ({port}@{baud})", foreground="green"
        )
        self._log(f"Connecting to {port} at {baud}...")

    def _disconnect(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.join(timeout=1.0)
            self.serial_thread = None
        self.connect_btn.config(text="Connect")
        self.status_label.config(text="Status: disconnected", foreground="gray")
        self._log("Disconnected")

    def _log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert(tk.END, f"{time.strftime('%H:%M:%S')}  {text}\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def _poll_queue(self):
        updated = False
        while not self.queue.empty():
            raw = self.queue.get_nowait()
            parsed = parse_status_line(raw)
            if parsed:
                self.processor.push(parsed["status"], parsed["ts"])
                self.latest_label.config(
                    text=f"Latest: {parsed['status']} @ {time.strftime('%H:%M:%S', time.localtime(parsed['ts']))}"
                )
                self.counts_label.config(text=f"Counts: {self.processor.counts()}")
                self.avg_label.config(
                    text=f"Moving avg: {self.processor.moving_average():.3f}"
                )
                self._log(f"RX: {raw.strip()}")
                updated = True
            else:
                # show non-parsed lines
                self._log(f"RAW: {raw.strip()}")

        if updated:
            self._update_plot()
        self.root.after(150, self._poll_queue)

    def _update_plot(self):
        xs = list(range(-len(self.processor.window()) + 1, 1))
        ys = list(self.processor.window())
        self.line.set_data(xs, ys)
        self.ax.set_xlim(xs[0] if xs else -50, 0)
        self.canvas.draw_idle()

    def on_close(self):
        self._disconnect()
        self.root.quit()


def main():
    root = tk.Tk()
    app = SerialMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_close()


if __name__ == "__main__":
    main()
