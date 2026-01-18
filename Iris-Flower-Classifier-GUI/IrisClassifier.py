"""
IrisClassifier v1.1 - Interactive GUI
Classify Iris species using a trained scikit-learn model
Drag & drop CSV files, browse CSVs, or enter measurements manually
"""

import os, sys, threading
import pandas as pd
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

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ---------------------- MODEL ----------------------
class IrisModel:
    def __init__(self):
        data = load_iris()
        self.X = data.data
        self.y = data.target
        self.target_names = data.target_names
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(self.X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, self.y, test_size=0.2, random_state=42)
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.clf.fit(X_train, y_train)

    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        preds = self.clf.predict(X_scaled)
        return [self.target_names[p] for p in preds]

# ---------------------- WORKER ----------------------
class ClassifierWorker:
    def __init__(self, files, callbacks):
        self.files = files
        self.callbacks = callbacks
        self._running = True
        self.model = IrisModel()

    def stop(self):
        self._running = False

    def run(self):
        total = len(self.files)
        for i, file in enumerate(self.files):
            if not self._running:
                break
            try:
                df = pd.read_csv(file)
                # Expect columns: sepal_length,sepal_width,petal_length,petal_width
                if set(df.columns) >= {"sepal_length","sepal_width","petal_length","petal_width"}:
                    X = df[["sepal_length","sepal_width","petal_length","petal_width"]].values
                    preds = self.model.predict(X)
                    if "found" in self.callbacks:
                        self.callbacks["found"](file, preds)
            except Exception as e:
                if "found" in self.callbacks:
                    self.callbacks["found"](file, [f"Error: {str(e)}"])
            if "progress" in self.callbacks:
                self.callbacks["progress"](int((i+1)/total*100))
        if "finished" in self.callbacks:
            self.callbacks["finished"]()

# ---------------------- MAIN APP ----------------------
class IrisClassifierApp:
    APP_NAME = "IrisClassifier"
    APP_VERSION = "1.1"

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
        self.model = IrisModel()

        self._build_ui()
        self._apply_styles()
        self.root.after(15, self.animate_progress)

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(main, text=f"🌸 {self.APP_NAME} - Iris Flower Classifier",
                 font=("Segoe UI", 20, "bold")).pack(pady=(0,10))
        tb.Label(main, text="Classify Iris species from CSV files or manual input",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0,15))

        # Row 1: File selection
        row1 = tb.Frame(main)
        row1.pack(fill=X, pady=(0,6))

        self.path_input = tb.Entry(row1, width=80)
        self.path_input.pack(side=LEFT, fill=X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop CSV files here…")

        browse_btn = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        browse_btn.pack(side=LEFT, padx=3)

        self.start_btn = tb.Button(row1, text="🚀 Classify CSV", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=LEFT, padx=3)

        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)

        export_btn = tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=LEFT, padx=3)

        # Progress bar
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=X, pady=(0,6))

        # Treeview for CSV results
        columns = ("selected","filename","prediction")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=15)
        self.tree.heading("selected", text="✅")
        self.tree.heading("filename", text="Filename", anchor=W)
        self.tree.heading("prediction", text="Prediction", anchor=W)
        self.tree.column("selected", width=50, anchor=CENTER)
        self.tree.column("filename", width=600)
        self.tree.column("prediction", width=200)
        self.tree.pack(fill=BOTH, expand=True, pady=(0,6))

        # Manual input frame
        manual_frame = tb.Labelframe(main, text="Manual Input", padding=10)
        manual_frame.pack(fill=X, pady=(10,6))

        self.manual_entries = {}
        labels = ["Sepal Length","Sepal Width","Petal Length","Petal Width"]
        default_vals = [5.1, 3.5, 1.4, 0.2]
        for i, (label, val) in enumerate(zip(labels, default_vals)):
            tb.Label(manual_frame, text=label).grid(row=0, column=i*2, sticky=W, padx=(0,2))
            entry = tb.Entry(manual_frame, width=8)
            entry.grid(row=0, column=i*2+1, sticky=W, padx=(0,6))
            entry.insert(0, str(val))
            self.manual_entries[label] = entry

        predict_btn = tb.Button(manual_frame, text="🔮 Predict", bootstyle=INFO, command=self.manual_predict)
        predict_btn.grid(row=0, column=8, padx=10)

        self.manual_result = tb.Label(manual_frame, text="Prediction: ---", font=("Segoe UI", 12, "bold"))
        self.manual_result.grid(row=1, column=0, columnspan=9, pady=(6,0), sticky=W)

        # Drag & Drop
        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---------------------- Browse / DnD ----------------------
    def browse(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV Files","*.csv")])
        if files:
            threading.Thread(target=self._queue_files_thread, args=(files,), daemon=True).start()

    def on_drop(self, event):
        dropped_paths = self.root.tk.splitlist(event.data)
        threading.Thread(target=self._queue_files_thread, args=(dropped_paths,), daemon=True).start()

    def _queue_files_thread(self, paths):
        for path in paths:
            if path not in self.file_set and os.path.isfile(path) and path.endswith(".csv"):
                self.file_set.add(path)
                self.tree.insert("", END, values=("☑️", path, "Queued"))

    # ---------------------- Actions ----------------------
    def start(self):
        selected_files = [self.tree.item(i)['values'][1] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("No files selected", "Select CSV files using the checkboxes first")
            return
        self.progress["value"] = 0
        self.smooth_value = 0
        self.target_progress = 0
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        self.worker_obj = ClassifierWorker(selected_files, callbacks={
            "found": self.add_prediction,
            "progress": self.set_target,
            "finished": self.finish
        })
        threading.Thread(target=self.worker_obj.run, daemon=True).start()

    def add_prediction(self, file, preds):
        for i in self.tree.get_children():
            if self.tree.item(i)['values'][1]==file:
                self.tree.item(i, values=("☑️", file, ", ".join(map(str,preds))))
                break

    def manual_predict(self):
        try:
            values = [float(self.manual_entries[label].get()) for label in self.manual_entries]
            pred = self.model.predict([values])[0]
            self.manual_result.config(text=f"Prediction: {pred}", foreground="#10b981")
        except Exception as e:
            self.manual_result.config(text=f"Error: {str(e)}", foreground="#f87171")

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
        selected = [self.tree.item(i)['values'] for i in self.tree.get_children()
                    if self.tree.item(i)['values'][0]=="☑️"]
        if not selected:
            messagebox.showwarning("Export", "No selected files to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                for s in selected:
                    f.write(f"{s[1]} | {s[2]}\n")
            messagebox.showinfo("Export", "Export completed")

    # ---------------------- Styles ----------------------
    def _apply_styles(self):
        self.root.style = tb.Style(theme="darkly")
        self.root.style.configure("TProgressbar", troughcolor="#1b1f3a", background="#7c3aed", thickness=14)

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = IrisClassifierApp()
    app.run()
