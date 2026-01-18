"""
Titanic Survival Predictor v3.1
ML-based Survival Prediction GUI
Auto-detects columns and can auto-train on any uploaded CSV
Fully compatible with pandas 3.x (no FutureWarnings)
"""

import os, sys, threading
import pandas as pd
import numpy as np
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

from sklearn.ensemble import RandomForestClassifier

# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ---------------------- WORKER ----------------------
class PredictionWorker:
    def __init__(self, files, model, callbacks):
        self.files = files
        self.model = model
        self.callbacks = callbacks
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        total_files = len(self.files)
        for i, path in enumerate(self.files):
            if not self._running:
                break
            try:
                df = pd.read_csv(path)
                df_pre = self._preprocess(df)
                X = df_pre[['Pclass','Sex','Age','SibSp','Parch','Fare']]
                preds = self.model.predict(X)
                for idx, pred in enumerate(preds):
                    if not self._running:
                        break
                    if 'found' in self.callbacks:
                        self.callbacks['found'](path, df_pre.iloc[idx], pred)
            except Exception as e:
                print(f"Error processing {path}: {e}")
            if 'progress' in self.callbacks:
                self.callbacks['progress'](int((i+1)/total_files*100))
        if 'finished' in self.callbacks:
            self.callbacks['finished']()

    def _preprocess(self, df):
        df = df.copy()
        # Map columns
        column_map = {
            'PassengerId': ['PassengerId','passengerid','Passenger ID','pid'],
            'Name': ['Name','FullName','full_name'],
            'Pclass': ['Pclass','Class'],
            'Sex': ['Sex','Gender'],
            'Age': ['Age','age'],
            'SibSp': ['SibSp','Siblings/Spouses'],
            'Parch': ['Parch','Parents/Children'],
            'Fare': ['Fare','fare']
        }
        for key, options in column_map.items():
            for opt in options:
                if opt in df.columns:
                    df[key] = df[opt]
                    break
            if key not in df.columns:
                if key in ['Age','SibSp','Parch','Fare','Pclass']:
                    df[key] = 0
                else:
                    df[key] = ""

        df['Sex'] = df['Sex'].map({'male':0,'female':1}).fillna(0)

        # Pandas 3.x safe assignment
        for col in ['Age','Fare']:
            df[col] = df[col].fillna(df[col].median())
        for col in ['SibSp','Parch','Pclass']:
            df[col] = df[col].fillna(0)

        return df

