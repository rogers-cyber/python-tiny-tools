import threading
import webbrowser
import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple
import time
import random
import math

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

# ---------------- CONFIG ---------------- #
UPDATE_INTERVAL = 2  # seconds
START_LAT = 37.7749   # San Francisco (example)
START_LON = -122.4194

# ---------------- GLOBAL STATE ---------------- #
tracking_active = False
location_history: List["Location"] = []

# ---------------- DATA STRUCTURE ---------------- #
@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float
    timestamp: str

# ---------------- GPS SIMULATION ---------------- #
def generate_next_location(lat: float, lon: float) -> Tuple[float, float]:
    delta = 0.0005
    lat += random.uniform(-delta, delta)
    lon += random.uniform(-delta, delta)
    return round(lat, 6), round(lon, 6)

# ---------------- TRACKING THREAD ---------------- #
def tracking_loop():
    global tracking_active
    lat, lon = START_LAT, START_LON

    while tracking_active:
        lat, lon = generate_next_location(lat, lon)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        loc = Location(lat, lon, timestamp)
        location_history.append(loc)

        app.after(0, lambda l=loc: display_location(l))
        time.sleep(UPDATE_INTERVAL)

# ---------------- UI HELPERS ---------------- #
def display_location(location: Location):
    text.configure(state="normal")
    text.insert(
        "end",
        f"📍 {location.timestamp}\nLatitude: {location.latitude}\nLongitude: {location.longitude}\n\n"
    )
    text.see("end")
    text.configure(state="disabled")

def open_in_maps():
    if not location_history:
        return
    loc = location_history[-1]
    url = f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}"
    webbrowser.open_new_tab(url)

# ---------------- CONTROL FUNCTIONS ---------------- #
def start_tracking():
    global tracking_active
    if tracking_active:
        return
    tracking_active = True
    status_label.config(text="🟢 Tracking Active", bootstyle="success")
    threading.Thread(target=tracking_loop, daemon=True).start()

def stop_tracking():
    global tracking_active
    tracking_active = False
    status_label.config(text="🔴 Tracking Stopped", bootstyle="danger")

def clear_history():
    location_history.clear()
    text.configure(state="normal")
    text.delete("1.0", "end")
    text.configure(state="disabled")

# ---------------- UI SETUP ---------------- #
app = tb.Window(
    title="Real-Time GPS Tracking System",
    themename="darkly",
    size=(800, 600),
    resizable=(True, True),
)

top = tb.Frame(app, padding=15)
top.pack(fill=tk.X)

tb.Label(
    top,
    text="📡 Real-Time GPS Tracking System",
    font=("Segoe UI", 18, "bold"),
).pack(anchor=tk.W)

status_label = tb.Label(top, text="🔴 Tracking Stopped", bootstyle="danger")
status_label.pack(anchor=tk.W, pady=5)

btn_frame = tb.Frame(top)
btn_frame.pack(fill=tk.X, pady=5)

tb.Button(btn_frame, text="▶ Start Tracking", bootstyle="success", command=start_tracking).pack(side=tk.LEFT, padx=5)
tb.Button(btn_frame, text="⏹ Stop Tracking", bootstyle="danger", command=stop_tracking).pack(side=tk.LEFT, padx=5)
tb.Button(btn_frame, text="🗺 Open in Maps", bootstyle="info", command=open_in_maps).pack(side=tk.LEFT, padx=5)
tb.Button(btn_frame, text="🧹 Clear", bootstyle="warning", command=clear_history).pack(side=tk.LEFT, padx=5)

# ---------------- RESULTS ---------------- #
result_frame = tb.Frame(app)
result_frame.pack(fill=tk.BOTH, expand=True)

result_box = ScrolledText(result_frame)
result_box.pack(fill=tk.BOTH, expand=True)

text = result_box.text
text.configure(state="disabled", wrap="word")

app.mainloop()
