"""
SpamSentinel v1.0 - Enterprise Edition
Ultra-Fast Email Spam Detector with GUI
Supports massive email sets with smooth UI
"""

import os, sys, re, threading
from collections import Counter, deque
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


# ---------------------- SPAM DETECTION WORKER ----------------------
class SpamWorker:
    def __init__(self, files, min_confidence, include_words,
                 exclude_words, regex_pattern, max_results,
                 callbacks):
        self.files = files
        self.min_confidence = min_confidence
        self.include_words = include_words
        self.exclude_words = exclude_words
        self.regex_pattern = re.compile(regex_pattern, re.IGNORECASE) if regex_pattern else None
        self.max_results = max_results
        self._running = True
        self.callbacks = callbacks

        # Fake spam scoring keywords
        self.spam_patterns = [
            re.compile(r"(free money|win cash|click here|urgent|lottery)", re.I),
            re.compile(r"(prize|offer|risk-free|credit card)", re.I),
        ]

    def stop(self):
        self._running = False

    def spam_score(self, text):
        score = 0
        for pattern in self.spam_patterns:
            if pattern.search(text):
                score += 50
        return min(score, 100)  # max 100

    def run(self):
        total_files = len(self.files)
        counters = Counter()
        results_buffer = deque(maxlen=self.max_results)

        for i, path in enumerate(self.files):
            if not self._running:
                break
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if self.include_words and not any(w in content.lower() for w in self.include_words):
                        continue
                    if self.exclude_words and any(w in content.lower() for w in self.exclude_words):
                        continue
                    if self.regex_pattern and not self.regex_pattern.search(content):
                        continue

                    score = self.spam_score(content)
                    if score < self.min_confidence:
                        continue

                    counters["SPAM"] += 1
                    counters["TOTAL"] += 1
                    results_buffer.append((path, score))

                    if "found" in self.callbacks:
                        self.callbacks["found"](path, score)

                    if counters["TOTAL"] >= self.max_results:
                        break
            except Exception:
                pass

            if total_files > 0 and "progress" in self.callbacks:
                self.callbacks["progress"](int((i + 1) / total_files * 100))
            if "stats" in self.callbacks:
                self.callbacks["stats"](dict(counters))

        if "stats" in self.callbacks:
            self.callbacks["stats"](dict(counters))
        if "finished" in self.callbacks:
            self.callbacks["finished"]()


