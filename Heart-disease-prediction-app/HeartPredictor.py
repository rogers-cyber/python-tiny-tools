"""
HeartPredictor v2.0 - Health Intelligence Tool
Predicts risk of heart disease from patient data using a logistic regression model
Supports batch CSV input with smooth UI and real-time results
"""

import os, sys, threading, csv, numpy as np, pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ---------------------- ML MODEL ----------------------
class HeartDiseaseModel:
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)
        self.scaler = StandardScaler()
        self.features = ["age","sex","cp","trestbps","chol","fbs","restecg",
                         "thalach","exang","oldpeak","slope","ca","thal"]
        self._train_dummy_model()

    def _train_dummy_model(self):
        """
        Creates a dummy dataset to train a simple logistic regression model.
        In practice, replace this with a real dataset.
        """
        np.random.seed(42)
        X = np.random.randint(0, 100, size=(500, len(self.features)))
        y = np.random.randint(0, 2, size=(500,))
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict_risk(self, patient_data):
        """
        patient_data: dict of feature_name -> value
        Returns: "Low", "Medium", "High"
        """
        try:
            x = np.array([float(patient_data.get(f,0)) for f in self.features]).reshape(1,-1)
            x_scaled = self.scaler.transform(x)
            prob = self.model.predict_proba(x_scaled)[0][1]  # probability of heart disease
            if prob < 0.33:
                return "Low"
            elif prob < 0.66:
                return "Medium"
            else:
                return "High"
        except Exception:
            return "Low"

# ---------------------- WORKER ----------------------
class PredictionWorker:
    def __init__(self, files, model, callbacks):
        self.files = files
        self.model = model
        self._running = True
        self.callbacks = callbacks

    def stop(self):
        self._running = False

    def run(self):
        total_files = len(self.files)
        results = []

        for i, path in enumerate(self.files):
            if not self._running:
                break
            try:
                df = pd.read_csv(path)
                for _, row in df.iterrows():
                    if not self._running:
                        break
                    patient_data = row.to_dict()
                    name = patient_data.get("name","Unknown")
                    risk = self.model.predict_risk(patient_data)
                    results.append((path, name, risk))
                    if "found" in self.callbacks:
                        self.callbacks["found"](path, name, risk)
            except Exception as e:
                print(f"Failed to process {path}: {e}")

            if total_files > 0 and "progress" in self.callbacks:
                self.callbacks["progress"](int((i + 1) / total_files * 100))

        if "finished" in self.callbacks:
            self.callbacks["finished"]()

# ---------------------- MAIN APP ----------------------
class HeartPredictorApp:
    APP_NAME = "HeartPredictor"
    APP_VERSION = "2.0"
    SUPPORTED_EXT = (".csv",)

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1000, 600)

        self.worker_obj = None
        self.model = HeartDiseaseModel()
        self.smooth_value = 0
        self.target_progress = 0
        self.file_set = set()

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(main, text=f"❤️ {self.APP_NAME} - Health Intelligence",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        tb.Label(main, text="Predict heart disease risk from patient CSV files",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0, 20))

        # Row 1: File selection
        row1 = tb.Frame(main)
        row1.pack(fill=X, pady=(0,6))

        self.path_input = tb.Entry(row1, width=80)
        self.path_input.pack(side=LEFT, fill=X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Select patient CSV files here…")

        browse_btn = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        browse_btn.pack(side=LEFT, padx=3)

        self.start_btn = tb.Button(row1, text="🚀 Start Prediction", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=LEFT, padx=3)

        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)

        export_btn = tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=LEFT, padx=3)

        # Progress
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=X, pady=(0,6))

        # Treeview
        columns = ("selected", "filename", "patient", "risk")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("selected", text="✅")
        self.tree.heading("filename", text="Filename")
        self.tree.heading("patient", text="Patient Name")
        self.tree.heading("risk", text="Predicted Risk")
        self.tree.column("selected", width=50, anchor=CENTER)
        self.tree.column("filename", width=300)
        self.tree.column("patient", width=200)
        self.tree.column("risk", width=100)
        self.tree.pack(fill=BOTH, expand=True, pady=(0,6))

        self.stats_label = tb.Label(main, text="TOTAL: 0 | LOW: 0 | MEDIUM: 0 | HIGH: 0")
        self.stats_label.pack(anchor=E)

        self.root.after(15, self.animate_progress)

    # ---------------------- Browse ----------------------
    def browse(self):
        paths = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        if paths:
            for path in paths:
                if path not in self.file_set:
                    self.file_set.add(path)
                    self.tree.insert("", END, values=("☑️", path, "-", "-"))

    # ---------------------- Actions ----------------------
    def start(self):
        selected_files = [self.tree.item(i)['values'][1] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("No Selection", "Select CSV files before prediction.")
            return
        self.progress["value"] = 0
        self.smooth_value = 0
        self.target_progress = 0
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        threading.Thread(target=self._run_worker, args=(selected_files,), daemon=True).start()

    def _run_worker(self, files):
        self.worker_obj = PredictionWorker(
            files,
            model=self.model,
            callbacks={
                "found": self.add_result,
                "progress": self.set_target,
                "finished": self.finish
            }
        )
        self.worker_obj.run()

    def add_result(self, file, patient, risk):
        for i in self.tree.get_children():
            if self.tree.item(i)['values'][1] == file:
                self.tree.item(i, values=("☑️", file, patient, risk))
                colors = {"High":"#dc2626","Medium":"#facc15","Low":"#4ade80"}
                self.tree.tag_configure(risk, foreground=colors.get(risk))
                self.tree.item(i, tags=(risk,))
                self.update_stats()
                break

    def update_stats(self):
        counts = {"Low":0,"Medium":0,"High":0,"TOTAL":0}
        for i in self.tree.get_children():
            risk = self.tree.item(i)['values'][3]
            if risk in counts:
                counts[risk] += 1
                counts["TOTAL"] += 1
        self.stats_label.config(text=f"TOTAL: {counts['TOTAL']} | LOW: {counts['Low']} | MEDIUM: {counts['Medium']} | HIGH: {counts['High']}")

    def set_target(self, v):
        self.target_progress = v

    def animate_progress(self):
        if self.smooth_value < self.target_progress:
            self.smooth_value += 1
            self.progress["value"] = self.smooth_value
        self.root.after(15, self.animate_progress)

    def cancel(self):
        if self.worker_obj:
            self.worker_obj.stop()
        self.finish()

    def finish(self):
        self.start_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        self.progress["value"] = 100

    # ---------------------- Export ----------------------
    def export_results(self):
        selected_files = [self.tree.item(i)['values'] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("Export", "No selected results to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if path:
            with open(path,"w",encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Filename","Patient Name","Predicted Risk"])
                for s in selected_files:
                    writer.writerow([s[1], s[2], s[3]])
            messagebox.showinfo("Export", "Export completed")

    # ---------------------- Styles ----------------------
    def _apply_styles(self):
        style = tb.Style(theme="darkly")  # don't assign to self.root.style
        style.configure("TProgressbar", troughcolor="#1b1f3a", background="#7c3aed", thickness=14)

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = HeartPredictorApp()
    app.run()
