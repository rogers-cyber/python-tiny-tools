"""
HousePrice Sentinel v1.0 - Enterprise Edition
Smart Real Estate Price Prediction Tool
ML-powered house valuation with modern UI
"""

import os, sys, threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import pandas as pd
import numpy as np

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


# ---------------------- ML WORKER ----------------------
class PriceModelWorker:
    def __init__(self, csv_path, callbacks):
        self.csv_path = csv_path
        self.callbacks = callbacks
        self.model = LinearRegression()

    def run(self):
        try:
            df = pd.read_csv(self.csv_path)

            X = df[["Area", "Bedrooms", "Bathrooms"]]
            y = df["Price"]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            self.model.fit(X_train, y_train)
            score = self.model.score(X_test, y_test)

            if "trained" in self.callbacks:
                self.callbacks["trained"](score, self.model)

        except Exception as e:
            if "error" in self.callbacks:
                self.callbacks["error"](str(e))


# ---------------------- MAIN APP ----------------------
class HousePriceApp:
    APP_NAME = "HousePrice Sentinel"
    APP_VERSION = "1.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1100, 650)

        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except:
            pass

        self.model = None
        self._build_ui()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(
            main,
            text="🏠 HousePrice Sentinel",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(0, 4))

        tb.Label(
            main,
            text="AI-Powered Real Estate Price Prediction",
            font=("Segoe UI", 10, "italic"),
            foreground="#9ca3af"
        ).pack(pady=(0, 20))

        # Dataset row
        row1 = tb.Frame(main)
        row1.pack(fill=X, pady=6)

        self.dataset_entry = tb.Entry(row1, width=90)
        self.dataset_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 6))
        self.dataset_entry.insert(0, "Load CSV dataset (Area, Bedrooms, Bathrooms, Price)")

        tb.Button(
            row1,
            text="📂 Load Dataset",
            bootstyle=INFO,
            command=self.load_dataset
        ).pack(side=LEFT, padx=3)

        tb.Button(
            row1,
            text="🧠 Train Model",
            bootstyle=SUCCESS,
            command=self.train_model
        ).pack(side=LEFT, padx=3)

        # Stats
        self.stats_label = tb.Label(
            main,
            text="Model Status: Not trained",
            font=("Segoe UI", 10)
        )
        self.stats_label.pack(anchor=W, pady=(10, 10))

        # Prediction inputs
        form = tb.Labelframe(main, text="Price Prediction", padding=15)
        form.pack(fill=X, pady=10)

        self.area_var = tk.DoubleVar()
        self.bed_var = tk.IntVar()
        self.bath_var = tk.IntVar()

        tb.Label(form, text="Area (sqft)").grid(row=0, column=0, padx=5, pady=5)
        tb.Entry(form, textvariable=self.area_var).grid(row=0, column=1, padx=5)

        tb.Label(form, text="Bedrooms").grid(row=0, column=2, padx=5)
        tb.Entry(form, textvariable=self.bed_var).grid(row=0, column=3, padx=5)

        tb.Label(form, text="Bathrooms").grid(row=0, column=4, padx=5)
        tb.Entry(form, textvariable=self.bath_var).grid(row=0, column=5, padx=5)

        tb.Button(
            form,
            text="💰 Predict Price",
            bootstyle=PRIMARY,
            command=self.predict_price
        ).grid(row=0, column=6, padx=10)

        tb.Button(
            form,
            text="ℹ️ About",
            bootstyle=INFO,
            command=self.show_about
        ).grid(row=0, column=7, padx=10)
        
        self.result_label = tb.Label(
            main,
            text="Predicted Price: —",
            font=("Segoe UI", 16, "bold"),
            foreground="#4ade80"
        )
        self.result_label.pack(pady=20)

    # ---------------------- Actions ----------------------
    def load_dataset(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if path:
            self.dataset_entry.delete(0, END)
            self.dataset_entry.insert(0, path)

    def train_model(self):
        path = self.dataset_entry.get()
        if not os.path.isfile(path):
            messagebox.showerror("Error", "Invalid dataset path")
            return

        self.stats_label.config(text="Training model...")

        threading.Thread(
            target=self._train_worker,
            args=(path,),
            daemon=True
        ).start()

    def _train_worker(self, path):
        worker = PriceModelWorker(
            path,
            callbacks={
                "trained": self.on_trained,
                "error": self.on_error
            }
        )
        worker.run()

    def on_trained(self, score, model):
        self.model = model
        self.stats_label.config(
            text=f"Model trained successfully | Accuracy: {score:.2f}"
        )

    def on_error(self, msg):
        messagebox.showerror("Training Error", msg)
        self.stats_label.config(text="Training failed")

    def predict_price(self):
        if not self.model:
            messagebox.showwarning("Model", "Train the model first")
            return

        X = pd.DataFrame([{
            "Area": self.area_var.get(),
            "Bedrooms": self.bed_var.get(),
            "Bathrooms": self.bath_var.get()
        }])

        price = self.model.predict(X)[0]

        self.result_label.config(
            text=f"Predicted Price: ${price:,.2f}"
        )

    # ---------------------- About ----------------------
    def show_about(self):
        messagebox.showinfo(
            f"About {self.APP_NAME}",
            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
            "• CSV-based ML training\n"
            "• Real-time house price prediction\n"
            "• Clean enterprise UI\n"
            "• Built with Python & Scikit-Learn\n\n"
            "🏢 Mate Technologies"
        )

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = HousePriceApp()
    app.run()
