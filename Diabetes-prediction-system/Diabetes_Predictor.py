"""
Diabetes Predictor v2.0 - Professional Edition
AI-Powered Diabetes Risk Prediction System
Supports single entries & CSV batch predictions with polished GUI
"""

import os, sys, threading
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import ttkbootstrap as tb
from ttkbootstrap.constants import *

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_ENABLED = True
except ImportError:
    DND_ENABLED = False
    print("Drag & Drop requires tkinterdnd2: pip install tkinterdnd2")


# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


# ---------------------- PREDICTION WORKER ----------------------
class PredictionWorker:
    def __init__(self, data_files, callbacks):
        self.data_files = data_files
        self.callbacks = callbacks
        self._running = True
        self.model = None
        self._train_model()

    def _train_model(self):
        try:
            df = pd.read_csv("diabetes.csv")
            X = df.drop("Outcome", axis=1)
            y = df["Outcome"]
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X, y)
        except Exception as e:
            print(f"Training error: {e}")
            self.model = None

    def stop(self):
        self._running = False

    def run(self):
        results = []
        total_files = len(self.data_files)
        for i, path in enumerate(self.data_files):
            if not self._running:
                break
            try:
                df = pd.read_csv(path)
                if self.model is not None:
                    pred = self.model.predict(df)
                    for j, p in enumerate(pred):
                        results.append((path, j + 1, p))
                        if "found" in self.callbacks:
                            self.callbacks["found"](path, j + 1, p)
            except Exception as e:
                results.append((path, 0, f"Error: {e}"))
            if "progress" in self.callbacks:
                self.callbacks["progress"](int((i + 1) / total_files * 100))
        if "finished" in self.callbacks:
            self.callbacks["finished"]()


