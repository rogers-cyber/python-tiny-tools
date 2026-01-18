"""
SpamShield v3.1 - SMS Spam Classifier
AI-Powered SMS Spam Detection
Auto-downloads the SMSSpamCollection dataset if missing
Efficient batch classification from CSV/TXT
"""

import os, sys, threading, csv
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

# ML libs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import joblib

import urllib.request
import zipfile

# ---------------------- UTIL ----------------------

def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def download_dataset():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
    zip_path = resource_path("smsspamcollection.zip")
    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        messagebox.showerror("Download Failed", f"Failed to download dataset:\n{e}")
        sys.exit(1)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(resource_path(""))
    os.remove(zip_path)

# ---------------------- ML MODEL ----------------------

def train_sms_model():
    ds_path = resource_path("SMSSpamCollection")
    if not os.path.exists(ds_path):
        download_dataset()

    df = pd.read_csv(ds_path, sep="\t", header=None, names=["label", "text"])
    df["label_num"] = df["label"].map({"ham": 0, "spam": 1})

    X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label_num"],
                                                        test_size=0.2, random_state=42)

    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"[INFO] Model trained — Test Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")

    model_path = resource_path("sms_spam_model.pkl")
    joblib.dump(model, model_path)

    return model

def load_model():
    model_path = resource_path("sms_spam_model.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return train_sms_model()

# ---------------------- SPAM WORKER ----------------------

class SpamWorker:
    def __init__(self, files, model, callbacks, max_results=200_000):
        self.files = files
        self.model = model
        self.callbacks = callbacks
        self.max_results = max_results
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        total_files = len(self.files)
        stats = {"TOTAL": 0, "SPAM": 0, "HAM": 0}

        for i, path in enumerate(self.files):
            if not self._running:
                break

            try:
                texts = []
                with open(path, newline="", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            texts.append(row[0].strip())

                if texts:
                    labels_num = self.model.predict(texts)
                    labels = ["SPAM" if l == 1 else "HAM" for l in labels_num]

                    for t, lbl in zip(texts, labels):
                        stats[lbl] += 1
                        stats["TOTAL"] += 1

                        if "found" in self.callbacks:
                            self.callbacks["found"](path, t, lbl)

                        if stats["TOTAL"] >= self.max_results:
                            break

            except Exception as e:
                print(f"[WARN] Could not read {path}: {e}")

            pct = int((i + 1) / total_files * 100)
            if "progress" in self.callbacks:
                self.callbacks["progress"](pct)
            if "stats" in self.callbacks:
                self.callbacks["stats"](dict(stats))

        if "finished" in self.callbacks:
            self.callbacks["finished"]()

# ---------------------- MAIN APP ----------------------

class SpamShieldApp:
    APP_NAME = "SpamShield"
    APP_VERSION = "3.1"
    SUPPORTED_EXT = (".csv", ".txt")

    def __init__(self):
        if DND_ENABLED:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tb.Window(themename="darkly")

        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1200, 650)

        self.model = load_model()

        self.worker = None
        self.smooth = 0
        self.target = 0
        self.file_set = set()

        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        tb.Label(main, text=f"📩 {self.APP_NAME} - AI SMS Spam Detector",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0,4))

        tb.Label(main, text="Batch classification — handles large SMS datasets",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0,12))

        row1 = tb.Frame(main)
        row1.pack(fill=tk.X)

        self.path_input = tb.Entry(row1, width=90)
        self.path_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop CSV/TXT files with SMS data…")

        btn_browse = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        btn_browse.pack(side=tk.LEFT, padx=3)

        self.btn_start = tb.Button(row1, text="🚀 Start", bootstyle=SUCCESS, command=self.start)
        self.btn_start.pack(side=tk.LEFT, padx=3)

        self.btn_cancel = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.btn_cancel.pack(side=tk.LEFT, padx=3)
        self.btn_cancel.config(state=tk.DISABLED)

        btn_export = tb.Button(row1, text="💾 Export", bootstyle=PRIMARY, command=self.export_results)
        btn_export.pack(side=tk.LEFT, padx=3)

        btn_about = tb.Button(row1, text="ℹ️ About", bootstyle=INFO, command=self.show_about)
        btn_about.pack(side=tk.LEFT, padx=3)

        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=tk.X, pady=(6,6))

        columns = ("selected", "text", "label")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", height=20)
        self.tree.heading("selected", text="☑️")
        self.tree.heading("text", text="SMS Text")
        self.tree.heading("label", text="Prediction")

        self.tree.column("selected", width=50, anchor=tk.CENTER)
        self.tree.column("text", width=800)
        self.tree.column("label", width=120)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.stats_lbl = tb.Label(main, text="TOTAL: 0 | SPAM: 0 | HAM: 0")
        self.stats_lbl.pack(anchor=tk.E)

        self.root.after(15, self._anim_progress)

        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---- File Queue ----

    def browse(self):
        files = filedialog.askopenfilenames(title="Select SMS Data Files",
                                            filetypes=[("CSV Files","*.csv"), ("Text Files","*.txt")])
        if files:
            self._queue_files(files)

    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        self._queue_files(paths)

    def _queue_files(self, paths):
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if ext in self.SUPPORTED_EXT and p not in self.file_set:
                self.file_set.add(p)
                self.tree.insert("", tk.END, values=("☑️", p, "Queued"))
        self.path_input.delete(0, tk.END)
        self.path_input.insert(0, f"{len(self.file_set)} files queued")

    # ---- Actions ----

    def start(self):
        selected = [self.tree.item(i)["values"][1] for i in self.tree.get_children()
                    if self.tree.item(i)["values"][0] == "☑️"]
        if not selected:
            messagebox.showwarning("No Data", "Select at least one file to classify.")
            return

        self.btn_start.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL)
        self.progress["value"] = 0
        self.smooth = 0
        self.target = 0

        threading.Thread(target=self._run_worker, args=(selected,), daemon=True).start()

    def _run_worker(self, files):
        self.worker = SpamWorker(files, self.model,
                                 callbacks={"found": self._add_row,
                                            "progress": self._set_target,
                                            "stats": self._update_stats,
                                            "finished": self._finish})
        self.worker.run()

    def _add_row(self, file, text, label):
        self.tree.insert("", tk.END, values=("☑️", text, label))
        self.tree.tag_configure(label, foreground="#dc2626" if label == "SPAM" else "#4ade80")
        iid = self.tree.get_children()[-1]
        self.tree.item(iid, tags=(label,))

    def _update_stats(self, stats):
        self.stats_lbl.config(text=f"TOTAL: {stats['TOTAL']} | SPAM: {stats['SPAM']} | HAM: {stats['HAM']}")

    def _set_target(self, v):
        self.target = v

    def _anim_progress(self):
        if self.smooth < self.target:
            self.smooth += 1
            self.progress["value"] = self.smooth
        self.root.after(15, self._anim_progress)

    def cancel(self):
        if self.worker:
            self.worker.stop()
        self._finish()

    def _finish(self):
        self.btn_start.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.DISABLED)
        self.progress["value"] = 100

    # ---- Export ----

    def export_results(self):
        rows = [self.tree.item(i)["values"] for i in self.tree.get_children()
                if self.tree.item(i)["values"][0] == "☑️"]
        if not rows:
            messagebox.showwarning("Export", "No classified messages to export.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files","*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for _, text, lbl in rows:
                    f.write(f"{text} | {lbl}\n")
            messagebox.showinfo("Export", "Results exported successfully!")

    # ---- About ----

    def show_about(self):
        messagebox.showinfo(
            f"About {self.APP_NAME}",
            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
            "• Drag & drop SMS dataset files\n"
            "• Auto-downloads needed dataset\n"
            "• Batch ML classification\n"
            "• SPAM/HAM highlighting\n"
            "• Export results\n\n"
            "🏢 Built with ❤️"
        )

    def _apply_styles(self):
        self.root.style = tb.Style(theme="darkly")
        self.root.style.configure("TProgressbar", troughcolor="#1b1f3a",
                                  background="#7c3aed", thickness=14)

    def run(self):
        self.root.mainloop()

# ---- Run App ----

if __name__ == "__main__":
    app = SpamShieldApp()
    app.run()
