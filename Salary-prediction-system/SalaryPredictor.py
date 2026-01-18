"""
SalaryPredictor v2.0 - Enterprise Edition
Predict salaries from employee features using ML
Supports batch predictions with real-time per-employee preview, filtering, and live search
"""

import os, sys, threading
import pandas as pd
import joblib
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

# ---------------------- SALARY PREDICTION WORKER ----------------------
class SalaryPredictWorker:
    def __init__(self, files, model_path, callbacks):
        self.files = files
        self.model = joblib.load(model_path)
        self.callbacks = callbacks
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        total_files = len(self.files)
        feature_cols = ["Age", "Experience", "EducationLevel"]  # Only these are used by the model
        for i, path in enumerate(self.files):
            if not self._running:
                break
            try:
                df = pd.read_csv(path)
                # Select only the model features
                X = df[feature_cols]
                df['PredictedSalary'] = self.model.predict(X)

                for idx, row in df.iterrows():
                    if not self._running:
                        break
                    row_data = row.to_dict()
                    row_data['_row_id'] = idx
                    if "found" in self.callbacks:
                        self.callbacks["found"](path, row_data)

            except Exception as e:
                print(f"Error processing {path}: {e}")

            if "progress" in self.callbacks:
                self.callbacks["progress"](int((i + 1) / total_files * 100))

        if "finished" in self.callbacks:
            self.callbacks["finished"]()