# ---------------------- MAIN APP ----------------------
class TitanicApp:
    APP_NAME = "Titanic Survival Predictor"
    APP_VERSION = "3.1"
    SUPPORTED_EXT = (".csv",)

    def __init__(self):
        # Root window
        if DND_ENABLED:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tb.Window(themename="darkly")

        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1000, 600)

        self.worker_obj = None
        self.smooth_value = 0
        self.target_progress = 0
        self.file_set = set()

        # Load model
        self.model = self._load_or_train_model()

        self._build_ui()
        self._apply_styles()

    # ---------------------- MODEL ----------------------
    def _load_or_train_model(self):
        train_file = resource_path("train.csv")
        if os.path.exists(train_file):
            df = pd.read_csv(train_file)
            messagebox.showinfo("Model", "Loaded train.csv for model training.")
        else:
            # No train.csv → smart retrain on first uploaded CSV
            messagebox.showinfo("Model", "train.csv not found. The first CSV uploaded will be used to train the model automatically.")
            df = pd.DataFrame(columns=['Survived','Pclass','Sex','Age','SibSp','Parch','Fare'])
        df = self._preprocess(df)
        X = df[['Pclass','Sex','Age','SibSp','Parch','Fare']]
        y = df.get('Survived', pd.Series([0]*len(df)))
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        if len(df) > 0:
            model.fit(X, y)
        return model

    def _preprocess(self, df):
        df = df.copy()
        # Map columns
        column_map = {
            'PassengerId': ['PassengerId','passengerid','Passenger ID','pid'],
            'Name': ['Name','FullName','full_name'],
            'Pclass': ['Pclass','Class'],
            'Sex': ['Sex','Gender'],
            'Age': ['Age','age'],
            'SibSp': ['SibSp','Siblings/Spouses'],
            'Parch': ['Parch','Parents/Children'],
            'Fare': ['Fare','fare']
        }
        for key, options in column_map.items():
            for opt in options:
                if opt in df.columns:
                    df[key] = df[opt]
                    break
            if key not in df.columns:
                if key in ['Age','SibSp','Parch','Fare','Pclass']:
                    df[key] = 0
                else:
                    df[key] = ""

        df['Sex'] = df['Sex'].map({'male':0,'female':1}).fillna(0)

        # Pandas 3.x safe assignment
        for col in ['Age','Fare']:
            df[col] = df[col].fillna(df[col].median())
        for col in ['SibSp','Parch','Pclass']:
            df[col] = df[col].fillna(0)

        return df

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        tb.Label(main, text=f"🛳 {self.APP_NAME}",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        tb.Label(main, text="Predict Titanic Passenger Survival",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0, 20))

        # Row 1: File selection
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
        self.cancel_btn.config(state=DISABLED)

        export_btn = tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=tk.LEFT, padx=3)

        about_btn = tb.Button(row1, text="ℹ️ About", bootstyle=INFO, command=self.show_about)
        about_btn.pack(side=tk.LEFT, padx=3)

        # Progress bar
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=tk.X, pady=(0,6))

        # Treeview
        columns = ("selected","PassengerID","Name","Prediction")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("selected", text="✅")
        self.tree.heading("PassengerID", text="Passenger ID", anchor=W)
        self.tree.heading("Name", text="Name", anchor=W)
        self.tree.heading("Prediction", text="Survived", anchor=W)
        self.tree.column("selected", width=50, anchor=tk.CENTER)
        self.tree.column("PassengerID", width=80)
        self.tree.column("Name", width=400)
        self.tree.column("Prediction", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0,6))

        self.root.after(15, self.animate_progress)

        # Drag & drop
        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---------------------- Browse / Drop ----------------------
    def browse(self):
        files = filedialog.askopenfilenames(title="Select CSV Files", filetypes=[("CSV Files","*.csv")])
        if files:
            self._process_uploaded_files(files)

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self._process_uploaded_files(files)

    def _process_uploaded_files(self, files):
        for f in files:
            if f.lower().endswith(".csv") and f not in self.file_set:
                self.file_set.add(f)
                self.tree.insert("", tk.END, values=("☑️", "", os.path.basename(f), "Queued"))
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.path_input.delete(0, tk.END)
        self.path_input.insert(0, f"{len(self.file_set)} files queued")

        # Smart retrain if model has no training
        if hasattr(self.model, 'estimators_') == False:
            messagebox.showinfo("Smart Retrain", f"Training model using first uploaded CSV: {files[0]}")
            df = pd.read_csv(files[0])
            df = self._preprocess(df)
            X = df[['Pclass','Sex','Age','SibSp','Parch','Fare']]
            y = df.get('Survived', pd.Series([0]*len(df)))
            self.model.fit(X, y)

    # ---------------------- Actions ----------------------
    def start(self):
        selected_files = [self.tree.item(i)['values'][2] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("No Selection", "Select CSV files before prediction.")
            return
        self.progress["value"] = 0
        self.smooth_value = 0
        self.target_progress = 0
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)

        files_to_process = [f for f in self.file_set if os.path.basename(f) in selected_files]
        self.worker_obj = PredictionWorker(files_to_process, self.model, {
            "found": self.add_result,
            "progress": self.set_target,
            "finished": self.finish
        })
        threading.Thread(target=self.worker_obj.run, daemon=True).start()

    def add_result(self, file, row, pred):
        pid = row.get('PassengerId','')
        name = row.get('Name','')
        survived = "Yes" if pred==1 else "No"
        self.tree.insert("", tk.END, values=("☑️", pid, name, survived))

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
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress["value"] = 100

    # ---------------------- Export ----------------------
    def export_results(self):
        selected = [self.tree.item(i)['values'] for i in self.tree.get_children()
                    if self.tree.item(i)['values'][0]=="☑️"]
        if not selected:
            messagebox.showwarning("Export", "No selected rows to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if path:
            df = pd.DataFrame(selected, columns=["Selected","PassengerID","Name","Survived"])
            df.to_csv(path,index=False)
            messagebox.showinfo("Export", f"Exported {len(df)} rows to {path}")

    # ---------------------- About ----------------------
    def show_about(self):
        messagebox.showinfo(
            f"About {self.APP_NAME}",
            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
            "• Drag & drop CSV files\n"
            "• Auto-detect columns in any Titanic CSV\n"
            "• Smart auto-train model if train.csv is missing\n"
            "• Multi-file threaded prediction\n"
            "• Export prediction results to CSV\n\n"
            "🏢 Built for Learning Purposes"
        )

    # ---------------------- Styles ----------------------
    def _apply_styles(self):
        self.root.style = tb.Style(theme="darkly")
        self.root.style.configure("TProgressbar", troughcolor="#1b1f3a", background="#7c3aed", thickness=14)

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = TitanicApp()
    app.run()
