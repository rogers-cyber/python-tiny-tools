import sys
import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from PIL import Image, ImageTk
import subprocess
import PyPDF2

# =================== APP CONFIG ===================
APP_NAME = "Mate Desktop Search Pro"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Mate Technologies"

def resource_path(name):
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return Path(base) / name

# ================= APP =================

app = tk.Tk()
style = tb.Style(theme="superhero")

app.title(f"{APP_NAME} {APP_VERSION}")
app.geometry("1200x650")

# ================= VARIABLES =================

indexed_files = []
recent_files = []

current_folder = tk.StringVar(value="")
search_query = tk.StringVar(value="")
status_text = tk.StringVar(value="Idle")
file_filter = tk.StringVar(value="All")
sort_mode = tk.StringVar(value="Name")

preview_img = None

FILTERS = {
    "All": [],
    "Images": [".png",".jpg",".jpeg",".gif"],
    "Docs": [".txt",".pdf",".docx"],
    "Videos": [".mp4",".mov",".avi"]
}

# ================= FUNCTIONS =================

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        current_folder.set(folder)
        index_folder(folder)

def index_folder(folder):
    indexed_files.clear()

    for root, dirs, files in os.walk(folder):
        for f in files:
            indexed_files.append(os.path.join(root,f))

    status_text.set(f"Indexed {len(indexed_files)} files")
    update_results()

def file_matches(path):
    ext = Path(path).suffix.lower()
    allowed = FILTERS[file_filter.get()]
    return not allowed or ext in allowed

def search_content(path, query):
    try:
        if path.endswith(".txt"):
            return query in open(path,errors="ignore").read().lower()

        if path.endswith(".pdf"):
            reader = PyPDF2.PdfReader(path)
            for p in reader.pages[:3]:
                if query in p.extract_text().lower():
                    return True
    except:
        pass
    return False

def update_results(*args):
    q = search_query.get().lower()
    results.delete(0,tk.END)

    matches = []

    for f in indexed_files:
        if not file_matches(f):
            continue

        name_match = q in os.path.basename(f).lower()
        content_match = q and search_content(f,q)

        if not q or name_match or content_match:
            matches.append(f)

    if sort_mode.get()=="Size":
        matches.sort(key=lambda x: os.path.getsize(x))
    elif sort_mode.get()=="Date":
        matches.sort(key=lambda x: os.path.getmtime(x))
    else:
        matches.sort()

    for m in matches[:500]:
        results.insert(tk.END,m)

    status_text.set(f"{len(matches)} result(s)")

def open_selected(event=None):
    sel = results.curselection()
    if not sel: return
    path = results.get(sel[0])

    recent_files.append(path)
    if len(recent_files)>20:
        recent_files.pop(0)

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Error",str(e))

def show_preview(event=None):
    global preview_img
    sel = results.curselection()
    if not sel: return

    path = results.get(sel[0])
    ext = Path(path).suffix.lower()

    preview.delete("all")

    try:
        if ext in [".png",".jpg",".jpeg",".gif"]:
            img = Image.open(path)
            img.thumbnail((250,250))
            preview_img = ImageTk.PhotoImage(img)
            preview.create_image(0,0,anchor="nw",image=preview_img)

        elif ext==".txt":
            txt = open(path,errors="ignore").read()[:1500]
            preview.create_text(5,5,anchor="nw",fill="white",text=txt)

        else:
            info = f"{Path(path).name}\n\nSize: {os.path.getsize(path)//1024} KB\nModified: {time.ctime(os.path.getmtime(path))}"
            preview.create_text(5,5,anchor="nw",fill="white",text=info)

    except:
        pass

def show_recent():
    results.delete(0,tk.END)
    for f in reversed(recent_files):
        results.insert(tk.END,f)

def show_about():
    messagebox.showinfo(
        APP_NAME,
        f"{APP_NAME} {APP_VERSION}\n\n"
        "Advanced desktop search engine.\n\n"
        "• Content search TXT/PDF\n"
        "• Filters\n"
        "• Preview\n"
        "• Sorting\n"
        "• Recent files\n\n"
        "Mate Technologies"
    )

# ================= UI =================

tb.Label(app,text=APP_NAME,font=("Segoe UI",18,"bold")).pack(pady=5)

main = tb.Frame(app)
main.pack(fill="both",expand=True,padx=10,pady=10)

# Left
left = tb.Frame(main)
left.pack(side="left",fill="both",expand=True)

results = tk.Listbox(left,bg="#222",fg="white")
results.pack(fill="both",expand=True)
results.bind("<Double-Button-1>",open_selected)
results.bind("<<ListboxSelect>>",show_preview)

# Right
right = tb.Frame(main,width=320)
right.pack(side="right",fill="y",padx=5)

tb.Entry(right,textvariable=current_folder).pack(fill="x")
tb.Button(right,text="Select Folder",bootstyle="primary",command=select_folder).pack(fill="x",pady=3)

tb.Entry(right,textvariable=search_query).pack(fill="x")
search_query.trace_add("write",update_results)

tb.Combobox(right,values=list(FILTERS.keys()),textvariable=file_filter).pack(fill="x",pady=2)
file_filter.trace_add("write",update_results)

tb.Combobox(right,values=["Name","Size","Date"],textvariable=sort_mode).pack(fill="x",pady=2)
sort_mode.trace_add("write",update_results)

tb.Button(right,text="Recent Files",bootstyle="info",command=show_recent).pack(fill="x",pady=3)
tb.Button(right,text="Open",bootstyle="success",command=open_selected).pack(fill="x",pady=3)
tb.Button(right,text="About",bootstyle="secondary",command=show_about).pack(fill="x",pady=3)

preview = tk.Canvas(right,width=250,height=250,bg="#333")
preview.pack(pady=5)

tb.Label(right,textvariable=status_text).pack()

# ================= RUN =================
app.mainloop()
