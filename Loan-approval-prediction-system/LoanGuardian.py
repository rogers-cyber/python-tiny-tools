"""
LoanGuardian v2.1 - Enterprise Edition
AI-Powered Loan Approval Prediction System
Handles large CSV datasets efficiently with auto feature detection, normalization, and fixed categorical encoding
"""

import os, sys, threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np

import ttkbootstrap as tb
from ttkbootstrap.constants import *

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_ENABLED = True
except ImportError:
    DND_ENABLED = False
    print("Drag & Drop requires tkinterdnd2: pip install tkinterdnd2")

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ---------------------- PREDICTION WORKER ----------------------
class LoanWorker:
    def __init__(self, files, callbacks, chunk_size=500):
        self.files = files
        self.callbacks = callbacks
        self._running = True
        self.chunk_size = chunk_size
        self.encoders = {}  # Store encoders for categorical columns
        self.model, self.feature_info = self._train_model()

    def stop(self):
        self._running = False

    def _train_model(self):
        # Dummy training dataset
        data = pd.DataFrame({
            "Gender": ["Male","Female","Female","Male","Male","Female"],
            "Married": ["Yes","No","Yes","Yes","No","No"],
            "Education": ["Graduate","Graduate","Not Graduate","Graduate","Not Graduate","Graduate"],
            "ApplicantIncome": [5000,3000,4000,6000,3500,4200],
            "LoanAmount": [200,100,150,250,120,140],
            "Loan_Approved": ["Yes","No","Yes","Yes","No","Yes"]
        })
        X = data.drop("Loan_Approved", axis=1)
        y = data["Loan_Approved"]

        feature_info = {"categorical": [], "numeric": []}
        for col in X.columns:
            if X[col].dtype == object:
                feature_info["categorical"].append(col)
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col])
                self.encoders[col] = le
            else:
                feature_info["numeric"].append(col)

        scaler = MinMaxScaler()
        if feature_info["numeric"]:
            X[feature_info["numeric"]] = scaler.fit_transform(X[feature_info["numeric"]])

        le_y = LabelEncoder()
        y_encoded = le_y.fit_transform(y)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y_encoded)

        return model, {
            "categorical": feature_info["categorical"],
            "numeric": feature_info["numeric"],
            "le_y": le_y,
            "scaler": scaler
        }

    def _preprocess_chunk(self, df):
        fi = self.feature_info
        # Encode categorical using stored encoders
        for col in fi["categorical"]:
            if col in df.columns:
                le = self.encoders[col]
                df[col] = df[col].astype(str)
                # Map unseen categories to -1
                df[col] = df[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
        # Normalize numeric columns
        if fi["numeric"]:
            for col in fi["numeric"]:
                if col in df.columns:
                    df[col] = df[col] / (df[col].max() + 1e-5)
        return df

    def run(self):
        total_files = len(self.files)
        for i, path in enumerate(self.files):
            if not self._running:
                break
            try:
                for chunk in pd.read_csv(path, chunksize=self.chunk_size):
                    if not self._running:
                        break
                    original_chunk = chunk.copy()
                    chunk_processed = self._preprocess_chunk(chunk)
                    missing_cols = set(self.feature_info["categorical"] + self.feature_info["numeric"]) - set(chunk_processed.columns)
                    for col in missing_cols:
                        chunk_processed[col] = 0
                    preds = self.model.predict(chunk_processed[self.feature_info["categorical"] + self.feature_info["numeric"]])
                    chunk["Approval_Prediction"] = self.feature_info["le_y"].inverse_transform(preds)
                    if "found" in self.callbacks:
                        self.callbacks["found"](path, original_chunk, chunk)
            except Exception as e:
                if "error" in self.callbacks:
                    self.callbacks["error"](path, str(e))
            if "progress" in self.callbacks:
                self.callbacks["progress"](int((i + 1)/total_files * 100))
        if "finished" in self.callbacks:
            self.callbacks["finished"]()

# ---------------------- MAIN APP ----------------------
class LoanGuardianApp:
    APP_NAME = "LoanGuardian"
    APP_VERSION = "2.1"
    SUPPORTED_EXT = (".csv",)

    def __init__(self):
        if DND_ENABLED:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1000, 600)

        self.worker_obj = None
        self.progress_value = 0
        self.target_progress = 0
        self.file_set = set()
        self._build_ui()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        tb.Label(main, text=f"🧠 {self.APP_NAME} - Enterprise Loan Predictor",
                 font=("Segoe UI", 20, "bold")).pack(pady=(0,10))
        tb.Label(main, text="Auto-detect features, normalize numeric columns, process thousands of files",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0,10))

        row1 = tb.Frame(main)
        row1.pack(fill=tk.X, pady=(0,6))
        self.path_input = tb.Entry(row1, width=80)
        self.path_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop CSV files here…")
        browse_btn = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        browse_btn.pack(side=tk.LEFT, padx=3)
        self.start_btn = tb.Button(row1, text="🚀 Start Prediction", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=3)
        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=tk.LEFT, padx=3)
        self.cancel_btn.config(state=tk.DISABLED)
        export_btn = tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=tk.LEFT, padx=3)

        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=tk.X, pady=(0,6))

        columns = ("selected","filename","status")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("selected", text="✅")
        self.tree.heading("filename", text="Filename", anchor=tk.W)
        self.tree.heading("status", text="Status", anchor=tk.W)
        self.tree.column("selected", width=50, anchor=tk.CENTER)
        self.tree.column("filename", width=600)
        self.tree.column("status", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0,6))
        self.root.after(15, self.animate_progress)

        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---------------------- File Handling ----------------------
    def browse(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV Files","*.csv")])
        if files:
            self._queue_files(files)

    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        self._queue_files(paths)

    def _queue_files(self, paths):
        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext in self.SUPPORTED_EXT and path not in self.file_set:
                self.file_set.add(path)
                self.tree.insert("", tk.END, values=("☑️", path, "Queued"))

    # ---------------------- Actions ----------------------
    def start(self):
        selected_files = [self.tree.item(i)['values'][1] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("No Selection", "Select CSV files before starting prediction.")
            return
        self.progress["value"] = 0
        self.target_progress = 0
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        threading.Thread(target=self._run_worker, args=(selected_files,), daemon=True).start()

    def _run_worker(self, files):
        self.worker_obj = LoanWorker(
            files,
            callbacks={
                "found": self.add_result,
                "error": self.add_error,
                "progress": self.set_target,
                "finished": self.finish
            }
        )
        self.worker_obj.run()

    def add_result(self, file, original_df, result_df):
        for i in self.tree.get_children():
            if self.tree.item(i)['values'][1]==file:
                self.tree.item(i, values=("☑️", file, "Predicted"))
                break

    def add_error(self, file, error_msg):
        for i in self.tree.get_children():
            if self.tree.item(i)['values'][1]==file:
                self.tree.item(i, values=("☑️", file, f"Error: {error_msg}"))
                break

    def set_target(self, v):
        self.target_progress = v

    def animate_progress(self):
        if self.progress_value < self.target_progress:
            self.progress_value += 1
            self.progress["value"] = self.progress_value
        self.root.after(15, self.animate_progress)

    def cancel(self):
        if self.worker_obj:
            self.worker_obj.stop()
        self.finish()

    def finish(self):
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress["value"] = 100

    # ---------------------- Export ----------------------
    def export_results(self):
        selected_files = [self.tree.item(i)['values'] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("Export", "No files to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                for s in selected_files:
                    f.write(f"{s[1]} | {s[2]}\n")
            messagebox.showinfo("Export", "Export completed")

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = LoanGuardianApp()
    app.run()
