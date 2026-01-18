"""
AttritionPredictor v1.0 - Enterprise Edition
Employee Attrition Prediction GUI
Upload employee datasets, predict attrition, export results
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

# ---------------------- UTIL ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ---------------------- WORKER ----------------------
class AttritionWorker:
    def __init__(self, dataframe, callbacks):
        self.df = dataframe
        self.callbacks = callbacks
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        results = []
        for idx, row in self.df.iterrows():
            if not self._running:
                break
            # Placeholder prediction logic
            attrition_prob = min(1.0, max(0.0, 0.1 + 0.2 * row.get("Age", 30)/50))
            prediction = "Yes" if attrition_prob > 0.5 else "No"
            results.append((row.get("EmployeeID", idx), row.get("Name", "N/A"), prediction))
            if "update" in self.callbacks:
                self.callbacks["update"](idx, results[-1])
        if "finished" in self.callbacks:
            self.callbacks["finished"](results)

# ---------------------- MAIN APP ----------------------
class AttritionPredictorApp:
    APP_NAME = "AttritionPredictor"
    APP_VERSION = "1.0"

    def __init__(self):
        if DND_ENABLED:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1100, 600)

        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except: pass

        self.worker_obj = None
        self.file_path = None

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(main, text=f"🧠 {self.APP_NAME} - Enterprise Attrition Predictor",
                 font=("Segoe UI", 20, "bold")).pack(pady=(0,4))
        tb.Label(main, text="Upload employee dataset, predict attrition, export results",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0,20))

        # Row 1: File selection
        row1 = tb.Frame(main)
        row1.pack(fill=X, pady=(0,6))

        self.path_input = tb.Entry(row1, width=80)
        self.path_input.pack(side=LEFT, fill=X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop employee CSV here…")

        browse_btn = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        browse_btn.pack(side=LEFT, padx=3)

        self.start_btn = tb.Button(row1, text="🚀 Predict Attrition", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=LEFT, padx=3)

        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)

        export_btn = tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=LEFT, padx=3)

        # Row 2: Treeview for results
        columns = ("selected", "employee_id", "name", "prediction")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("selected", text="✅")
        self.tree.heading("employee_id", text="Employee ID", anchor=W)
        self.tree.heading("name", text="Name", anchor=W)
        self.tree.heading("prediction", text="Attrition", anchor=W)
        self.tree.column("selected", width=50, anchor=CENTER)
        self.tree.column("employee_id", width=150)
        self.tree.column("name", width=300)
        self.tree.column("prediction", width=120)
        self.tree.pack(fill=BOTH, expand=True, pady=(0,6))

        # Progress bar
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=X, pady=(0,6))
        self.progress_value = 0
        self.target_progress = 0
        self.root.after(15, self.animate_progress)

        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---------------------- Actions ----------------------
    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if path:
            self.path_input.delete(0, END)
            self.path_input.insert(0, path)
            self.file_path = path

    def on_drop(self, event):
        path = self.root.tk.splitlist(event.data)[0]
        if os.path.isfile(path) and path.lower().endswith(".csv"):
            self.path_input.delete(0, END)
            self.path_input.insert(0, path)
            self.file_path = path

    def start(self):
        if not self.file_path or not os.path.isfile(self.file_path):
            messagebox.showwarning("No File", "Select a valid CSV file first.")
            return
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        self.progress["value"] = 0
        self.progress_value = 0
        self.target_progress = 0
        self.tree.delete(*self.tree.get_children())

        df = pd.read_csv(self.file_path)
        self.worker_obj = AttritionWorker(df, callbacks={
            "update": self.add_row,
            "finished": self.finish
        })
        threading.Thread(target=self.worker_obj.run, daemon=True).start()

    def add_row(self, idx, data):
        self.tree.insert("", END, values=("☑️", data[0], data[1], data[2]))
        self.target_progress = int((idx+1)/len(self.worker_obj.df)*100)

    def animate_progress(self):
        if self.progress_value < self.target_progress:
            self.progress_value += 1
            self.progress["value"] = self.progress_value
        self.root.after(15, self.animate_progress)

    def cancel(self):
        if self.worker_obj:
            self.worker_obj.stop()
        self.finish()

    def finish(self, results=None):
        self.start_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        self.progress["value"] = 100

    def export_results(self):
        selected = [self.tree.item(i)['values'] for i in self.tree.get_children()
                    if self.tree.item(i)['values'][0]=="☑️"]
        if not selected:
            messagebox.showwarning("Export", "No selected rows to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if path:
            pd.DataFrame(selected, columns=["Selected","EmployeeID","Name","Attrition"]).to_csv(path,index=False)
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
    app = AttritionPredictorApp()
    app.run()
