"""
AutoValue Pro v1.0 - Enterprise Edition
AI-Powered Car Price Prediction Tool
Fast, Accurate & User-Friendly Desktop GUI
"""

import os, sys, threading
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

import numpy as np
from sklearn.linear_model import LinearRegression


# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


# ---------------------- ML WORKER ----------------------
class PredictionWorker:
    def __init__(self, features, callbacks):
        self.features = features
        self.callbacks = callbacks
        self._running = True

        # Dummy trained model (demo)
        self.model = LinearRegression()
        X = np.array([
            [1, 5000, 2015],
            [2, 3000, 2018],
            [3, 2000, 2020],
            [1, 8000, 2012],
            [2, 4000, 2016]
        ])
        y = np.array([12000, 15000, 18000, 9000, 14000])
        self.model.fit(X, y)

    def stop(self):
        self._running = False

    def run(self):
        try:
            if "progress" in self.callbacks:
                self.callbacks

            prediction = self.model.predict([self.features])[0]

            if "progress" in self.callbacks:
                self.callbacks

            if not self._running:
                return

            if "result" in self.callbacks:
                self.callbacks["result"](round(prediction, 2))

        except Exception as e:
            if "error" in self.callbacks:
                self.callbacks["error"](str(e))

        if "progress" in self.callbacks:
            self.callbacks


# ---------------------- MAIN APP ----------------------
class AutoValueApp:
    APP_NAME = "AutoValue Pro"
    APP_VERSION = "1.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(900, 550)

        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except:
            pass

        self.worker = None
        self.target_progress = 0
        self.smooth_value = 0

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=20)
        main.pack(fill=BOTH, expand=True)

        tb.Label(
            main,
            text="🚗 AutoValue Pro – Car Price Predictor",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(0, 6))

        tb.Label(
            main,
            text="AI-Driven Used Car Price Estimation",
            font=("Segoe UI", 10, "italic"),
            foreground="#9ca3af"
        ).pack(pady=(0, 25))

        form = tb.Frame(main)
        form.pack(fill=X, pady=10)

        # Inputs
        self.owner_var = tk.IntVar(value=1)
        self.km_var = tk.IntVar(value=3000)
        self.year_var = tk.IntVar(value=2018)

        tb.Label(form, text="Number of Owners").grid(row=0, column=0, sticky=W, pady=6)
        tb.Spinbox(form, from_=1, to=5, textvariable=self.owner_var, width=10).grid(row=0, column=1, padx=10)

        tb.Label(form, text="Kilometers Driven").grid(row=1, column=0, sticky=W, pady=6)
        tb.Entry(form, textvariable=self.km_var, width=15).grid(row=1, column=1, padx=10)

        tb.Label(form, text="Manufacturing Year").grid(row=2, column=0, sticky=W, pady=6)
        tb.Entry(form, textvariable=self.year_var, width=15).grid(row=2, column=1, padx=10)

        # Buttons
        btns = tb.Frame(main)
        btns.pack(pady=15)

        self.predict_btn = tb.Button(
            btns, text="🔮 Predict Price", bootstyle=SUCCESS, command=self.start_prediction
        )
        self.predict_btn.pack(side=LEFT, padx=6)

        self.cancel_btn = tb.Button(
            btns, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel, state=DISABLED
        )
        self.cancel_btn.pack(side=LEFT, padx=6)

        # Progress
        self.progress = tb.Progressbar(
            main, maximum=100, bootstyle="success-striped"
        )
        self.progress.pack(fill=X, pady=(20, 10))

        # Result
        self.result_label = tb.Label(
            main,
            text="Predicted Price: —",
            font=("Segoe UI", 16, "bold"),
            foreground="#4ade80"
        )
        self.result_label.pack(pady=10)

        self.root.after(15, self.animate_progress)

    # ---------------------- Actions ----------------------
    def start_prediction(self):
        try:
            features = [
                self.owner_var.get(),
                self.km_var.get(),
                self.year_var.get()
            ]
        except Exception:
            messagebox.showerror("Input Error", "Invalid input values")
            return

        self.progress["value"] = 0
        self.target_progress = 0
        self.smooth_value = 0

        self.predict_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)

        threading.Thread(
            target=self._run_worker,
            args=(features,),
            daemon=True
        ).start()

    def _run_worker(self, features):
        self.worker = PredictionWorker(
            features,
            callbacks={
                "progress": self.set_target,
                "result": self.show_result,
                "error": self.show_error
            }
        )
        self.worker.run()

    def show_result(self, price):
        self.result_label.config(text=f"Predicted Price: ${price:,}")
        self.finish()

    def show_error(self, msg):
        messagebox.showerror("Prediction Error", msg)
        self.finish()

    def cancel(self):
        if self.worker:
            self.worker.stop()
        self.finish()

    def finish(self):
        self.predict_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        self.progress["value"] = 100

    # ---------------------- Progress Animation ----------------------
    def set_target(self, v):
        self.target_progress = v

    def animate_progress(self):
        if self.smooth_value < self.target_progress:
            self.smooth_value += 1
            self.progress["value"] = self.smooth_value
        self.root.after(15, self.animate_progress)

    # ---------------------- Styles ----------------------
    def _apply_styles(self):
        style = tb.Style()
        style.configure(
            "TProgressbar",
            troughcolor="#1b1f3a",
            background="#22c55e",
            thickness=14
        )

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = AutoValueApp()
    app.run()
