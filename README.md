# lab1-serialcomm

A minimal serial-monitor GUI and helper library to read `Status:0` / `Status:1` messages from an Arduino/ESP32 IR-sensor transmitter.  
This repo contains an Arduino sketch (`firmware/sensor_transmitter.ino`) and a Python app (`src/serial_monitor/`) that reads, parses, displays, and plots incoming serial data.

---

## Features

- Connect to a serial port and display incoming lines.
- Parse `Status:0` / `Status:1` and keep simple rolling stats (counts, moving average).
- Small embedded plot of recent values (matplotlib + Tk).
- Console fallback available if a GUI/runtime is unavailable.

---

## Requirements

- Python 3.9+ (already installed)
- [uv](https://github.com/astral-sh/uv) — project manager
- System Tcl/Tk (for GUI/Tkinter) — platform-specific packages listed below
- Optional: `arduino-cli` (for compiling/uploading firmware)

---

## Quick Start

1. **Install `uv`** (see platform-specific instructions below).
2. **Install system Tcl/Tk** (see below for your OS).
3. From the project root, create/sync the environment:
   ```bash
   uv sync
   ```
4. Run the app:
   ```bash
   uv run lab1-serialcomm
   ```
5. In the GUI, select the device port (e.g. `/dev/ttyUSB0` or `COM3`) and baud `9600`, then click **Connect**.

---

## Build & Test

- Run tests:
  ```bash
  uv run pytest
  ```
- Build a wheel (optional):
  ```bash
  hatch build -t wheel
  ```

---

## Platform Setup

### Install `uv`

- **macOS / Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell)**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Alternative (pip)**:
  ```bash
  pip install uv
  ```

Verify installation:

```bash
uv --version
```

---

### Install Tcl/Tk (GUI requirement)

- **Ubuntu / Debian**:
  ```bash
  sudo apt update
  sudo apt install python3-tk tcl tk
  ```
- **Fedora**:
  ```bash
  sudo dnf install python3-tkinter tcl tk
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -Syu tk tcl
  ```
- **macOS**:
  ```bash
  brew install tcl-tk
  ```
- **Windows**: Included by default in official Python installer. If missing, re-run installer and enable `tcl/tk` option.

---

### Optional: Arduino CLI

```bash
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli compile --fqbn esp32:esp32:esp32 firmware
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 firmware
```

---

## Using `uv`

**Normal use (managed Python):**

```bash
uv sync
uv run lab1-serialcomm
```

**Use system Python (avoid managed Python):**

```bash
UV_NO_MANAGED_PYTHON=1 uv sync
uv run lab1-serialcomm
```

**Install a specific Python via `uv`:**

```bash
uv python install 3.13 --default
uv sync
```

---

## Troubleshooting

**Tkinter / Matplotlib crash (XCB errors)**:  
Use system Python instead of uv-managed Python:

```bash
UV_NO_MANAGED_PYTHON=1 uv sync
```

**Serial port permissions (Linux)**:

```bash
# Example for Debian/Ubuntu:
sudo usermod -a -G dialout $USER
newgrp dialout
```

---

## Project Layout

```
lab1-serialcomm/
├── firmware/sensor_transmitter.ino
├── src/serial_monitor/
│   ├── main.py
│   ├── serial_handler.py
│   ├── data_processing.py
│   └── utils.py
├── tests/
├── pyproject.toml
└── README.md
```

---

## Optional: upload + run helper

Create `run_all.sh`:

```bash
#!/usr/bin/env bash
set -e
PORT=${1:-/dev/ttyUSB0}
FQBN=${FQBN:-esp32:esp32:esp32}

arduino-cli compile --fqbn "$FQBN" firmware
arduino-cli upload -p "$PORT" --fqbn "$FQBN" firmware
sleep 1
uv run lab1-serialcomm
```

Make executable:

```bash
chmod +x run_all.sh
```

Run:

```bash
./run_all.sh /dev/ttyUSB0
```
