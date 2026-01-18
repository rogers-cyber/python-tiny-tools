"""
WineSense v1.0 - Wine Quality Prediction Tool
ML-powered Wine Quality Analyzer
Predicts wine quality from physicochemical properties
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import ttkbootstrap as tb
from ttkbootstrap.constants import *


# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


# ---------------------- ML MODEL ----------------------
class WineQualityModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42
        )
        self.trained = False
        self.accuracy = 0.0
        self.feature_names = []

    def train(self, csv_path):
        data = pd.read_csv(csv_path)

        if "quality" not in data.columns:
            raise ValueError("CSV must contain a 'quality' column")

        self.feature_names = [c for c in data.columns if c != "quality"]

        X = data[self.feature_names]
        y = data["quality"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, preds)
        self.trained = True

    def predict(self, features):
        if not self.trained:
            raise RuntimeError("Model not trained")

        # FIX: pass feature names using DataFrame
        X = pd.DataFrame([features], columns=self.feature_names)
        return int(self.model.predict(X)[0])


# ---------------------- MAIN APP ----------------------
class WineSenseApp:
    APP_NAME = "WineSense"
    APP_VERSION = "1.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(900, 600)

        self.model = WineQualityModel()
        self.feature_vars = {}

        self._build_ui()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=15)
        main.pack(fill=BOTH, expand=True)

        tb.Label(
            main,
            text="🍷 WineSense - Quality Prediction",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(0, 5))

        tb.Label(
            main,
            text="Machine Learning Based Wine Quality Estimator",
            font=("Segoe UI", 10, "italic"),
            foreground="#9ca3af"
        ).pack(pady=(0, 20))

        # ---------------- Training Section ----------------
        train_frame = tb.Labelframe(main, text="Model Training", padding=10)
        train_frame.pack(fill=X, pady=(0, 10))

        tb.Button(
            train_frame,
            text="📊 Load Wine CSV & Train Model",
            bootstyle=SUCCESS,
            command=self.train_model
        ).pack(side=LEFT, padx=5)

        self.train_status = tb.Label(train_frame, text="Model not trained")
        self.train_status.pack(side=LEFT, padx=10)

        # ---------------- Feature Input ----------------
        input_frame = tb.Labelframe(main, text="Wine Properties", padding=10)
        input_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        self.features = [
            "fixed acidity",
            "volatile acidity",
            "citric acid",
            "residual sugar",
            "chlorides",
            "free sulfur dioxide",
            "total sulfur dioxide",
            "density",
            "pH",
            "sulphates",
            "alcohol",
        ]

        grid = tb.Frame(input_frame)
        grid.pack()

        for i, feat in enumerate(self.features):
            tb.Label(grid, text=feat.title()).grid(
                row=i, column=0, sticky=W, pady=4, padx=6
            )
            var = tk.DoubleVar(value=0.0)
            self.feature_vars[feat] = var
            tb.Entry(grid, textvariable=var, width=18).grid(
                row=i, column=1, pady=4
            )

        # ---------------- Prediction Section ----------------
        predict_frame = tb.Frame(main)
        predict_frame.pack(fill=X, pady=(10, 0))

        tb.Button(
            predict_frame,
            text="🔮 Predict Quality",
            bootstyle=PRIMARY,
            command=self.predict_quality
        ).pack(side=LEFT, padx=5)

        self.result_label = tb.Label(
            predict_frame,
            text="Quality: -",
            font=("Segoe UI", 14, "bold")
        )
        self.result_label.pack(side=LEFT, padx=20)

    # ---------------------- Actions ----------------------
    def train_model(self):
        path = filedialog.askopenfilename(
            title="Select Wine Quality CSV",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return

        self.train_status.config(text="Training model...")
        threading.Thread(
            target=self._train_thread,
            args=(path,),
            daemon=True
        ).start()

    def _train_thread(self, path):
        try:
            self.model.train(path)
            self.root.after(
                0,
                lambda: self.train_status.config(
                    text=f"Model trained | Accuracy: {self.model.accuracy:.2%}"
                )
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror("Training Error", str(e))
            )

    def predict_quality(self):
        if not self.model.trained:
            messagebox.showwarning("Model", "Please train the model first")
            return

        try:
            features = [self.feature_vars[f].get() for f in self.features]
            quality = self.model.predict(features)
            self.result_label.config(text=f"Quality: {quality}")
        except Exception as e:
            messagebox.showerror("Prediction Error", str(e))

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = WineSenseApp()
    app.run()