# ---------------------- MAIN APP ----------------------
class SpamSentinelApp:
    APP_NAME = "SpamSentinel"
    APP_VERSION = "1.0"
    SUPPORTED_EXT = (".eml", ".txt")

    def __init__(self):
        if DND_ENABLED:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tb.Window(themename="darkly")

        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.minsize(1200, 700)

        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except: pass

        self.worker_obj = None
        self.smooth_value = 0
        self.target_progress = 0
        self.file_set = set()

        # Checkbox variables
        self.eml_var = tk.BooleanVar(value=True)
        self.txt_var = tk.BooleanVar(value=True)

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=10)
        main.pack(fill=BOTH, expand=True)

        tb.Label(main, text=f"🧠 {self.APP_NAME} - Enterprise Spam Detector",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))

        tb.Label(main, text="Detect spam emails quickly and efficiently",
                 font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0, 20))

        # Row 1: File Selection
        row1 = tb.Frame(main)
        row1.pack(fill=X, pady=(0,6))

        self.path_input = tb.Entry(row1, width=90)
        self.path_input.pack(side=LEFT, fill=X, expand=True, padx=(0,6))
        self.path_input.insert(0, "Drag & drop email files or folders here…")

        browse_btn = tb.Button(row1, text="📂 Browse", bootstyle=INFO, command=self.browse)
        browse_btn.pack(side=LEFT, padx=3)

        self.start_btn = tb.Button(row1, text="🚀 Start Scan", bootstyle=SUCCESS, command=self.start)
        self.start_btn.pack(side=LEFT, padx=3)

        self.cancel_btn = tb.Button(row1, text="⏹ Cancel", bootstyle=DANGER, command=self.cancel)
        self.cancel_btn.pack(side=LEFT, padx=3)
        self.cancel_btn.config(state=DISABLED)

        export_btn = tb.Button(row1, text="💾 Export Selected", bootstyle=PRIMARY, command=self.export_results)
        export_btn.pack(side=LEFT, padx=3)

        about_btn = tb.Button(row1, text="ℹ️ About", bootstyle=INFO, command=self.show_about)
        about_btn.pack(side=LEFT, padx=3)

        # Row 2: Filters
        row2 = tb.Frame(main)
        row2.pack(fill=X, pady=(0,6))

        self.eml_cb = tb.Checkbutton(row2, text=".eml", bootstyle=SUCCESS, variable=self.eml_var)
        self.eml_cb.pack(side=LEFT, padx=3)
        self.txt_cb = tb.Checkbutton(row2, text=".txt", bootstyle=SUCCESS, variable=self.txt_var)
        self.txt_cb.pack(side=LEFT, padx=3)

        tb.Label(row2, text="Min Spam Confidence (%)").pack(side=LEFT, padx=3)
        self.confidence_input = tb.Entry(row2, width=5)
        self.confidence_input.insert(0, "50")
        self.confidence_input.pack(side=LEFT, padx=3)

        tb.Label(row2, text="Include words").pack(side=LEFT, padx=3)
        self.include_input = tb.Entry(row2, width=20)
        self.include_input.pack(side=LEFT, padx=3)

        tb.Label(row2, text="Exclude words").pack(side=LEFT, padx=3)
        self.exclude_input = tb.Entry(row2, width=20)
        self.exclude_input.pack(side=LEFT, padx=3)

        tb.Label(row2, text="Regex filter (optional)").pack(side=LEFT, padx=3)
        self.regex_input = tb.Entry(row2, width=20)
        self.regex_input.pack(side=LEFT, padx=3)

        # Progress
        self.progress = tb.Progressbar(main, bootstyle="success-striped", maximum=100)
        self.progress.pack(fill=X, pady=(0,6))

        # Treeview for multi-select batch
        columns = ("selected", "filename", "spam_score")
        self.tree = ttk.Treeview(main, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("selected", text="✅")
        self.tree.heading("filename", text="Filename", anchor=W)
        self.tree.heading("spam_score", text="Spam Score (%)", anchor=W)
        self.tree.column("selected", width=50, anchor=CENTER)
        self.tree.column("filename", width=800)
        self.tree.column("spam_score", width=120)
        self.tree.pack(fill=BOTH, expand=True, pady=(0,6))

        self.stats_label = tb.Label(main, text="TOTAL: 0 | SPAM: 0")
        self.stats_label.pack(anchor=E)

        # Timer for smooth progress
        self.root.after(15, self.animate_progress)

        # Bind DnD if enabled
        if DND_ENABLED:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self.on_drop)

    # ---------------------- Unified Browse + DnD ----------------------
    def browse(self):
        folder = filedialog.askdirectory(title="Select Email Folder")
        if folder:
            self.start_btn.config(state=DISABLED)
            self.cancel_btn.config(state=NORMAL)
            threading.Thread(target=self._scan_and_queue_files_thread, args=([folder],), daemon=True).start()

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
            if ((ext == ".eml" and self.eml_var.get()) or (ext == ".txt" and self.txt_var.get())):
                if path not in self.file_set:
                    self.file_set.add(path)
                    self.tree.insert("", END, values=("☑️", path, "0"))
        self.root.after(1, lambda: self._insert_files_chunked(remaining, chunk_size))

    # ---------------------- Actions ----------------------
    def start(self):
        selected_files = [self.tree.item(i)['values'][1] for i in self.tree.get_children()
                          if self.tree.item(i)['values'][0]=="☑️"]
        if not selected_files:
            messagebox.showwarning("No Selection", "Select emails using the checkboxes before scanning.")
            return
        try:
            min_conf = int(self.confidence_input.get())
        except ValueError:
            min_conf = 50
        self.progress["value"] = 0
        self.smooth_value = 0
        self.target_progress = 0
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        threading.Thread(target=self._run_worker, args=(selected_files, min_conf), daemon=True).start()

    def _run_worker(self, files, min_confidence):
        self.worker_obj = SpamWorker(
            files,
            min_confidence,
            [w.strip() for w in self.include_input.get().lower().split(",") if w.strip()],
            [w.strip() for w in self.exclude_input.get().lower().split(",") if w.strip()],
            self.regex_input.get(),
            max_results=200_000,
            callbacks={
                "found": self.add_line,
                "progress": self.set_target,
                "stats": self.update_stats,
                "finished": self.finish
            }
        )
        self.worker_obj.run()

    def add_line(self, file, score):
        for i in self.tree.get_children():
            if self.tree.item(i)['values'][1] == file:
                self.tree.item(i, values=("☑️", file, str(score)))
                color = "#dc2626" if score >= 70 else "#facc15" if score >= 50 else "#4ade80"
                self.tree.tag_configure(file, foreground=color)
                self.tree.item(i, tags=(file,))
                break

    def update_stats(self, stats):
        self.stats_label.config(text=f"TOTAL: {stats.get('TOTAL',0)} | SPAM: {stats.get('SPAM',0)}")

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
            messagebox.showwarning("Export", "No selected files to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                for s in selected_files:
                    f.write(f"{s[1]} | Spam Score: {s[2]}%\n")
            messagebox.showinfo("Export", "Export completed")

    # ---------------------- About ----------------------
    def show_about(self):
        messagebox.showinfo(
            f"About {self.APP_NAME}",
            f"{self.APP_NAME} v{self.APP_VERSION}\n\n"
            "• Drag & drop email files or folders\n"
            "• Multi-select batch scanning with checkboxes\n"
            "• Real-time spam score highlighting\n"
            "• Include/exclude filters & optional regex\n"
            "• Export selected results to text\n\n"
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
    app = SpamSentinelApp()
    app.run()
