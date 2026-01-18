"""
ExamResultPredictor v2.0 - Academic Performance Predictor
Predicts student exam results based on study hours, attendance, previous grades,
and historical data loaded from CSV.
"""

import os, sys, threading, csv
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# For predictive model
from sklearn.linear_model import LinearRegression
import numpy as np

# ---------------------- UTILS ----------------------
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


# ---------------------- PREDICTOR WORKER ----------------------
class PredictorWorker:
    def __init__(self, data, model, callbacks):
        self.data = data
        self.model = model
        self.callbacks = callbacks
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        results = []
        for i, student in enumerate(self.data):
            if not self._running:
                break

            # Predict grade using model
            features = np.array([[student["study_hours"],
                                  student["attendance"],
                                  student["previous_grade"]]])
            predicted_score = self.model.predict(features)[0]

            # Map score to letter grade
            grade = "A" if predicted_score >= 80 else "B" if predicted_score >= 60 else "C" if predicted_score >= 40 else "F"
            results.append({**student, "predicted_grade": grade})

            if "found" in self.callbacks:
                self.callbacks["found"](student, grade)

            if "progress" in self.callbacks:
                self.callbacks["progress"](int((i + 1) / len(self.data) * 100))

        if "finished" in self.callbacks:
            self.callbacks["finished"](results)


# ---------------------- MAIN APP ----------------------
class ExamResultPredictorApp:
    APP_NAME = "ExamResultPredictor"
    APP_VERSION = "2.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(950, 650)

        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except: pass

        self.worker_obj = None
        self.smooth_value = 0
        self.target_progress = 0
        self.student_data = []
        self.model = self._train_dummy_model()

        self._build_ui()
        self._apply_styles()

    # ---------------------- TRAIN DUMMY MODEL ----------------------
    def _train_dummy_model(self):
        # Example training data: [study_hours, attendance, previous_grade] => current_score
        X = np.array([
            [5, 80, 70],
            [10, 90, 80],
            [2, 60, 50],
            [8, 100, 90],
            [3, 50, 40],
            [6, 70, 65]
        ])
        y = np.array([60, 90, 40, 95, 35, 70])
        model = LinearRegression()
        model.fit(X, y)
        return model

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(main, text=f"📚 {self.APP_NAME} - Academic Predictor",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        tb.Label(main, text="Predict Exam Results Based on Input Parameters or CSV",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0, 20))

        # Input Form
        form_frame = tb.Frame(main)
        form_frame.pack(fill=X, pady=(0,6))

        self.name_input = self._create_form_row(form_frame, "Student Name:")
        self.study_input = self._create_form_row(form_frame, "Study Hours per Week:")
        self.attendance_input = self._create_form_row(form_frame, "Attendance %:")
        self.prev_grade_input = self._create_form_row(form_frame, "Previous Grade (0-100):")

        add_btn = tb.Button(form_frame, text="➕ Add Student", bootstyle=SUCCESS, command=self.add_student)
        add_btn.grid(row=4, column=0, columnspan=2, pady=5)

        csv_btn = tb.Button(form_frame, text="📁 Import CSV", bootstyle=INFO, command=self.import_csv)
        csv_btn.grid(row=5, column=0, columnspan=2, pady=5)

        # Progress bar
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=X, pady=(10,6))

        # Treeview for results
        columns = ("name", "study_hours", "attendance", "previous_grade", "predicted_grade")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=15)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=130)
        self.tree.pack(fill=BOTH, expand=True, pady=(0,6))

        # Action buttons
        row_btns = tb.Frame(main)
        row_btns.pack(fill=X, pady=(5,0))
        self.start_btn = tb.Button(row_btns, text="🚀 Predict Grades", bootstyle=PRIMARY, command=self.start)
        self.start_btn.pack(side=LEFT, padx=3)
        self.cancel_btn = tb.Button(row_btns, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)
        export_btn = tb.Button(row_btns, text="💾 Export Results", bootstyle=INFO, command=self.export_results)
        export_btn.pack(side=LEFT, padx=3)

        # Timer for smooth progress
        self.root.after(15, self.animate_progress)

    def _create_form_row(self, parent, label_text):
        row = tb.Frame(parent)
        row.grid(sticky=W, pady=2)
        tb.Label(row, text=label_text).pack(side=LEFT, padx=(0,5))
        entry = tb.Entry(row, width=30)
        entry.pack(side=LEFT)
        return entry

    # ---------------------- Actions ----------------------
    def add_student(self):
        try:
            student = {
                "name": self.name_input.get().strip(),
                "study_hours": float(self.study_input.get()),
                "attendance": float(self.attendance_input.get()),
                "previous_grade": float(self.prev_grade_input.get())
            }
            self.student_data.append(student)
            self.tree.insert("", END, values=(student["name"], student["study_hours"],
                                              student["attendance"], student["previous_grade"], "Pending"))
            self.name_input.delete(0, END)
            self.study_input.delete(0, END)
            self.attendance_input.delete(0, END)
            self.prev_grade_input.delete(0, END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hours, attendance, and previous grade.")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    try:
                        student = {
                            "name": row["name"].strip(),
                            "study_hours": float(row["study_hours"]),
                            "attendance": float(row["attendance"]),
                            "previous_grade": float(row["previous_grade"])
                        }
                        self.student_data.append(student)
                        self.tree.insert("", END, values=(student["name"], student["study_hours"],
                                                          student["attendance"], student["previous_grade"], "Pending"))
                        count += 1
                    except:
                        continue
            messagebox.showinfo("CSV Import", f"Successfully imported {count} students.")
        except Exception as e:
            messagebox.showerror("CSV Import Error", f"Failed to read CSV: {e}")

    def start(self):
        if not self.student_data:
            messagebox.showwarning("No Data", "Add at least one student before predicting.")
            return

        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        threading.Thread(target=self._run_worker, daemon=True).start()

    def _run_worker(self):
        self.worker_obj = PredictorWorker(
            self.student_data,
            model=self.model,
            callbacks={
                "found": self.update_student_grade,
                "progress": self.set_target,
                "finished": self.finish
            }
        )
        self.worker_obj.run()

    def update_student_grade(self, student, grade):
        for i in self.tree.get_children():
            vals = self.tree.item(i)["values"]
            if vals[0] == student["name"]:
                self.tree.item(i, values=(vals[0], vals[1], vals[2], vals[3], grade))
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

    def finish(self, results=None):
        self.start_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        self.progress["value"] = 100

    def export_results(self):
        if not self.student_data:
            messagebox.showwarning("Export", "No results to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if path:
            with open(path,"w",newline="",encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["name","study_hours","attendance","previous_grade","predicted_grade"])
                for i in self.tree.get_children():
                    writer.writerow(self.tree.item(i)["values"])
            messagebox.showinfo("Export", "Export completed successfully.")

    # ---------------------- Styles ----------------------
    def _apply_styles(self):
        self.style = tb.Style(theme="darkly")
        self.style.configure("TProgressbar", troughcolor="#1b1f3a", background="#7c3aed", thickness=14)
    
    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = ExamResultPredictorApp()
    app.run()
