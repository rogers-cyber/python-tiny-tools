"""
InsurePredict v1.0 - Enterprise Edition
Insurance Cost Prediction & Analysis Tool
AI-driven cost predictions with smooth GUI
"""

import os, sys, threading
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

import pandas as pd
from sklearn.linear_model import LinearRegression

# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ---------------------- PREDICTION WORKER ----------------------
class PredictionWorker:
    def __init__(self, files, callbacks):
        self.files = files
        self.callbacks = callbacks
        self._running = True
        # Dummy regression model (for demonstration)
        self.model = LinearRegression()
        # Example training on synthetic data
        self.model.fit([[18,0],[25,1],[40,1],[60,0]], [2000,3000,4000,3500])

    def stop(self):
        self._running = False

    def run(self):
        results = []
        total_files = len(self.files)
        for i, file in enumerate(self.files):
            if not self._running:
                break
            try:
                df = pd.read_csv(file)
                # Expected columns: ["age", "smoker"] for simplicity
                if "age" in df.columns and "smoker" in df.columns:
                    pred = self.model.predict(df[["age","smoker"]])
                    results.append((file, pred.tolist()))
                else:
                    results.append((file, "Missing required columns"))
            except Exception as e:
                results.append((file, f"Error: {e}"))

            # Update progress
            if "progress" in self.callbacks:
                self.callbacks["progress"](int((i+1)/total_files*100))
            if "found" in self.callbacks:
                self.callbacks["found"](file, results[-1][1])

        if "finished" in self.callbacks:
            self.callbacks["finished"]()

# ---------------------- MAIN APP ----------------------
class InsurePredictApp:
    APP_NAME = "InsurePredict"
    APP_VERSION = "1.0"
    SUPPORTED_EXT = (".csv",)

    def __init__(self):
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

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(main, text=f"💰 {self.APP_NAME} - Insurance Cost Predictor",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0,4))

        tb.Label(main, text="Predict insurance cost from CSV data",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0,20))

        # Row 1: File Selection
        row1 = tb.Frame(main)
        row1.pack(fill=X, pady=(0,6))

        self.path_input = tb.Entry(row1, width=80)
        self.path_input.pack(side=LEFT, fill=X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop CSV files here…")

        browse_btn = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        browse_btn.pack(side=LEFT, padx=3)

        self.start_btn = tb.Button(row1, text="🚀 Predict", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=LEFT, padx=3)

        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)

        export_btn = tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=LEFT, padx=3)

        about_btn = tb.Button(row1, text="ℹ️ About", bootstyle=INFO, command=self.show_about)
        about_btn.pack(side=LEFT, padx=3)

        # Progress
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=X, pady=(0,6))

        # Treeview
        columns = ("selected","filename","prediction")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("selected", text="✅")
        self.tree.heading("filename", text="Filename", anchor=W)
        self.tree.heading("prediction", text="Prediction", anchor=W)
        self.tree.column("selected", width=50, anchor=CENTER)
        self.tree.column("filename", width=600)
        self.tree.column("prediction", width=300)
        self.tree.pack(fill=BOTH, expand=True, pady=(0,6))

        # Timer
        self.root.after(15, self.animate_progress)

        # Bind DnD if enabled
        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---------------------- File Handling ----------------------
    def browse(self):
        files = filedialog.askopenfilenames(title="Select CSV Files", filetypes=[("CSV Files","*.csv")])
        if files:
            self._insert_files_chunked(files)

    def on_drop(self, event):
        dropped_paths = self.root.tk.splitlist(event.data)
        self._insert_files_chunked(dropped_paths)

    def _insert_files_chunked(self, paths, chunk_size=500):
        if not paths:
            return
        chunk = paths[:chunk_size]
        remaining = paths[chunk_size:]
        for path in chunk:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".csv" and path not in self.file_set:
                self.file_set.add(path)
                self.tree.insert("", END, values=("☑️", path, "Queued"))
        self.root.after(1, lambda: self._insert_files_chunked(remaining, chunk_size))

    # ---------------------- Actions ----------------------
    def start(self):
        selected_files = [self.tree.item(i)['values'][1] for i in self.tree.get_children() if self.tree.item(i)['values'][0]=="☑️"]
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
        self.worker_obj = PredictionWorker(files, callbacks={
            "found": self.add_prediction,
            "progress": self.set_target,
            "finished": self.finish
        })
        self.worker_obj.run()

    def add_prediction(self, file, prediction):
        for i in self.tree.get_children():
            if self.tree.item(i)['values'][1] == file:
                self.tree.item(i, values=("☑️", file, str(prediction)))
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

    # ---------------------- Export ----------------------
    def export_results(self):
        selected_files = [self.tree.item(i)['values'] for i in self.tree.get_children() if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("Export", "No results to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                for s in selected_files:
                    f.write(f"{s[1]} | {s[2]}\n")
            messagebox.showinfo("Export", "Export completed")

    # ---------------------- About ----------------------
    def show_about(self):
        messagebox.showinfo(f"About {self.APP_NAME}",
            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
            "• Predict insurance cost from CSV files\n"
            "• Drag & drop support\n"
            "• Multi-file batch predictions\n"
            "• Export results to text\n\n"
            "🏢 Built by Mate Technologies\n"
            "🌐 https://matetools.gumroad.com"
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
    app = InsurePredictApp()
    app.run()
