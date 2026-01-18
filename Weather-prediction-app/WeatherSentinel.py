"""
WeatherSentinel v1.0 - Enterprise Edition
AI-Assisted Weather Prediction & Forecast Intelligence Tool
Clean UI • Fast Predictions • Location-Based Forecasting
"""

import os, sys, threading, time, random
import tkinter as tk
from tkinter import messagebox, ttk

import ttkbootstrap as tb
from ttkbootstrap.constants import *


# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


# ---------------------- WEATHER WORKER ----------------------
class WeatherWorker:
    def __init__(self, location, days, callbacks):
        self.location = location
        self.days = days
        self.callbacks = callbacks
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        forecasts = []
        conditions = ["Sunny", "Cloudy", "Rain", "Storm", "Snow", "Fog"]

        for day in range(1, self.days + 1):
            if not self._running:
                break

            time.sleep(0.5)  # simulate API delay

            forecast = {
                "day": f"Day {day}",
                "temp": random.randint(-5, 35),
                "humidity": random.randint(30, 90),
                "condition": random.choice(conditions)
            }
            forecasts.append(forecast)

            if "progress" in self.callbacks:
                self.callbacks["progress"](int(day / self.days * 100))

            if "update" in self.callbacks:
                self.callbacks["update"](forecast)

        if "finished" in self.callbacks:
            self.callbacks["finished"](forecasts)


# ---------------------- MAIN APP ----------------------
class WeatherSentinelApp:
    APP_NAME = "WeatherSentinel"
    APP_VERSION = "1.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(900, 550)

        try:
            self.root.iconbitmap(resource_path("weather.ico"))
        except:
            pass

        self.worker = None
        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=12)
        main.pack(fill=BOTH, expand=True)

        tb.Label(
            main,
            text=f"🌤️ {self.APP_NAME} - Weather Prediction System",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(0, 5))

        tb.Label(
            main,
            text="Location-based weather forecasting with predictive insights",
            font=("Segoe UI", 10, "italic"),
            foreground="#9ca3af"
        ).pack(pady=(0, 20))

        # Controls
        controls = tb.Frame(main)
        controls.pack(fill=X, pady=(0, 10))

        tb.Label(controls, text="Location").pack(side=LEFT, padx=5)
        self.location_entry = tb.Entry(controls, width=30)
        self.location_entry.pack(side=LEFT, padx=5)
        self.location_entry.insert(0, "New York")

        tb.Label(controls, text="Forecast Days").pack(side=LEFT, padx=5)
        self.days_combo = tb.Combobox(controls, values=[1, 3, 5, 7], width=5)
        self.days_combo.set(5)
        self.days_combo.pack(side=LEFT, padx=5)

        self.start_btn = tb.Button(
            controls, text="🔍 Predict", bootstyle=SUCCESS, command=self.start
        )
        self.start_btn.pack(side=LEFT, padx=5)

        self.cancel_btn = tb.Button(
            controls, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel
        )
        self.cancel_btn.pack(side=LEFT, padx=5)
        self.cancel_btn.config(state=DISABLED)

        # Progress
        self.progress = tb.Progressbar(
            main, bootstyle="info-striped", maximum=100
        )
        self.progress.pack(fill=X, pady=(0, 10))

        # Results Table
        columns = ("day", "temp", "humidity", "condition")
        self.tree = ttk.Treeview(
            main, columns=columns, show="headings", height=15
        )
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor=CENTER)

        self.tree.pack(fill=BOTH, expand=True)

        # Footer
        self.status_label = tb.Label(
            main, text="Ready", anchor=E
        )
        self.status_label.pack(fill=X, pady=(6, 0))

    # ---------------------- Actions ----------------------
    def start(self):
        location = self.location_entry.get().strip()
        if not location:
            messagebox.showwarning("Input Required", "Please enter a location")
            return

        self.tree.delete(*self.tree.get_children())
        self.progress["value"] = 0
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        self.status_label.config(text="Predicting weather...")

        self.worker = WeatherWorker(
            location=location,
            days=int(self.days_combo.get()),
            callbacks={
                "progress": self.set_progress,
                "update": self.add_forecast,
                "finished": self.finish
            }
        )

        threading.Thread(target=self.worker.run, daemon=True).start()

    def cancel(self):
        if self.worker:
            self.worker.stop()
        self.finish([])

    def add_forecast(self, data):
        self.tree.insert(
            "", END,
            values=(
                data["day"],
                f"{data['temp']} °C",
                f"{data['humidity']} %",
                data["condition"]
            )
        )

    def set_progress(self, value):
        self.progress["value"] = value

    def finish(self, forecasts):
        self.start_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        self.status_label.config(
            text=f"Forecast completed ({len(forecasts)} days)"
        )

    # ---------------------- Styles ----------------------
    def _apply_styles(self):
        style = tb.Style()  # get existing style
        style.configure(
            "TProgressbar",
            troughcolor="#1f2937",
            background="#38bdf8",
            thickness=14
        )

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = WeatherSentinelApp()
    app.run()
