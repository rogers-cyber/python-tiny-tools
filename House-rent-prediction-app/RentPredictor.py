"""
RentPredictor v1.0 - Smart Housing Intelligence Tool
ML-powered house rent estimation with modern UI
"""

import os, sys, threading
import tkinter as tk
from tkinter import messagebox

import numpy as np
import joblib

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


# ---------------------- ML WORKER ----------------------
class PredictionWorker:
    def __init__(self, model, features, callback):
        self.model = model
        self.features = features
        self.callback = callback

    def run(self):
        try:
            prediction = self.model.predict([self.features])[0]
            self.callback(round(prediction, 2))
        except Exception as e:
            self.callback(None, str(e))


# ---------------------- MAIN APP ----------------------
class RentPredictorApp:
    APP_NAME = "RentPredictor"
    APP_VERSION = "1.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(900, 520)

        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except:
            pass

        self.model = self._load_model()
        self._build_ui()

    # ---------------------- LOAD MODEL ----------------------
    def _load_model(self):
        try:
            return joblib.load(resource_path("rent_model.pkl"))
        except:
            # fallback dummy model
            class DummyModel:
                def predict(self, X):
                    size, bhk, bath, city = X[0]
                    return [size * 25 + bhk * 1500 + bath * 1000 + city * 2000]
            return DummyModel()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=15)
        main.pack(fill=BOTH, expand=True)

        tb.Label(
            main,
            text="🏠 RentPredictor - Smart Rent Estimation",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(0, 5))

        tb.Label(
            main,
            text="AI-powered house rent prediction engine",
            font=("Segoe UI", 10, "italic"),
            foreground="#9ca3af"
        ).pack(pady=(0, 25))

        form = tb.Labelframe(main, text="Property Details", padding=15)
        form.pack(fill=X, pady=(0, 20))

        # Inputs
        self.size_var = tk.DoubleVar()
        self.bhk_var = tk.IntVar()
        self.bath_var = tk.IntVar()
        self.city_var = tk.IntVar()

        self._add_field(form, "House Size (sq ft)", self.size_var, 0)
        self._add_field(form, "BHK", self.bhk_var, 1)
        self._add_field(form, "Bathrooms", self.bath_var, 2)

        tb.Label(form, text="City Category").grid(row=3, column=0, sticky=W, pady=5)
        self.city_combo = tb.Combobox(
            form,
            values=["Small City", "Metro City"],
            state="readonly"
        )
        self.city_combo.current(0)
        self.city_combo.grid(row=3, column=1, sticky=EW, pady=5)

        # Actions
        actions = tb.Frame(main)
        actions.pack(fill=X, pady=(0, 15))

        self.predict_btn = tb.Button(
            actions,
            text="🔮 Predict Rent",
            bootstyle=SUCCESS,
            command=self.predict
        )
        self.predict_btn.pack(side=LEFT, padx=5)

        tb.Button(
            actions,
            text="ℹ️ About",
            bootstyle=INFO,
            command=self.show_about
        ).pack(side=LEFT, padx=5)

        # Result
        self.result_label = tb.Label(
            main,
            text="Estimated Monthly Rent: —",
            font=("Segoe UI", 18, "bold"),
            foreground="#22c55e"
        )
        self.result_label.pack(pady=20)

    def _add_field(self, parent, label, var, row):
        tb.Label(parent, text=label).grid(row=row, column=0, sticky=W, pady=5)
        tb.Entry(parent, textvariable=var).grid(row=row, column=1, sticky=EW, pady=5)
        parent.columnconfigure(1, weight=1)

    # ---------------------- ACTIONS ----------------------
    def predict(self):
        try:
            size = self.size_var.get()
            bhk = self.bhk_var.get()
            bath = self.bath_var.get()
            city = 1 if self.city_combo.get() == "Metro City" else 0

            if size <= 0 or bhk <= 0 or bath <= 0:
                raise ValueError

        except:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values")
            return

        self.result_label.config(text="Estimating rent…")

        worker = PredictionWorker(
            self.model,
            [size, bhk, bath, city],
            self.show_result
        )

        threading.Thread(target=worker.run, daemon=True).start()

    def show_result(self, rent, error=None):
        if error:
            messagebox.showerror("Prediction Error", error)
            self.result_label.config(text="Estimated Monthly Rent: —")
        else:
            self.result_label.config(
                text=f"Estimated Monthly Rent: ₹ {rent:,}"
            )

    # ---------------------- ABOUT ----------------------
    def show_about(self):
        messagebox.showinfo(
            f"About {self.APP_NAME}",
            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
            "• Machine Learning powered rent estimation\n"
            "• Clean enterprise-grade UI\n"
            "• Threaded predictions (no UI freeze)\n"
            "• Supports trained ML models\n\n"
            "🏢 Built by Mate Technologies"
        )

    # ---------------------- RUN ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- START ----------------------
if __name__ == "__main__":
    app = RentPredictorApp()
    app.run()
