import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PyPDF2 import PdfMerger, PdfReader
from pdf2image import convert_from_path
from PIL import Image, ImageTk

# ---------------- GLOBALS ---------------- #
pdf_files = []
preview_cache = {}

# ---------------- FUNCTIONS ---------------- #
def add_pdfs(files=None):
    if not files:
        files = filedialog.askopenfilenames(
            filetypes=[("PDF Files", "*.pdf")]
        )
    for f in files:
        f = f.strip("{}")
        if f.lower().endswith(".pdf") and f not in pdf_files:
            pdf_files.append(f)
            listbox.insert(tk.END, os.path.basename(f))

def on_drop(event):
    files = app.tk.splitlist(event.data)
    add_pdfs(files)

def remove_selected():
    sel = listbox.curselection()
    if not sel:
        return
    i = sel[0]
    pdf_files.pop(i)
    listbox.delete(i)
    preview_label.config(image='')

def refresh_list():
    listbox.delete(0, tk.END)
    for f in pdf_files:
        listbox.insert(tk.END, os.path.basename(f))

def merge_pdfs():
    if not pdf_files:
        messagebox.showwarning("No PDFs", "Add PDF files first.")
        return

    out = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not out:
        return

    def task():
        merger = PdfMerger()
        total = len(pdf_files)
        for i, pdf in enumerate(pdf_files):
            merger.append(pdf)
            progress_var.set((i + 1) / total * 100)
        merger.write(out)
        merger.close()
        messagebox.showinfo("Done", "PDFs merged successfully!")

    threading.Thread(target=task, daemon=True).start()

def show_preview(event=None):
    sel = listbox.curselection()
    if not sel:
        return
    path = pdf_files[sel[0]]

    if path in preview_cache:
        preview_label.config(image=preview_cache[path])
        preview_label.image = preview_cache[path]
        return

    try:
        img = convert_from_path(path, first_page=1, last_page=1)[0]
        img.thumbnail((300, 400))
        tk_img = ImageTk.PhotoImage(img)
        preview_cache[path] = tk_img
        preview_label.config(image=tk_img)
        preview_label.image = tk_img
    except Exception as e:
        messagebox.showerror("Preview Error", str(e))

# Drag reorder
drag_index = None
def drag_start(e):
    global drag_index
    drag_index = listbox.nearest(e.y)

def drag_release(e):
    global drag_index
    drop = listbox.nearest(e.y)
    if drag_index is not None and drop != drag_index:
        pdf_files.insert(drop, pdf_files.pop(drag_index))
        refresh_list()
        listbox.selection_set(drop)
    drag_index = None

# ---------------- GUI ---------------- #
app = TkinterDnD.Tk()
app.title("PDF Merger Tool")
app.geometry("900x550")
tb.Style("darkly")

app.drop_target_register(DND_FILES)
app.dnd_bind("<<Drop>>", on_drop)

main = tb.Frame(app, padding=10)
main.pack(fill=BOTH, expand=True)

# Left
left = tb.Frame(main)
left.pack(side=LEFT, fill=BOTH, expand=True)

listbox = tk.Listbox(left)
listbox.pack(fill=BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", show_preview)
listbox.bind("<Button-1>", drag_start)
listbox.bind("<ButtonRelease-1>", drag_release)

tb.Button(left, text="Add PDFs", command=add_pdfs, bootstyle=PRIMARY).pack(fill=X, pady=5)
tb.Button(left, text="Remove Selected", command=remove_selected, bootstyle=DANGER).pack(fill=X)

# Right
right = tb.Frame(main)
right.pack(side=RIGHT, fill=Y, padx=10)

preview_label = tk.Label(right)
preview_label.pack(pady=10)

progress_var = tk.DoubleVar()
progress = tb.Progressbar(
    right, variable=progress_var, maximum=100, bootstyle=SUCCESS
)
progress.pack(fill=X, pady=10)

tb.Button(
    right, text="Merge PDFs", command=merge_pdfs, bootstyle=SUCCESS
).pack(fill=X)

app.mainloop()
