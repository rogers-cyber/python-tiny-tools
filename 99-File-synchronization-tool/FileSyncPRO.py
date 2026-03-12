# ==========================================================
# FileSync PRO - File Synchronization Tool
# Professional Desktop Tool
# ==========================================================

import os
import sys
import shutil
import threading
import time
import traceback
from datetime import datetime
from queue import Queue, Empty

import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *


# =================== APP CONFIG ===================

APP_NAME = "FileSync PRO"
APP_VERSION = "1.0.0"


# =================== APP ===================

app = tk.Tk()
app.title(f"{APP_NAME} {APP_VERSION}")
app.geometry("1100x620")

tb.Style("darkly")


# =================== FLAGS ===================

ui_queue = Queue()

source_folder = tb.StringVar()
target_folder = tb.StringVar()

sync_running = False
auto_sync = False


# =================== UTIL ===================

def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def log_error():
    with open("error.log","a",encoding="utf-8") as f:
        f.write(traceback.format_exc()+"\n")


def log(msg):
    ui_queue.put(("log",msg))


def resource_path(file_name):
    base = getattr(sys,"_MEIPASS",os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base,file_name)


# =================== FILE SYNC ENGINE ===================

def sync_folders():

    global sync_running

    if not source_folder.get() or not target_folder.get():
        messagebox.showerror("Error","Select source and target folders")
        return

    sync_running = True

    src = source_folder.get()
    dst = target_folder.get()

    log("🔄 Synchronization started")

    try:

        for root, dirs, files in os.walk(src):

            if not sync_running:
                break

            rel_path = os.path.relpath(root, src)
            dst_path = os.path.join(dst, rel_path)

            if not os.path.exists(dst_path):
                os.makedirs(dst_path)

            for file in files:

                src_file = os.path.join(root,file)
                dst_file = os.path.join(dst_path,file)

                try:

                    if not os.path.exists(dst_file) or \
                       os.path.getmtime(src_file) > os.path.getmtime(dst_file):

                        shutil.copy2(src_file,dst_file)

                        log(f"✔ Synced: {file}")

                except:
                    log_error()

        log("✅ Synchronization finished")

    except:
        log_error()

    sync_running = False


# =================== AUTO SYNC ===================

def auto_sync_loop():

    global auto_sync

    auto_sync = True

    log("⏱ Auto Sync started")

    while auto_sync:

        sync_folders()

        for i in range(30):

            if not auto_sync:
                break

            time.sleep(1)

    log("🛑 Auto Sync stopped")


def stop_auto_sync():
    global auto_sync
    auto_sync = False


# =================== BROWSE ===================

def browse_source():

    folder = filedialog.askdirectory()

    if folder:
        source_folder.set(folder)


def browse_target():

    folder = filedialog.askdirectory()

    if folder:
        target_folder.set(folder)


# =================== ABOUT ===================

def show_about():

    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME} v{APP_VERSION}\n\n"
        "Professional File Synchronization Tool\n\n"
        "Features:\n"
        "• 🔄 One-click folder synchronization\n"
        "• 📁 Source → Destination mirror\n"
        "• ⚡ Fast incremental sync\n"
        "• ⏱ Automatic background syncing\n"
        "• 🧠 Smart file modification detection\n"
        "• 📜 Real-time activity log\n"
        "• 🖥 Modern UI with ttkbootstrap\n\n"
        "Built with:\n"
        "Python • Tkinter • ttkbootstrap\n\n"
        "Designed for developers, IT admins,\n"
        "and productivity workflows.\n\n"
        "© 2026 Mate Technologies\n"
        "https://matetools.gumroad.com"
    )


# =================== MENU ===================

menubar = tb.Menu(app)

help_menu = tb.Menu(menubar,tearoff=0)
help_menu.add_command(label="About",command=show_about)

menubar.add_cascade(label="Help",menu=help_menu)

app.config(menu=menubar)


try:
    app.iconbitmap(resource_path("logo.ico"))
except:
    pass


# =================== TITLE ===================

title_frame = tb.Frame(app)
title_frame.pack(pady=(10,10))

tb.Label(
    title_frame,
    text=APP_NAME,
    font=("Segoe UI",26,"bold"),
    bootstyle="primary"
).pack()

tb.Label(
    title_frame,
    text=f"v{APP_VERSION} • Professional File Synchronization Tool",
    font=("Segoe UI",10,"italic"),
    foreground="#9ca3af"
).pack()

tb.Label(
    title_frame,
    text="Synchronize folders, backup files, and mirror directories easily",
    font=("Segoe UI",9),
    foreground="#6b7280"
).pack()


# =================== CONTROLS ===================

frame_controls = tb.Labelframe(app,text="Controls",padding=10)
frame_controls.pack(fill="x",padx=10,pady=6)

tb.Button(
    frame_controls,
    text="🔄 Start Sync",
    bootstyle="success",
    command=lambda: threading.Thread(target=sync_folders,daemon=True).start()
).pack(side="left",padx=5)

tb.Button(
    frame_controls,
    text="⏱ Start Auto Sync",
    bootstyle="warning",
    command=lambda: threading.Thread(target=auto_sync_loop,daemon=True).start()
).pack(side="left",padx=5)

tb.Button(
    frame_controls,
    text="🛑 Stop Auto Sync",
    bootstyle="danger",
    command=stop_auto_sync
).pack(side="left",padx=5)


# =================== SETTINGS ===================

frame_settings = tb.Labelframe(app,text="Folders",padding=10)
frame_settings.pack(fill="x",padx=10,pady=6)

tb.Label(frame_settings,text="Source Folder").pack(side="left")

tb.Entry(frame_settings,textvariable=source_folder,width=40).pack(side="left",padx=5)

tb.Button(frame_settings,text="Browse",command=browse_source).pack(side="left",padx=5)

tb.Label(frame_settings,text="Target Folder").pack(side="left",padx=10)

tb.Entry(frame_settings,textvariable=target_folder,width=40).pack(side="left",padx=5)

tb.Button(frame_settings,text="Browse",command=browse_target).pack(side="left",padx=5)


# =================== LOG PANEL ===================

log_frame = tb.Labelframe(app,text="Activity Log",padding=10)
log_frame.pack(fill="both",expand=True,padx=10,pady=6)

log_text = tk.Text(log_frame)
log_text.pack(side="left",fill="both",expand=True)

scroll = tk.Scrollbar(log_frame,command=log_text.yview)
scroll.pack(side="right",fill="y")

log_text.config(yscrollcommand=scroll.set,state="disabled")


# =================== UI QUEUE ===================

def process_ui_queue():

    try:

        while True:

            cmd,data = ui_queue.get_nowait()

            if cmd=="log":

                log_text.config(state="normal")
                log_text.insert("end",data+"\n")
                log_text.see("end")
                log_text.config(state="disabled")

    except Empty:
        pass

    app.after(100,process_ui_queue)


# =================== START ===================

app.after(100,process_ui_queue)

app.mainloop()
