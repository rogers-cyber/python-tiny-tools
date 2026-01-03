import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PyPDF2 import PdfMerger

# ---------------- GLOBALS ---------------- #
pdf_files = []

# ---------------- FUNCTIONS ---------------- #
def add_pdfs():
    files = filedialog.askopenfilenames(
        title="Select PDF files",
        filetypes=[("PDF Files", "*.pdf")]
    )
    for f in files:
        if f not in pdf_files:
            pdf_files.append(f)
            listbox.insert(tk.END, os.path.basename(f))

def remove_selected():
    sel = listbox.curselection()
    if not sel:
        return
    index = sel[0]
    pdf_files.pop(index)
    listbox.delete(index)

def move_up():
    sel = listbox.curselection()
    if not sel or sel[0] == 0:
        return
    i = sel[0]
    pdf_files[i-1], pdf_files[i] = pdf_files[i], pdf_files[i-1]
    refresh_list()
    listbox.selection_set(i-1)

def move_down():
    sel = listbox.curselection()
    if not sel or sel[0] == len(pdf_files)-1:
        return
    i = sel[0]
    pdf_files[i+1], pdf_files[i] = pdf_files[i], pdf_files[i+1]
    refresh_list()
    listbox.selection_set(i+1)

def refresh_list():
    listbox.delete(0, tk.END)
    for f in pdf_files:
        listbox.insert(tk.END, os.path.basename(f))

def merge_pdfs():
    if not pdf_files:
        messagebox.showwarning("No Files", "Add PDF files first.")
        return

    output_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
        title="Save merged PDF as"
    )
    if not output_path:
        return

    try:
        merger = PdfMerger()
        for pdf in pdf_files:
            merger.append(pdf)
        merger.write(output_path)
        merger.close()
        messagebox.showinfo("Success", "PDFs merged successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Drag & Drop reorder
drag_data = None
def on_drag_start(event):
    global drag_data
    drag_data = listbox.nearest(event.y)

def on_drag_release(event):
    global drag_data
    if drag_data is None:
        return
    drop_index = listbox.nearest(event.y)
    if drop_index != drag_data:
        pdf_files.insert(drop_index, pdf_files.pop(drag_data))
        refresh_list()
        listbox.selection_set(drop_index)
    drag_data = None

# ---------------- GUI ---------------- #
app = tb.Window(
    title="PDF Merger Tool",
    themename="darkly",
    size=(700, 450)
)

main_frame = tb.Frame(app)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Listbox
listbox = tk.Listbox(main_frame, height=15)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
listbox.bind("<Button-1>", on_drag_start)
listbox.bind("<ButtonRelease-1>", on_drag_release)

# Controls
control_frame = tb.Frame(main_frame)
control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

tb.Button(control_frame, text="Add PDFs", bootstyle="primary", command=add_pdfs).pack(fill=tk.X, pady=5)
tb.Button(control_frame, text="Remove Selected", bootstyle="danger", command=remove_selected).pack(fill=tk.X, pady=5)
tb.Button(control_frame, text="Move Up", bootstyle="secondary", command=move_up).pack(fill=tk.X, pady=5)
tb.Button(control_frame, text="Move Down", bootstyle="secondary", command=move_down).pack(fill=tk.X, pady=5)
tb.Separator(control_frame).pack(fill=tk.X, pady=10)
tb.Button(control_frame, text="Merge PDFs", bootstyle="success", command=merge_pdfs).pack(fill=tk.X, pady=5)

app.mainloop()
