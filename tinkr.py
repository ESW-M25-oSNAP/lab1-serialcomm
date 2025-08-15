import serial
import threading
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ser = None
running = False
data_values = []  # Store numeric data for the graph
max_points = 50   # Number of points to display in the graph

def start_reading():
    global ser, running
    port = port_entry.get()
    baud = int(baud_entry.get())
    ser = serial.Serial(port, baud, timeout=1)
    running = True
    threading.Thread(target=read_serial, daemon=True).start()

def stop_reading():
    global running, ser
    running = False
    if ser and ser.is_open:
        ser.close()

def read_serial():
    global running, ser, data_values
    while running:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    output_text.insert(tk.END, line + "\n")
                    output_text.see(tk.END)

                    # Try to convert to float for graphing
                    try:
                        value = float(line)
                        data_values.append(value)
                        if len(data_values) > max_points:
                            data_values = data_values[-max_points:]
                        update_graph()
                    except ValueError:
                        pass  # Ignore non-numeric lines
            except Exception as e:
                print(f"Error reading serial: {e}")

def update_graph():
    ax.clear()
    if data_values:  # Only plot if we have at least 1 value
        ax.step(range(len(data_values)), data_values, where='post',
                color='blue', linewidth=2)
    ax.set_ylim(-0.2, 1.2)  # Keep 0/1 visible
    ax.set_title("Live Binary Data (Square Wave)")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Value")
    ax.grid(True)
    canvas.draw()

# GUI Setup
root = tk.Tk()
root.title("ESP32 Serial Reader with Live Graph")

ttk.Label(root, text="COM Port:").grid(row=0, column=0)
port_entry = ttk.Entry(root)
port_entry.insert(0, "COM3")  # Default value
port_entry.grid(row=0, column=1)

ttk.Label(root, text="Baud Rate:").grid(row=1, column=0)
baud_entry = ttk.Entry(root)
baud_entry.insert(0, "115200")
baud_entry.grid(row=1, column=1)

ttk.Button(root, text="Start", command=start_reading).grid(row=2, column=0)
ttk.Button(root, text="Stop", command=stop_reading).grid(row=2, column=1)

output_text = tk.Text(root, width=50, height=10)
output_text.grid(row=3, column=0, columnspan=2)

# Matplotlib Figure
fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=4, column=0, columnspan=2)

root.mainloop()