# ---------------------- MAIN APP ----------------------
class DiabetesPredictorApp:
    APP_NAME = "Diabetes Predictor"
    APP_VERSION = "2.0"

    def __init__(self):
        if DND_ENABLED:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1000, 700)

        self.worker_obj = None
        self.file_set = set()
        self.smooth_value = 0
        self.target_progress = 0

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        tb.Label(main, text=f"🩺 {self.APP_NAME}", font=("Segoe UI", 22, "bold")).pack(pady=(0,4))
        tb.Label(main, text="AI-Powered Diabetes Risk Prediction", font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0,20))

        # ------------------ Tabs ------------------
        self.tabs = tb.Notebook(main)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Batch Prediction Tab
        self.batch_tab = tb.Frame(self.tabs)
        self.tabs.add(self.batch_tab, text="📂 Batch CSV Prediction")

        self._build_batch_tab()

        # Single Entry Prediction Tab
        self.single_tab = tb.Frame(self.tabs)
        self.tabs.add(self.single_tab, text="📝 Single Entry Prediction")

        self._build_single_tab()

    # ---------------------- Batch Tab ----------------------
    def _build_batch_tab(self):
        row1 = tb.Frame(self.batch_tab)
        row1.pack(fill=tk.X, pady=(0,6))

        self.path_input = tb.Entry(row1, width=70)
        self.path_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop CSV files here…")

        browse_btn = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        browse_btn.pack(side=tk.LEFT, padx=3)

        self.start_btn = tb.Button(row1, text="🚀 Predict", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=3)

        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=tk.LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)

        export_btn = tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=tk.LEFT, padx=3)

        # Progress
        self.progress = tb.Progressbar(self.batch_tab, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=tk.X, pady=(0,6))

        # Treeview for results
        columns = ("selected", "file", "entry", "prediction")
        self.tree = ttk.Treeview(self.batch_tab, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("selected", text="✅")
        self.tree.heading("file", text="File")
        self.tree.heading("entry", text="Entry #")
        self.tree.heading("prediction", text="Predicted Outcome")
        self.tree.column("selected", width=50, anchor=tk.CENTER)
        self.tree.column("file", width=350)
        self.tree.column("entry", width=80, anchor=tk.CENTER)
        self.tree.column("prediction", width=150, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0,6))

        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

        self.root.after(15, self.animate_progress)

    # ---------------------- Single Entry Tab ----------------------
    def _build_single_tab(self):
        tb.Label(self.single_tab, text="Enter Patient Data:", font=("Segoe UI", 14, "bold")).pack(pady=(0,10))

        form_frame = tb.Frame(self.single_tab)
        form_frame.pack(pady=10)

        # Features used in Pima dataset
        self.single_inputs = {}
        features = ["Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age"]
        for i, feature in enumerate(features):
            row = tb.Frame(form_frame)
            row.pack(fill=tk.X, pady=2)
            tb.Label(row, text=f"{feature}:", width=25, anchor="w").pack(side=tk.LEFT)
            entry = tb.Entry(row, width=20)
            entry.pack(side=tk.LEFT)
            self.single_inputs[feature] = entry

        tb.Button(self.single_tab, text="🩺 Predict Single Entry", bootstyle=SUCCESS, command=self.predict_single).pack(pady=10)
        self.single_result = tb.Label(self.single_tab, text="", font=("Segoe UI", 12, "bold"))
        self.single_result.pack(pady=10)

    # ---------------------- File Handling ----------------------
    def browse(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV Files","*.csv")])
        if files:
            self._queue_files(files)

    def on_drop(self, event):
        dropped_paths = self.root.tk.splitlist(event.data)
        self._queue_files(dropped_paths)

    def _queue_files(self, files):
        for f in files:
            if f not in self.file_set:
                self.file_set.add(f)
                self.tree.insert("", tk.END, values=("☑️", f, "-", "-"))

    # ---------------------- Actions ----------------------
    def start(self):
        selected_files = [self.tree.item(i)['values'][1] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("No Selection", "Select CSV files before predicting.")
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
            callbacks={
                "found": self.add_prediction,
                "progress": self.set_target,
                "finished": self.finish
            }
        )
        self.worker_obj.run()

    def add_prediction(self, file, entry, prediction):
        for i in self.tree.get_children():
            if self.tree.item(i)['values'][1] == file and self.tree.item(i)['values'][2] == "-":
                self.tree.item(i, values=("☑️", file, entry, prediction))
                break

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

    # ---------------------- Single Entry Prediction ----------------------
    def predict_single(self):
        try:
            values = [float(self.single_inputs[f].get()) for f in self.single_inputs]
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for all fields.")
            return

        try:
            df = pd.read_csv("diabetes.csv")
            X = df.drop("Outcome", axis=1)
            y = df["Outcome"]
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            pred = model.predict([values])[0]
            self.single_result.config(text=f"Predicted Outcome: {'Diabetic' if pred==1 else 'Non-Diabetic'}", foreground="#4ade80" if pred==0 else "#f87171")
        except Exception as e:
            messagebox.showerror("Prediction Error", str(e))

    # ---------------------- Export ----------------------
    def export_results(self):
        selected = [self.tree.item(i)['values'] for i in self.tree.get_children() if self.tree.item(i)['values'][0]=="☑️"]
        if not selected:
            messagebox.showwarning("Export", "No results to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if path:
            import csv
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["File","Entry #","Predicted Outcome"])
                for row in selected:
                    writer.writerow(row[1:])
            messagebox.showinfo("Export", "Results exported successfully!")

    # ---------------------- About ----------------------
    def show_about(self):
        messagebox.showinfo(f"About {self.APP_NAME}",
                            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
                            "• Batch prediction of diabetes risk from CSV files\n"
                            "• Single patient entry prediction\n"
                            "• Drag & drop files or browse\n"
                            "• Real-time updates for batch predictions\n"
                            "• Export results to CSV\n\n"
                            "🏢 Built professionally with Tkinter & AI")

    # ---------------------- Styles ----------------------
    def _apply_styles(self):
        self.root.style = tb.Style(theme="darkly")
        self.root.style.configure("TProgressbar", troughcolor="#1b1f3a", background="#7c3aed", thickness=14)

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = DiabetesPredictorApp()
    app.run()
