# ==========================================================
# Screenshot PRO - Screen Capture Tool
# Professional Desktop Tool
# ==========================================================

import os
import sys
import threading
import time
import traceback
from queue import Queue, Empty

import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from PIL import ImageGrab


# =================== APP CONFIG ===================

APP_NAME = "Screenshot PRO"
APP_VERSION = "1.0.0"


# =================== APP ===================

app = tk.Tk()
app.title(f"{APP_NAME} {APP_VERSION}")
app.geometry("1050x620")

tb.Style("darkly")


# =================== UTILITY ===================

def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


def log_error():
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(traceback.format_exc() + "\n")


def show_about():
    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME} v{APP_VERSION}\n\n"
        "Professional Screen Capture Tool\n\n"
        "Features:\n"
        "• Full screen capture\n"
        "• Region capture\n"
        "• Delayed screenshots\n"
        "• Custom output folder\n"
        "• Progress tracking\n"
        "• Processing log\n\n"
        "Built with Python + Tkinter + ttkbootstrap\n"
        "© 2026 Mate Technologies\n"
    )


# =================== MENU ===================

menubar = tb.Menu(app)

help_menu = tb.Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=show_about)

menubar.add_cascade(label="Help", menu=help_menu)

app.config(menu=menubar)


# =================== FLAGS ===================

stop_flag = False
pause_flag = False

ui_queue = Queue()

output_path = tb.StringVar(value=os.getcwd())
delay_seconds = tb.IntVar(value=0)


# =================== TITLE ===================

tb.Label(
    app,
    text=APP_NAME,
    font=("Segoe UI", 24, "bold")
).pack(pady=(10, 2))

tb.Label(
    app,
    text="Professional Screen Capture Tool",
    font=("Segoe UI", 10, "italic"),
    foreground="#9ca3af"
).pack(pady=(0, 10))


# =================== FRAME: CAPTURE CONTROLS ===================

frame1 = tb.Labelframe(app, text="Capture Controls", padding=10)
frame1.pack(fill="x", padx=10, pady=6)


# Delay

tb.Label(frame1, text="Delay (seconds):").pack(side="left")

delay_entry = tb.Entry(frame1, textvariable=delay_seconds, width=6)
delay_entry.pack(side="left", padx=5)


# Output Folder

tb.Label(frame1, text="Output Folder:", width=13).pack(side="left", padx=(20, 0))

tb.Entry(frame1, textvariable=output_path, width=40).pack(side="left", padx=6)


def browse_output():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)


tb.Button(frame1, text="Browse", command=browse_output).pack(side="left", padx=4)


# =================== SCREENSHOT FUNCTIONS ===================

def capture_fullscreen():

    try:

        if delay_seconds.get() > 0:
            ui_queue.put(("log", f"Waiting {delay_seconds.get()} seconds..."))
            time.sleep(delay_seconds.get())

        img = ImageGrab.grab()

        file_name = f"screenshot_{int(time.time())}.png"

        path = os.path.join(output_path.get(), file_name)

        img.save(path)

        ui_queue.put(("log", f"✔ Saved: {file_name}"))

    except Exception:
        log_error()
        ui_queue.put(("log", "❌ Screenshot failed"))

    ui_queue.put(("progress", 100))


# =================== REGION CAPTURE ===================

def capture_region():

    selector = tk.Toplevel()
    selector.attributes("-fullscreen", True)
    selector.attributes("-alpha", 0.3)
    selector.configure(bg="black")

    canvas = tk.Canvas(selector, cursor="cross", bg="black")
    canvas.pack(fill="both", expand=True)

    start_x = start_y = 0
    rect = None

    def on_press(event):
        nonlocal start_x, start_y, rect
        start_x = event.x
        start_y = event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_drag(event):
        canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_release(event):

        x1 = min(start_x, event.x)
        y1 = min(start_y, event.y)
        x2 = max(start_x, event.x)
        y2 = max(start_y, event.y)

        selector.destroy()

        try:

            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            file_name = f"screenshot_region_{int(time.time())}.png"

            path = os.path.join(output_path.get(), file_name)

            img.save(path)

            ui_queue.put(("log", f"✔ Region saved: {file_name}"))

        except:
            log_error()
            ui_queue.put(("log", "❌ Region capture failed"))

        ui_queue.put(("progress", 100))

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)


# =================== THREAD STARTERS ===================

def start_fullscreen():
    progress_var.set(0)
    threading.Thread(target=capture_fullscreen, daemon=True).start()


def start_region():
    progress_var.set(0)
    capture_region()


# =================== BUTTONS ===================

tb.Button(
    frame1,
    text="📸 Full Screen",
    bootstyle="success",
    command=start_fullscreen
).pack(side="left", padx=6)

tb.Button(
    frame1,
    text="🖼 Capture Region",
    bootstyle="info",
    command=start_region
).pack(side="left", padx=4)


# =================== PROGRESS ===================

frame2 = tb.Labelframe(app, text="Progress", padding=8)
frame2.pack(fill="x", padx=10)

progress_var = tb.IntVar()

tb.Progressbar(
    frame2,
    variable=progress_var,
    maximum=100,
    length=400
).pack(side="left", padx=10)

status_lbl = tb.Label(frame2, text="Status: Ready")
status_lbl.pack(side="left", padx=10)


# =================== LOG ===================

frame3 = tb.Labelframe(app, text="Processing Log", padding=8)
frame3.pack(fill="both", expand=True, padx=10, pady=6)

log_text = tk.Text(frame3, height=10)
log_text.pack(side="left", fill="both", expand=True)

scroll = tk.Scrollbar(frame3, command=log_text.yview)
scroll.pack(side="right", fill="y")

log_text.config(yscrollcommand=scroll.set, state="disabled")


# =================== UI QUEUE ===================

def process_ui_queue():

    try:

        while True:

            cmd, data = ui_queue.get_nowait()

            if cmd == "progress":

                progress_var.set(data)

            elif cmd == "log":

                log_text.config(state="normal")
                log_text.insert("end", data + "\n")
                log_text.see("end")
                log_text.config(state="disabled")

            elif cmd == "status":

                status_lbl.config(text=f"Status: {data}")

    except Empty:
        pass

    app.after(100, process_ui_queue)


# =================== START UI ===================

app.after(100, process_ui_queue)

app.mainloop()
