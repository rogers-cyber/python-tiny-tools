import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import datetime
import threading
import winsound
import pytz

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("MateTools - Alarm Clock")
root.geometry("950x620")
sv_ttk.set_theme("light")  # default theme

# =========================
# Globals
# =========================
alarms = []
dark_mode_var = tk.BooleanVar(value=False)
timezone_var = tk.StringVar(value="UTC")

# =========================
# Helpers
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def toggle_theme():
    if dark_mode_var.get():
        sv_ttk.set_theme("dark")
        set_status("Theme switched to Dark mode")
    else:
        sv_ttk.set_theme("light")
        set_status("Theme switched to Light mode")

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w", font=("Segoe UI", 10)).pack(side=tk.BOTTOM, fill="x")

# =========================
# Alarm Logic Functions
# =========================
def alarm_thread(alarm):
    tz = pytz.timezone(timezone_var.get())
    while alarm["running"]:
        now_dt = datetime.datetime.now(tz)
        weekday = now_dt.weekday()

        alarm_time_naive = datetime.datetime.strptime(alarm["time"], "%H:%M:%S")
        alarm_time_dt = tz.localize(alarm_time_naive.replace(year=now_dt.year, month=now_dt.month, day=now_dt.day))
        if alarm_time_dt < now_dt:
            alarm_time_dt += datetime.timedelta(days=1)

        remaining = alarm_time_dt - now_dt
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        alarm["remaining_var"].set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        if now_dt.strftime("%H:%M:%S") == alarm["time"]:
            if alarm["recurring"] == "Once" or \
               (alarm["recurring"] == "Daily") or \
               (alarm["recurring"] == "Weekdays" and weekday < 5) or \
               (alarm["recurring"] == "Weekends" and weekday >= 5):
                winsound.Beep(1000, 1000)
                response = messagebox.askyesno("Alarm", f"{alarm['label']} - Time's up! Snooze?")
                if response:
                    future = now_dt + datetime.timedelta(minutes=alarm["snooze"])
                    alarm["time"] = future.strftime("%H:%M:%S")
                    set_status(f"{alarm['label']} snoozed for {alarm['snooze']} minutes")
                else:
                    if alarm["recurring"] == "Once":
                        alarm["running"] = False
                        set_status(f"{alarm['label']} finished")
                        refresh_alarm_list()
            threading.Event().wait(1)
        threading.Event().wait(0.5)

def refresh_alarm_list():
    for widget in alarm_list_frame.winfo_children():
        widget.destroy()
    for i, alarm in enumerate(alarms):
        row_frame = ttk.Frame(alarm_list_frame)
        row_frame.pack(fill="x", pady=2)
        ttk.Label(row_frame, text=f"{alarm['label']} ({alarm['recurring']})", font=("Segoe UI", 12)).pack(side="left", padx=5)
        ttk.Label(row_frame, textvariable=alarm["remaining_var"], font=("Consolas", 12, "bold")).pack(side="left", padx=10)
        ttk.Button(row_frame, text="Stop", style="Reset.TButton", width=8,
                   command=lambda i=i: stop_alarm(i)).pack(side="right", padx=5)
        ttk.Button(row_frame, text="Delete", style="Reset.TButton", width=8,
                   command=lambda i=i: delete_alarm(i)).pack(side="right", padx=5)

def add_alarm():
    time_str = alarm_time_var.get()
    label_str = alarm_label_var.get()
    recurring_str = alarm_recurring_var.get()
    snooze_min = alarm_snooze_var.get()
    try:
        datetime.datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        messagebox.showerror("Invalid Input", "Time must be HH:MM:SS")
        return
    remaining_var = tk.StringVar(value="00:00:00")
    new_alarm = {"time": time_str, "label": label_str, "running": True,
                 "recurring": recurring_str, "snooze": snooze_min,
                 "remaining_var": remaining_var}
    t = threading.Thread(target=alarm_thread, args=(new_alarm,), daemon=True)
    new_alarm["thread"] = t
    alarms.append(new_alarm)
    t.start()
    set_status(f"Alarm '{label_str}' set for {time_str} ({recurring_str})")
    refresh_alarm_list()

def stop_alarm(index):
    alarm = alarms[index]
    alarm["running"] = False
    set_status(f"Alarm '{alarm['label']}' stopped")
    refresh_alarm_list()

def delete_alarm(index):
    alarm = alarms[index]
    alarm["running"] = False
    alarms.pop(index)
    set_status(f"Alarm '{alarm['label']}' deleted")
    refresh_alarm_list()

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

