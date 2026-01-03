import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from dataclasses import dataclass
from typing import List, Dict
import os
import shutil
import csv

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinterdnd2 import TkinterDnD, DND_FILES

# ---------------- GLOBAL STATE ---------------- #
storage_nodes = ["Node_A", "Node_B", "Node_C"]
file_registry: List["DistributedFile"] = []

BASE_DIR = "dfs_nodes"
os.makedirs(BASE_DIR, exist_ok=True)
for n in storage_nodes:
    os.makedirs(os.path.join(BASE_DIR, n), exist_ok=True)

# ---------------- DATA STRUCTURE ---------------- #
@dataclass
class DistributedFile:
    filename: str
    size_kb: float
    replicas: List[str]

# ---------------- HELPERS ---------------- #
def kb(size):
    return round(size / 1024, 2)

def reset_nodes():
    for n in storage_nodes:
        path = os.path.join(BASE_DIR, n)
        shutil.rmtree(path)
        os.makedirs(path)
    file_registry.clear()

# ---------------- DRAG & DROP ---------------- #
def drop_file(event):
    files = app.tk.splitlist(event.data)
    for file in files:
        if os.path.isfile(file):
            threading.Thread(
                target=store_file,
                args=(file,),
                daemon=True
            ).start()

# ---------------- FILE STORAGE ---------------- #
def store_file(path):
    filename = os.path.basename(path)
    size = kb(os.path.getsize(path))
    replicas = []

    try:
        for node in storage_nodes:
            dest = os.path.join(BASE_DIR, node, filename)
            shutil.copy(path, dest)
            replicas.append(node)

        file_registry.append(
            DistributedFile(filename, size, replicas)
        )
        app.after(0, refresh_files)

    except Exception as e:
        messagebox.showerror("Storage Error", str(e))

# ---------------- DOWNLOAD ---------------- #
def download_file():
    sel = file_listbox.curselection()
    if not sel:
        return

    file = file_registry[sel[0]]
    node = file.replicas[0]

    src = os.path.join(BASE_DIR, node, file.filename)
    dest = filedialog.asksaveasfilename(
        initialfile=file.filename
    )

    if dest:
        shutil.copy(src, dest)
        messagebox.showinfo("Downloaded", "File retrieved successfully")

# ---------------- EXPORT METADATA ---------------- #
def export_metadata():
    if not file_registry:
        messagebox.showwarning("No Data", "No files to export")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")]
    )
    if not path:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Size (KB)", "Replicas"])
        for fdata in file_registry:
            writer.writerow([
                fdata.filename,
                fdata.size_kb,
                ", ".join(fdata.replicas)
            ])

    messagebox.showinfo("Exported", "Metadata exported successfully")

# ---------------- DISPLAY ---------------- #
def refresh_files():
    file_listbox.delete(0, END)
    for f in file_registry:
        file_listbox.insert(
            END,
            f"{f.filename} ({f.size_kb} KB) → {len(f.replicas)} replicas"
        )

# ---------------- UI ---------------- #
app = TkinterDnD.Tk()
app.title("🗄️ Distributed File System")
app.geometry("950x650")

style = tb.Style("flatly")

top = tb.Frame(app, padding=15)
top.pack(fill=X)

tb.Label(
    top,
    text="🗄️ Distributed File System (Simulated)",
    font=("Segoe UI", 18, "bold")
).pack(anchor=W)

tb.Label(
    top,
    text="Drag & drop files below to distribute across nodes",
    font=("Segoe UI", 11)
).pack(anchor=W, pady=5)

drop_zone = tb.Frame(top, height=80, bootstyle="secondary")
drop_zone.pack(fill=X, pady=10)

tb.Label(
    drop_zone,
    text="📁 DROP FILES HERE",
    font=("Segoe UI", 14)
).place(relx=0.5, rely=0.5, anchor=CENTER)

drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind("<<Drop>>", drop_file)

tb.Label(top, text="Stored Files:", font=("Segoe UI", 12)).pack(anchor=W)

file_listbox = tk.Listbox(top, height=10)
file_listbox.pack(fill=X, pady=5)

btn_row = tb.Frame(top)
btn_row.pack(fill=X, pady=5)

tb.Button(
    btn_row,
    text="Download",
    bootstyle="success",
    command=download_file
).pack(side=LEFT)

tb.Button(
    btn_row,
    text="Export Metadata",
    command=export_metadata
).pack(side=LEFT, padx=5)

tb.Button(
    btn_row,
    text="Reset Nodes",
    bootstyle="danger",
    command=lambda: [reset_nodes(), refresh_files()]
).pack(side=LEFT, padx=5)

# ---------------- FOOTER ---------------- #
footer = tb.Frame(app, padding=10)
footer.pack(fill=X, side=BOTTOM)

tb.Label(
    footer,
    text="Nodes: " + " | ".join(storage_nodes),
    font=("Segoe UI", 10)
).pack(anchor=W)

app.mainloop()
