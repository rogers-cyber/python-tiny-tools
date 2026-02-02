import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
import subprocess

# =================== APP CONFIG ===================
APP_NAME = "Mate Desktop Search"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Mate Technologies"
APP_WEBSITE = "https://matetools.gumroad.com"

def resource_path(name):
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return Path(base) / name

# ================= APP =================

app = tk.Tk()
style_obj = tb.Style(theme="superhero")

app.title(f"{APP_NAME} {APP_VERSION}")
app.geometry("1000x600")

try:
    app.iconbitmap(str(resource_path("logo.ico")))
except:
    pass

# =================== VARIABLES ===================

indexed_files = []
current_folder = tk.StringVar(master=app, value="")
search_query = tk.StringVar(master=app, value="")
status_text = tk.StringVar(master=app, value="Idle")

# =================== FUNCTIONS ===================

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        current_folder.set(folder)
        index_folder(folder)

def index_folder(folder):
    indexed_files.clear()
    for root, dirs, files in os.walk(folder):
        for f in files:
            indexed_files.append(os.path.join(root, f))

    status_text.set(f"Indexed {len(indexed_files)} files")
    update_results()

def update_results(*args):
    query = search_query.get().lower()

    results_list.delete(0, tk.END)

    if not query:
        return

    matches = [f for f in indexed_files if query in os.path.basename(f).lower()]

    for m in matches[:500]:
        results_list.insert(tk.END, m)

    status_text.set(f"{len(matches)} result(s)")

def open_selected(event=None):
    sel = results_list.curselection()
    if not sel:
        return

    path = results_list.get(sel[0])

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_about():
    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME} v{APP_VERSION}\n\n"
        "A fast lightweight desktop file search engine.\n\n"
        "Features:\n"
        "• Folder indexing\n"
        "• Instant filename search\n"
        "• Double-click to open files\n"
        "• Works fully offline\n"
        "• Modern ttkbootstrap UI\n\n"
        "Use Cases:\n"
        "• Find documents quickly\n"
        "• Locate media files\n"
        "• Search project folders\n\n"
        f"{APP_AUTHOR}\n{APP_WEBSITE}"
    )

# =================== UI ===================

tb.Label(
    app,
    text=APP_NAME,
    font=("Segoe UI", 18, "bold")
).pack(pady=(10,2))

tb.Label(
    app,
    text="Instant local file search",
    font=("Segoe UI",10,"italic"),
    foreground="#9ca3af"
).pack(pady=(0,10))

main_frame = tb.Frame(app)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Left: Results
left = tb.Frame(main_frame)
left.pack(side="left", fill="both", expand=True)

results_list = tk.Listbox(left, bg="#222", fg="white")
results_list.pack(fill="both", expand=True)

results_list.bind("<Double-Button-1>", open_selected)

# Right: Controls
right = tb.Frame(main_frame, width=260)
right.pack(side="right", fill="y", padx=5)

tb.Label(right, text="Indexed Folder:").pack(anchor="w")
tb.Entry(right, textvariable=current_folder).pack(fill="x", pady=3)

tb.Button(
    right,
    text="Select Folder",
    bootstyle="primary",
    command=select_folder
).pack(fill="x", pady=5)

tb.Label(right, text="Search:").pack(anchor="w")

search_entry = tb.Entry(right, textvariable=search_query)
search_entry.pack(fill="x", pady=3)
search_entry.bind("<KeyRelease>", update_results)

tb.Button(
    right,
    text="Open Selected",
    bootstyle="success",
    command=open_selected
).pack(fill="x", pady=5)

tb.Button(
    right,
    text="About",
    bootstyle="secondary",
    command=show_about
).pack(fill="x", pady=5)

tb.Label(right, textvariable=status_text).pack(pady=10)

# =================== RUN ===================
app.mainloop()
