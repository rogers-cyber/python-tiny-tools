import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Stopwatch Pro")
root.geometry("640x540")

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
countdown_mode = tk.BooleanVar(value=False)

running = False
start_time = None
elapsed_time = 0.0

countdown_seconds = tk.IntVar(value=60)

laps = []

time_var = tk.StringVar(value="00:00:00.000")

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"

    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)

    time_label.configure(background=bg, foreground="#00FFAA" if dark_mode_var.get() else fg)
    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Core Logic
# =========================
def format_time(seconds):
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"

def timer_loop():
    global elapsed_time, running
    while running:
        now = time.perf_counter()

        if countdown_mode.get():
            remaining = countdown_seconds.get() - (now - start_time)
            if remaining <= 0:
                running = False
                time_var.set("00:00:00.000")
                messagebox.showinfo("⏰ Time's up", "Countdown finished!")
                set_status("Countdown completed")
                return
            time_var.set(format_time(remaining))
        else:
            elapsed_time = now - start_time
            time_var.set(format_time(elapsed_time))

        time.sleep(0.01)

def start():
    global running, start_time
    if running:
        return

    running = True
    start_time = time.perf_counter() - elapsed_time
    threading.Thread(target=timer_loop, daemon=True).start()
    set_status("Timer started")

def stop():
    global running
    running = False
    set_status("Timer stopped")

def reset():
    global running, elapsed_time, start_time, laps
    running = False
    elapsed_time = 0.0
    start_time = None
    laps.clear()
    lap_list.delete(0, tk.END)
    time_var.set("00:00:00.000")
    set_status("Timer reset")

def add_lap():
    if not running or countdown_mode.get():
        return

    lap_time = format_time(elapsed_time)
    laps.append(elapsed_time)
    lap_list.insert(tk.END, f"Lap {len(laps)} — {lap_time}")
    set_status(f"Lap {len(laps)} recorded")

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Action.TButton",
    font=("Segoe UI", 11, "bold"),
    foreground="white",
    background="#4CAF50",
    padding=8
)
style.map("Action.TButton", background=[("active", "#45a049")])

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill="x")

# =========================
# Main UI
# =========================
main = ttk.Frame(root, padding=20)
main.pack(expand=True, fill="both")

ttk.Label(main, text="Stopwatch Pro",
          font=("Segoe UI", 22, "bold")).pack()

ttk.Label(main, text="Stopwatch • Countdown • Lap Timer",
          font=("Segoe UI", 11)).pack(pady=(0, 10))

# =========================
# Timer Display
# =========================
time_label = ttk.Label(
    main,
    textvariable=time_var,
    font=("Segoe UI", 36, "bold"),
    anchor="center"
)
time_label.pack(pady=12)

# =========================
# Controls
# =========================
controls = ttk.Frame(main)
controls.pack(pady=8)

ttk.Button(controls, text="▶ Start", command=start,
           style="Action.TButton").pack(side="left", padx=4)

ttk.Button(controls, text="⏸ Stop", command=stop,
           style="Action.TButton").pack(side="left", padx=4)

ttk.Button(controls, text="⟲ Reset", command=reset,
           style="Action.TButton").pack(side="left", padx=4)

ttk.Button(controls, text="🏁 Lap", command=add_lap,
           style="Action.TButton").pack(side="left", padx=4)

# =========================
# Countdown
# =========================
countdown_frame = ttk.LabelFrame(main, text="Countdown Mode", padding=10)
countdown_frame.pack(fill="x", pady=8)

ttk.Checkbutton(
    countdown_frame,
    text="Enable Countdown",
    variable=countdown_mode
).pack(side="left", padx=6)

ttk.Label(countdown_frame, text="Seconds:").pack(side="left", padx=6)

ttk.Spinbox(
    countdown_frame,
    from_=1,
    to=86400,
    textvariable=countdown_seconds,
    width=8
).pack(side="left")

# =========================
# Laps
# =========================
laps_frame = ttk.LabelFrame(main, text="Lap Times", padding=10)
laps_frame.pack(fill="both", expand=True, pady=8)

lap_list = tk.Listbox(
    laps_frame,
    height=7,
    font=("Segoe UI", 10)
)
lap_list.pack(fill="both", expand=True)

# =========================
# Options
# =========================
options = ttk.Frame(main)
options.pack(pady=10)

ttk.Checkbutton(
    options,
    text="Dark Mode",
    variable=dark_mode_var,
    command=toggle_theme
).pack()

# =========================
# Run App
# =========================
root.mainloop()