ttk.Label(dash_tab, text="MateTools - Alarm Clock", font=("Segoe UI", 20, "bold")).pack(anchor="w")
ttk.Label(dash_tab, text="Your personal productivity assistant. Never miss an important task or event!", 
          font=("Segoe UI", 14)).pack(anchor="w", pady=(5, 15))

ttk.Label(dash_tab, text="Key Features:", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(5, 5))
features_text = (
    "• Set multiple alarms with custom labels.\n"
    "• Recurring alarms: Once, Daily, Weekdays, Weekends.\n"
    "• Snooze option for alarms.\n"
    "• Time zone support to set alarms globally.\n"
    "• Live countdown timers for each alarm.\n"
    "• Stop/Delete individual alarms.\n"
    "• Dark/Light mode toggle for your comfort."
)
ttk.Label(dash_tab, text=features_text, wraplength=900, justify="left", font=("Segoe UI", 12)).pack(anchor="w", pady=(0,15))

ttk.Label(dash_tab, text="About Developer:", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(5, 5))
about_text = (
    "MateTools – Focused on practical, secure, and user-friendly digital tools for daily life\n"
    "Website: https://matetools.gumroad.com"
)
ttk.Label(dash_tab, text=about_text, wraplength=900, justify="left", font=("Segoe UI", 12)).pack(anchor="w", pady=(0,10))

# =========================
# Set Alarm Tab
# =========================
set_tab = ttk.Frame(tabs, padding=20)
tabs.add(set_tab, text="⏰ Set Alarm")

# Variables
alarm_time_var = tk.StringVar(value="07:00:00")
alarm_label_var = tk.StringVar(value="Alarm 1")
alarm_recurring_var = tk.StringVar(value="Once")
alarm_snooze_var = tk.IntVar(value=5)

# Frame for Alarm Settings
input_frame = ttk.LabelFrame(set_tab, text="Alarm Settings", padding=20)
input_frame.pack(fill="x", pady=10)

# Row 0: Alarm Time
ttk.Label(input_frame, text="Time (HH:MM:SS):", font=("Segoe UI", 12)).grid(row=0, column=0, padx=10, pady=8, sticky="e")
ttk.Entry(input_frame, textvariable=alarm_time_var, width=31, font=("Segoe UI", 12)).grid(row=0, column=1, padx=10, pady=8, sticky="w")

# Row 1: Alarm Label
ttk.Label(input_frame, text="Label:", font=("Segoe UI", 12)).grid(row=1, column=0, padx=10, pady=8, sticky="e")
ttk.Entry(input_frame, textvariable=alarm_label_var, width=31, font=("Segoe UI", 12)).grid(row=1, column=1, padx=10, pady=8, sticky="w")

# Row 2: Recurring Option
ttk.Label(input_frame, text="Recurring:", font=("Segoe UI", 12)).grid(row=2, column=0, padx=10, pady=8, sticky="e")
ttk.Combobox(input_frame, textvariable=alarm_recurring_var,
             values=["Once", "Daily", "Weekdays", "Weekends"], state="readonly",
             font=("Segoe UI", 12), width=28).grid(row=2, column=1, padx=10, pady=8, sticky="w")

# Row 3: Snooze
ttk.Label(input_frame, text="Snooze (minutes):", font=("Segoe UI", 12)).grid(row=3, column=0, padx=10, pady=8, sticky="e")
ttk.Entry(input_frame, textvariable=alarm_snooze_var, width=31, font=("Segoe UI", 12)).grid(row=3, column=1, padx=10, pady=8, sticky="w")

# Row 4: Time Zone
ttk.Label(input_frame, text="Time Zone:", font=("Segoe UI", 12)).grid(row=4, column=0, padx=10, pady=8, sticky="e")
ttk.Combobox(input_frame, textvariable=timezone_var, values=pytz.all_timezones,
             state="readonly", font=("Segoe UI", 12), width=28).grid(row=4, column=1, padx=10, pady=8, sticky="w")

# Row 5: Add Alarm Button
ttk.Button(input_frame, text="Add Alarm", command=add_alarm, style="Action.TButton").grid(row=5, column=0, columnspan=2, pady=15)

# Row 6: Dark Mode Toggle
ttk.Checkbutton(set_tab, text="Dark Mode", variable=dark_mode_var, command=toggle_theme,
                style="TCheckbutton").pack(pady=10)

# =========================
# Active Alarms Tab
# =========================
active_tab = ttk.Frame(tabs, padding=20)
tabs.add(active_tab, text="📋 Active Alarms")
alarm_list_frame = ttk.Frame(active_tab)
alarm_list_frame.pack(fill="both", expand=True)

# =========================
# Run App
# =========================
root.mainloop()
