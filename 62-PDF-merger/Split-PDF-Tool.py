import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image, ImageTk

# ---------------- GLOBALS ---------------- #
pdf_path = None
pages = []
preview_cache = {}
drag_index = None

# ---------------- CORE FUNCTIONS ---------------- #
def load_pdf(path):
    global pdf_path, pages
    pdf_path = path
    pages.clear()
    listbox.delete(0, tk.END)

    reader = PdfReader(path)
    for i in range(len(reader.pages)):
        pages.append(i)
        listbox.insert(tk.END, f"Page {i+1}")

def on_drop(event):
    files = app.tk.splitlist(event.data)
    for f in files:
        f = f.strip("{}")
        if f.lower().endswith(".pdf"):
            load_pdf(f)
            break

def add_pdf():
    f = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if f:
        load_pdf(f)

def refresh_list():
    listbox.delete(0, tk.END)
    for p in pages:
        listbox.insert(tk.END, f"Page {p+1}")

# ---------------- PAGE PREVIEW ---------------- #
def show_preview(event=None):
    sel = listbox.curselection()
    if not sel or not pdf_path:
        return

    page_num = pages[sel[0]]
    key = (pdf_path, page_num)

    if key in preview_cache:
        preview_label.config(image=preview_cache[key])
        preview_label.image = preview_cache[key]
        return

    img = convert_from_path(
        pdf_path, first_page=page_num+1, last_page=page_num+1
    )[0]
    img.thumbnail((300, 400))
    tk_img = ImageTk.PhotoImage(img)
    preview_cache[key] = tk_img
    preview_label.config(image=tk_img)
    preview_label.image = tk_img

# ---------------- DRAG REORDER ---------------- #
def drag_start(e):
    global drag_index
    drag_index = listbox.nearest(e.y)

def drag_release(e):
    global drag_index
    drop = listbox.nearest(e.y)
    if drag_index is not None and drop != drag_index:
        pages.insert(drop, pages.pop(drag_index))
        refresh_list()
        listbox.selection_set(drop)
    drag_index = None

# ---------------- ROTATE ---------------- #
def rotate_selected(angle):
    sel = listbox.curselection()
    if not sel:
        return
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in pages:
        page = reader.pages[i]
        if i in [pages[s] for s in sel]:
            page.rotate(angle)
        writer.add_page(page)

    save_output(writer)

# ---------------- SPLIT ---------------- #
def split_pdf():
    if not pdf_path:
        return

    start = simple_input("Start page (1-based)")
    end = simple_input("End page")

    if not start or not end:
        return

    start, end = int(start)-1, int(end)-1

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in range(start, end+1):
        writer.add_page(reader.pages[i])

    save_output(writer)

# ---------------- SAVE ---------------- #
def save_output(writer):
    out = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]
    )
    if not out:
        return
    with open(out, "wb") as f:
        writer.write(f)
    messagebox.showinfo("Success", "Operation completed!")

# ---------------- INPUT DIALOG ---------------- #
def simple_input(title):
    popup = tk.Toplevel(app)
    popup.title(title)
    popup.geometry("250x100")
    val = tk.StringVar()

    tb.Label(popup, text=title).pack(pady=5)
    entry = tb.Entry(popup, textvariable=val)
    entry.pack(pady=5)
    entry.focus()

    tb.Button(popup, text="OK", command=popup.destroy).pack()
    popup.wait_window()
    return val.get()

# ---------------- GUI ---------------- #
app = TkinterDnD.Tk()
app.title("Advanced PDF Tool")
app.geometry("1000x600")
tb.Style("darkly")

app.drop_target_register(DND_FILES)
app.dnd_bind("<<Drop>>", on_drop)

main = tb.Frame(app, padding=10)
main.pack(fill=BOTH, expand=True)

# Left panel
left = tb.Frame(main)
left.pack(side=LEFT, fill=BOTH, expand=True)

listbox = tk.Listbox(left)
listbox.pack(fill=BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", show_preview)
listbox.bind("<Button-1>", drag_start)
listbox.bind("<ButtonRelease-1>", drag_release)

tb.Button(left, text="Load PDF", command=add_pdf, bootstyle=PRIMARY).pack(fill=X, pady=5)

# Right panel
right = tb.Frame(main)
right.pack(side=RIGHT, fill=Y, padx=10)

preview_label = tk.Label(right)
preview_label.pack(pady=10)

tb.Button(right, text="Rotate 90°", command=lambda: rotate_selected(90), bootstyle=WARNING).pack(fill=X, pady=2)
tb.Button(right, text="Rotate 180°", command=lambda: rotate_selected(180), bootstyle=WARNING).pack(fill=X, pady=2)
tb.Button(right, text="Rotate 270°", command=lambda: rotate_selected(270), bootstyle=WARNING).pack(fill=X, pady=2)

tb.Separator(right).pack(fill=X, pady=5)

tb.Button(right, text="Split PDF", command=split_pdf, bootstyle=DANGER).pack(fill=X)

app.mainloop()
