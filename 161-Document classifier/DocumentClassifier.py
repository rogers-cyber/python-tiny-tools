# ==========================================================
# Document Classifier PRO
# Professional Desktop Tool
# ==========================================================

import os
import sys
import threading
import time
import traceback
from queue import Queue, Empty
from tkinter import filedialog, messagebox
import tkinter as tk

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD


# =================== APP CONFIG ===================

APP_NAME = "Document Classifier"
APP_VERSION = "1.0.0"


# =================== APP ===================

app = TkinterDnD.Tk()
app.title(f"{APP_NAME} {APP_VERSION}")
app.geometry("1120x650")

tb.Style("darkly")


# =================== UTILITY ===================

def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


def log_error():
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(traceback.format_exc() + "\n")


def show_about():
    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME} v{APP_VERSION}\n\n"
        "Professional Document Classification Tool\n\n"
        "Features:\n"
        "• Drag & Drop files or folders\n"
        "• Folder scanning\n"
        "• Classify documents by content\n"
        "• Output results to folder\n"
        "• Pause / Stop processing\n"
        "• Live progress tracking\n"
        "• Detailed logging\n\n"
        "Built with Python + Tkinter + ttkbootstrap\n"
        "© 2026 Mate Technologies\n"
        "https://matetools.gumroad.com"
    )


try:
    app.iconbitmap(resource_path("logo.ico"))
except:
    pass


# =================== MENU ===================

menubar = tb.Menu(app)
help_menu = tb.Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)
app.config(menu=menubar)


# =================== FLAGS ===================

stop_flag = False
pause_flag = False
ui_queue = Queue()

file_list = []

output_path = tb.StringVar()


# =================== TITLE ===================

tb.Label(
    app,
    text=APP_NAME,
    font=("Segoe UI", 24, "bold")
).pack(pady=(10, 2))

tb.Label(
    app,
    text="Professional Document Classification – AI & Keyword Based",
    font=("Segoe UI", 10, "italic"),
    foreground="#9ca3af"
).pack(pady=(0, 10))


# =================== FRAME: FILE SELECTION ===================

frame1 = tb.Labelframe(app, text="Files & Folders", padding=10)
frame1.pack(fill="x", padx=10, pady=6)

file_frame = tb.Frame(frame1)
file_frame.pack(fill="x", pady=6)

file_listbox = tk.Listbox(file_frame, height=7, selectmode="extended")
file_listbox.pack(side="left", fill="x", expand=True)

scroll = tb.Scrollbar(file_frame, command=file_listbox.yview)
scroll.pack(side="right", fill="y")

file_listbox.config(yscrollcommand=scroll.set)


# =================== FILE FUNCTIONS ===================

def add_files():
    files = filedialog.askopenfilenames(title="Select Documents")
    for f in files:
        if f not in file_list:
            file_list.append(f)
            ui_queue.put(("add", f))


def add_folder():
    folder = filedialog.askdirectory(title="Select Folder")
    if not folder:
        return
    for root, dirs, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            if path not in file_list:
                file_list.append(path)
                ui_queue.put(("add", path))


def clear_list():
    file_list.clear()
    ui_queue.put(("clear", None))


def set_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)


# =================== DOCUMENT CLASSIFIER LOGIC ===================