# ---------------------- MAIN APP ----------------------
class SalaryPredictApp:
    APP_NAME = "SalaryPredictor"
    APP_VERSION = "2.0"

    def __init__(self):
        if DND_ENABLED:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tb.Window(themename="darkly")

        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1300, 750)

        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except: pass

        self.worker_obj = None
        self.smooth_value = 0
        self.target_progress = 0
        self.file_set = set()
        self.model_path = tk.StringVar()
        self.filter_min = tk.DoubleVar(value=0)
        self.filter_max = tk.DoubleVar(value=1e9)
        self.search_var = tk.StringVar()

        # store all rows to enable filtering/search
        self.all_rows = {}

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(main, text=f"💰 {self.APP_NAME} - Salary Prediction System",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        tb.Label(main, text="Batch salary prediction with per-employee preview, filtering, and live search",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0, 20))

        # Row 1: File Selection
        row1 = tb.Frame(main)
        row1.pack(fill=X, pady=(0,6))
        self.path_input = tb.Entry(row1, width=80)
        self.path_input.pack(side=LEFT, fill=X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop CSV files or folders here…")

        tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse).pack(side=LEFT, padx=3)
        self.start_btn = tb.Button(row1, text="🚀 Start Prediction", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=LEFT, padx=3)
        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)
        tb.Button(row1, text="💾 Export Results", bootstyle=PRIMARY, command=self.export_results).pack(side=LEFT, padx=3)
        tb.Button(row1, text="ℹ️ About", bootstyle=INFO, command=self.show_about).pack(side=LEFT, padx=3)

        # Row 2: Model selection + filters + search
        row2 = tb.Frame(main)
        row2.pack(fill=X, pady=(0,6))
        tb.Label(row2, text="ML Model Path").pack(side=LEFT, padx=3)
        self.model_input = tb.Entry(row2, width=50, textvariable=self.model_path)
        self.model_input.pack(side=LEFT, padx=3)
        tb.Button(row2, text="Browse", bootstyle=INFO, command=self.browse_model).pack(side=LEFT, padx=3)

        # Salary filters
        tb.Label(row2, text="Min Salary").pack(side=LEFT, padx=3)
        tb.Entry(row2, width=10, textvariable=self.filter_min).pack(side=LEFT, padx=3)
        tb.Label(row2, text="Max Salary").pack(side=LEFT, padx=3)
        tb.Entry(row2, width=10, textvariable=self.filter_max).pack(side=LEFT, padx=3)
        tb.Label(row2, text="Search Employee").pack(side=LEFT, padx=3)
        search_entry = tb.Entry(row2, width=20, textvariable=self.search_var)
        search_entry.pack(side=LEFT, padx=3)
        self.search_var.trace_add("write", lambda *args: self.apply_filters())

        # Progress bar
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=X, pady=(0,6))

        # Treeview for per-employee predictions
        columns = ("selected", "filename", "employee_name", "predicted_salary")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=25)
        self.tree.heading("selected", text="✅")
        self.tree.heading("filename", text="Filename", anchor=W)
        self.tree.heading("employee_name", text="Employee", anchor=W)
        self.tree.heading("predicted_salary", text="Predicted Salary", anchor=W)
        self.tree.column("selected", width=50, anchor=CENTER)
        self.tree.column("filename", width=400)
        self.tree.column("employee_name", width=250)
        self.tree.column("predicted_salary", width=150)
        self.tree.pack(fill=BOTH, expand=True, pady=(0,6))

        self.stats_label = tb.Label(main, text="EMPLOYEES PROCESSED: 0")
        self.stats_label.pack(anchor=E)

        self.root.after(15, self.animate_progress)

        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---------------------- Browse / DnD ----------------------
    def browse(self):
        folder = filedialog.askdirectory(title="Select Folder with CSV files")
        if folder:
            self.start_btn.config(state=DISABLED)
            self.cancel_btn.config(state=NORMAL)
            threading.Thread(target=self._scan_and_queue_files_thread, args=([folder],), daemon=True).start()

    def browse_model(self):
        path = filedialog.askopenfilename(title="Select ML Model", filetypes=[("Joblib Files","*.joblib")])
        if path:
            self.model_path.set(path)

    def on_drop(self, event):
        dropped_paths = self.root.tk.splitlist(event.data)
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        threading.Thread(target=self._scan_and_queue_files_thread, args=(dropped_paths,), daemon=True).start()

    def _scan_and_queue_files_thread(self, paths):
        all_files = []
        for p in paths:
            if os.path.isdir(p):
                for root_dir, _, fs in os.walk(p):
                    for name in fs:
                        all_files.append(os.path.join(root_dir, name))
            elif os.path.isfile(p):
                all_files.append(p)
        self._insert_files_chunked(all_files)

    def _insert_files_chunked(self, paths, chunk_size=500):
        if not paths:
            self.start_btn.config(state=NORMAL)
            self.cancel_btn.config(state=DISABLED)
            self.path_input.delete(0, END)
            self.path_input.insert(0, f"{len(self.file_set)} files queued")
            return
        chunk = paths[:chunk_size]
        remaining = paths[chunk_size:]
        for path in chunk:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".csv":
                if path not in self.file_set:
                    self.file_set.add(path)
                    self.tree.insert("", END, iid=f"{path}_placeholder",
                                     values=("☑️", path, "-", "-"))
        self.root.after(1, lambda: self._insert_files_chunked(remaining, chunk_size))

    # ---------------------- Actions ----------------------
    def start(self):
        if not self.model_path.get():
            messagebox.showwarning("No Model", "Please select an ML model before starting.")
            return
        selected_files = [self.tree.item(i)['values'][1] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("No Selection", "Select CSV files using the checkboxes before predicting.")
            return
        self.progress["value"] = 0
        self.smooth_value = 0
        self.target_progress = 0
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        self.all_rows = {}
        self.tree.delete(*self.tree.get_children())
        threading.Thread(target=self._run_worker, args=(selected_files,), daemon=True).start()

    def _run_worker(self, files):
        self.worker_obj = SalaryPredictWorker(
            files,
            self.model_path.get(),
            callbacks={
                "found": self.add_result,
                "progress": self.set_target,
                "finished": self.finish
            }
        )
        self.worker_obj.run()

    def add_result(self, file, row_data):
        row_key = f"{file}_{row_data.get('_row_id',0)}"
        self.all_rows[row_key] = {
            "selected": "☑️",
            "filename": file,
            "employee_name": row_data.get('Name',''),
            "predicted_salary": row_data['PredictedSalary']
        }
        self.apply_filters()

    def apply_filters(self):
        min_salary = self.filter_min.get()
        max_salary = self.filter_max.get()
        search_text = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for key, row in self.all_rows.items():
            if min_salary <= row['predicted_salary'] <= max_salary:
                if search_text in row['employee_name'].lower():
                    self.tree.insert("", END, iid=key,
                                     values=(row['selected'], row['filename'], row['employee_name'], f"${row['predicted_salary']:,.2f}"))
        self.stats_label.config(text=f"EMPLOYEES DISPLAYED: {len(self.tree.get_children())}")

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
        selected_rows = [self.tree.item(i)['values'] for i in self.tree.get_children()
                         if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_rows:
            messagebox.showwarning("Export", "No selected rows to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                f.write("Filename,Employee,PredictedSalary\n")
                for s in selected_rows:
                    f.write(f"{s[1]},{s[2]},{s[3]}\n")
            messagebox.showinfo("Export", "Export completed")

    # ---------------------- About ----------------------
    def show_about(self):
        messagebox.showinfo(
            f"About {self.APP_NAME}",
            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
            "• Drag & drop CSV files or folders\n"
            "• Real-time per-employee salary prediction\n"
            "• Min/Max salary filtering and live employee search\n"
            "• Batch processing with smooth progress bar\n"
            "• Export results to CSV\n\n"
            "🏢 Built by Your Company\n"
            "🌐 https://yourwebsite.com"
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
    app = SalaryPredictApp()
    app.run()
