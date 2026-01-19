"""
BodyMetrics Pro v2.0 - Health Intelligence Edition
ML-Powered BMI Risk Prediction System
Age • Gender • AI Risk Scoring • Visual Analytics
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# ---------------------- ML ENGINE ----------------------
class BMIRiskModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = LogisticRegression()
        self._train()

    def _train(self):
        # Synthetic training data: [BMI, Age, Gender]
        # Gender: Male=1, Female=0
        X = np.array([
            [18, 18, 0], [22, 25, 1], [24, 30, 0],
            [27, 40, 1], [29, 45, 0], [32, 50, 1],
            [35, 55, 0], [38, 60, 1], [42, 65, 0]
        ])
        y = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])  # Risk levels

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, bmi, age, gender):
        X = np.array([[bmi, age, gender]])
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)[0]


# ---------------------- UTIL ----------------------
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)


def risk_label(code):
    return {
        0: ("Low Risk", "✅"),
        1: ("Moderate Risk", "⚠️"),
        2: ("High Risk", "❌")
    }[code]


# ---------------------- MAIN APP ----------------------
class BMIPredictorApp:
    APP_NAME = "BodyMetrics Pro"
    APP_VERSION = "2.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(720, 620)

        self.model = BMIRiskModel()

        self._build_ui()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=15)
        main.pack(fill=BOTH, expand=True)

        tb.Label(
            main,
            text=f"🧠 {self.APP_NAME}",
            font=("Segoe UI", 22, "bold")
        ).pack()

        tb.Label(
            main,
            text="ML-Based BMI Risk Prediction System",
            font=("Segoe UI", 10, "italic"),
            foreground="#9ca3af"
        ).pack(pady=(0, 20))

        # ---------------------- INPUT PANEL ----------------------
        form = tb.Labelframe(main, text="Personal Data", padding=15)
        form.pack(fill=X, pady=10)

        self.weight = tb.Entry(form, width=15)
        self.height = tb.Entry(form, width=15)
        self.age = tb.Entry(form, width=15)

        self.gender = tk.StringVar(value="Male")

        labels = ["Weight (kg)", "Height (m)", "Age"]
        entries = [self.weight, self.height, self.age]

        for i, (l, e) in enumerate(zip(labels, entries)):
            tb.Label(form, text=l).grid(row=i, column=0, sticky=W, pady=5)
            e.grid(row=i, column=1, padx=10)

        tb.Label(form, text="Gender").grid(row=3, column=0, sticky=W, pady=5)
        tb.Combobox(
            form,
            values=["Male", "Female"],
            textvariable=self.gender,
            width=13
        ).grid(row=3, column=1)

        # ---------------------- ACTIONS ----------------------
        tb.Button(
            main,
            text="🚀 Analyze Health Risk",
            bootstyle=SUCCESS,
            command=self.analyze
        ).pack(pady=10)

        self.progress = tb.Progressbar(
            main,
            bootstyle="success-striped",
            maximum=100
        )
        self.progress.pack(fill=X, pady=5)

        # ---------------------- RESULT ----------------------
        self.result = tb.Label(
            main,
            text="Awaiting input...",
            font=("Segoe UI", 14)
        )
        self.result.pack(pady=10)

        # ---------------------- CHART ----------------------
        chart_frame = tb.Labelframe(main, text="BMI Visualization", padding=10)
        chart_frame.pack(fill=BOTH, expand=True)

        self.figure = Figure(figsize=(5, 3))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    # ---------------------- LOGIC ----------------------
    def analyze(self):
        try:
            self.progress["value"] = 0
            self.root.update_idletasks()

            w = float(self.weight.get())
            h = float(self.height.get())
            age = int(self.age.get())
            gender = 1 if self.gender.get() == "Male" else 0

            if w <= 0 or h <= 0 or age <= 0:
                raise ValueError

            self.progress["value"] = 30

            bmi = calculate_bmi(w, h)
            self.progress["value"] = 60

            risk_code = self.model.predict(bmi, age, gender)
            label, icon = risk_label(risk_code)

            self.progress["value"] = 100

            self.result.config(
                text=f"{icon} BMI: {bmi} | {label}",
                font=("Segoe UI", 16, "bold")
            )

            self._update_chart(bmi)

        except Exception:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid numeric values."
            )
            self.progress["value"] = 0

    # ---------------------- CHART ----------------------
    def _update_chart(self, bmi):
        self.ax.clear()
        self.ax.bar(["Your BMI"], [bmi])
        self.ax.axhline(18.5, linestyle="--")
        self.ax.axhline(25, linestyle="--")
        self.ax.axhline(30, linestyle="--")
        self.ax.set_ylabel("BMI Value")
        self.ax.set_title("BMI Classification Zones")
        self.canvas.draw()

    # ---------------------- RUN ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = BMIPredictorApp()
    app.run()