def classify_document(file_path):
    """Simple keyword-based classification placeholder"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read().lower()
        if "invoice" in text:
            return "Invoices"
        elif "report" in text:
            return "Reports"
        elif "resume" in text or "cv" in text:
            return "Resumes"
        else:
            return "Others"
    except Exception:
        return "Unknown"


# =================== PROCESSING ===================

def process_documents():
    global stop_flag, pause_flag
    stop_flag = False
    pause_flag = False

    classify_btn.config(state="disabled")
    pause_btn.config(state="normal")
    stop_btn.config(state="normal")

    total = len(file_list)
    if total == 0:
        messagebox.showerror("Error", "No files selected.")
        classify_btn.config(state="normal")
        pause_btn.config(state="disabled")
        stop_btn.config(state="disabled")
        return

    out_dir = output_path.get() or os.path.dirname(file_list[0])
    ui_queue.put(("log", f"Starting classification of {total} files..."))

    for idx, file in enumerate(file_list, 1):
        if stop_flag:
            ui_queue.put(("log", "Process stopped by user."))
            break

        while pause_flag:
            time.sleep(0.2)

        try:
            category = classify_document(file)
            dest_dir = os.path.join(out_dir, category)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, os.path.basename(file))
            # Copy file to classified folder
            import shutil
            shutil.copy2(file, dest)
            ui_queue.put(("log", f"✔ {os.path.basename(file)} -> {category}"))
        except Exception:
            log_error()
            ui_queue.put(("log", f"❌ Failed: {file}"))

        percent = int((idx / total) * 100)
        ui_queue.put(("progress", percent))

    ui_queue.put(("complete", "Classification finished."))


# =================== CONTROL BUTTONS ===================

tb.Button(frame1, text="Add Files", command=add_files, bootstyle="success").pack(side="left", padx=4)
tb.Button(frame1, text="Add Folder", command=add_folder, bootstyle="info").pack(side="left", padx=4)
tb.Button(frame1, text="Clear List", command=clear_list, bootstyle="danger-outline").pack(side="left", padx=4)

tb.Label(frame1, text="Output Folder:", width=13).pack(side="left", padx=(12, 0))
tb.Entry(frame1, textvariable=output_path, width=40).pack(side="left", padx=6)
tb.Button(frame1, text="Browse", command=set_output_folder).pack(side="left", padx=4)

classify_btn = tb.Button(frame1, text="📂 Classify", bootstyle="success")
pause_btn = tb.Button(frame1, text="⏸ Pause", bootstyle="warning-outline", state="disabled")
stop_btn = tb.Button(frame1, text="🛑 Stop", bootstyle="danger-outline", state="disabled")

classify_btn.pack(side="left", padx=6)
pause_btn.pack(side="left", padx=4)
stop_btn.pack(side="left", padx=4)


# =================== PROGRESS ===================

frame2 = tb.Labelframe(app, text="Progress", padding=8)
frame2.pack(fill="x", padx=10)

progress_var = tb.IntVar()

tb.Progressbar(
    frame2,
    variable=progress_var,
    maximum=100,
    length=500
).pack(side="left", padx=10)

status_lbl = tb.Label(frame2, text="Status: Ready")
status_lbl.pack(side="left", padx=10)


# =================== LOG ===================

frame3 = tb.Labelframe(app, text="Processing Log", padding=8)
frame3.pack(fill="both", expand=True, padx=10, pady=6)

log_text = tk.Text(frame3, height=10)
log_text.pack(side="left", fill="both", expand=True)

log_scroll = tk.Scrollbar(frame3, command=log_text.yview)
log_scroll.pack(side="right", fill="y")

log_text.config(yscrollcommand=log_scroll.set, state="disabled")


# =================== UI QUEUE ===================

def process_ui_queue():
    try:
        while True:
            cmd, data = ui_queue.get_nowait()
            if cmd == "add":
                file_listbox.insert("end", data)
            elif cmd == "clear":
                file_listbox.delete(0, "end")
            elif cmd == "progress":
                progress_var.set(data)
            elif cmd == "log":
                log_text.config(state="normal")
                log_text.insert("end", data + "\n")
                log_text.see("end")
                log_text.config(state="disabled")
            elif cmd == "complete":
                progress_var.set(100)
                status_lbl.config(text=f"Status: {data}")
                classify_btn.config(state="normal")
                pause_btn.config(state="disabled")
                stop_btn.config(state="disabled")
    except Empty:
        pass
    app.after(100, process_ui_queue)


# =================== BUTTON COMMANDS ===================

def toggle_pause():
    global pause_flag
    pause_flag = not pause_flag
    pause_btn.config(text="▶ Resume" if pause_flag else "⏸ Pause")


def stop_process():
    global stop_flag
    stop_flag = True
    status_lbl.config(text="Status: Stopping...")


classify_btn.config(
    command=lambda: threading.Thread(target=process_documents, daemon=True).start()
)
pause_btn.config(command=toggle_pause)
stop_btn.config(command=stop_process)


# =================== DRAG & DROP ===================

def drop(event):
    files = app.tk.splitlist(event.data)
    for f in files:
        if os.path.isfile(f):
            if f not in file_list:
                file_list.append(f)
                ui_queue.put(("add", f))
        elif os.path.isdir(f):
            for root, dirs, names in os.walk(f):
                for name in names:
                    path = os.path.join(root, name)
                    if path not in file_list:
                        file_list.append(path)
                        ui_queue.put(("add", path))


file_listbox.drop_target_register(DND_FILES)
file_listbox.dnd_bind("<<Drop>>", drop)


# =================== START UI ===================

app.after(100, process_ui_queue)
app.mainloop()
