import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("MateTools - Countdown Timer")
root.geometry("900x500")
# Optional: root.iconbitmap("logo.ico")  # if you have an icon

sv_ttk.set_theme("light")  # Default theme

# =========================
# Globals
# =========================
timer_running = False
hours_var = tk.StringVar(value="0")
minutes_var = tk.StringVar(value="0")
seconds_var = tk.StringVar(value="0")
time_left_var = tk.StringVar(value="00:00:00")
dark_mode_var = tk.BooleanVar(value=False)

# =========================
# Helpers
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def toggle_theme():
    style.theme_use("clam")
    if dark_mode_var.get():
        root.configure(bg="#2E2E2E")
        style.configure("TLabel", background="#2E2E2E", foreground="white")
        style.configure("TFrame", background="#2E2E2E")
        style.configure("TLabelframe", background="#2E2E2E", foreground="white")
        style.configure("TCheckbutton", background="#2E2E2E", foreground="white")
        style.configure("TNotebook", background="#2E2E2E")
        style.configure("TNotebook.Tab", background="#444444", foreground="white")
        style.map("TNotebook.Tab", background=[("selected", "#90caf9")], foreground=[("selected", "black")])
    else:
        root.configure(bg="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="black")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TLabelframe", background="#FFFFFF", foreground="black")
        style.configure("TCheckbutton", background="#FFFFFF", foreground="black")
        style.configure("TNotebook", background="#FFFFFF")
        style.configure("TNotebook.Tab", background="#e0e0e0", foreground="black")
        style.map("TNotebook.Tab", background=[("selected", "#90caf9")], foreground=[("selected", "black")])
    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Custom Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#4CAF50", padding=8)
style.map("Action.TButton", background=[("active", "#45a049"), ("disabled", "#a5d6a7")])
style.configure("Reset.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#f44336", padding=8)
style.map("Reset.TButton", background=[("active", "#d32f2f"), ("disabled", "#ef9a9a")])

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w", font=("Segoe UI", 10)).pack(side=tk.BOTTOM, fill="x")

# =========================
# Notebook
# =========================
tabs = ttk.Notebook(root)
tabs.pack(expand=True, fill="both", padx=20, pady=20)

# =========================
# Dashboard Tab
# =========================
dash_tab = ttk.Frame(tabs, padding=20)
tabs.add(dash_tab, text="🏠 Dashboard")

ttk.Label(dash_tab, text="MateTools - Countdown Timer",
          font=("Segoe UI", 20, "bold")).pack(anchor="w")
ttk.Label(dash_tab, text="A simple, modern countdown timer tool with flexible input and live display.",
          font=("Segoe UI", 11)).pack(anchor="w", pady=(5,15))

ttk.Label(dash_tab, text="Key Features:", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(10,5))
features_frame = ttk.Frame(dash_tab)
features_frame.pack(fill="x", pady=5)

def create_feature_card(parent, title, desc):
    card = ttk.LabelFrame(parent, text=title, padding=15)
    ttk.Label(card, text=desc, wraplength=250, font=("Segoe UI", 10)).pack(anchor="w")
    return card

create_feature_card(features_frame, "⏱ Flexible Timer Input",
                    "Set hours, minutes, and seconds easily.").grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
create_feature_card(features_frame, "▶️ Start / ⏸ Pause / 🔄 Reset",
                    "Control your countdown easily with intuitive buttons.").grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
create_feature_card(features_frame, "🌙 Dark / Light Mode",
                    "Switch themes to match your preference.").grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
features_frame.columnconfigure((0,1,2), weight=1)

ttk.Label(dash_tab, text="About This Tool", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(15,5))
about_text = (
    "MateTools Countdown Timer is built for productivity and simplicity. "
    "It allows you to set a countdown for any task, keep track of remaining time, "
    "and customize your experience with light/dark mode. "
    "\n\nBuilt by MateTools - https://matetools.gumroad.com"
)
ttk.Label(dash_tab, text=about_text, wraplength=850, justify="left", font=("Segoe UI", 10)).pack(anchor="w")

# =========================
# Timer Tab
# =========================
timer_tab = ttk.Frame(tabs, padding=20)
tabs.add(timer_tab, text="⏱ Countdown Timer")

# Timer Logic
def update_timer_display():
    time_left_var.set(f"{int(hours_var.get()):02d}:{int(minutes_var.get()):02d}:{int(seconds_var.get()):02d}")

def countdown():
    global timer_running
    if not timer_running:
        return
    try:
        h = int(hours_var.get())
        m = int(minutes_var.get())
        s = int(seconds_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid integers for hours, minutes, and seconds.")
        timer_running = False
        return
    total_seconds = h*3600 + m*60 + s
    if total_seconds <= 0:
        timer_running = False
        messagebox.showinfo("Time's up!", "Countdown finished.")
        return
    total_seconds -= 1
    hours_var.set(str(total_seconds // 3600))
    minutes_var.set(str((total_seconds % 3600) // 60))
    seconds_var.set(str(total_seconds % 60))
    update_timer_display()
    root.after(1000, countdown)

def start_timer():
    global timer_running
    timer_running = True
    countdown()
    set_status("Countdown started.")

def pause_timer():
    global timer_running
    timer_running = False
    set_status("Countdown paused.")

def reset_timer():
    global timer_running
    timer_running = False
    hours_var.set("0")
    minutes_var.set("0")
    seconds_var.set("0")
    update_timer_display()
    set_status("Countdown reset.")

# Timer UI
ttk.Label(timer_tab, text="Countdown Timer", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0,15))
time_frame = ttk.Frame(timer_tab)
time_frame.pack(pady=10)

ttk.Label(time_frame, text="Hours:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
ttk.Entry(time_frame, textvariable=hours_var, width=5, font=("Segoe UI", 12)).grid(row=0, column=1, padx=5)
ttk.Label(time_frame, text="Minutes:", font=("Segoe UI", 11)).grid(row=0, column=2, padx=5)
ttk.Entry(time_frame, textvariable=minutes_var, width=5, font=("Segoe UI", 12)).grid(row=0, column=3, padx=5)
ttk.Label(time_frame, text="Seconds:", font=("Segoe UI", 11)).grid(row=0, column=4, padx=5)
ttk.Entry(time_frame, textvariable=seconds_var, width=5, font=("Segoe UI", 12)).grid(row=0, column=5, padx=5)

ttk.Label(timer_tab, textvariable=time_left_var, font=("Consolas", 40, "bold")).pack(pady=20)

btn_frame = ttk.Frame(timer_tab)
btn_frame.pack(pady=10)
ttk.Button(btn_frame, text="Start", command=start_timer, style="Action.TButton").pack(side="left", padx=5)
ttk.Button(btn_frame, text="Pause", command=pause_timer, style="Action.TButton").pack(side="left", padx=5)
ttk.Button(btn_frame, text="Reset", command=reset_timer, style="Reset.TButton").pack(side="left", padx=5)
ttk.Checkbutton(timer_tab, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(pady=15)

# =========================
# Run App
# =========================
update_timer_display()
root.mainloop()
