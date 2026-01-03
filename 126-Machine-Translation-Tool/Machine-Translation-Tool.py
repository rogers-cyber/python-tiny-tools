import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from dataclasses import dataclass
from typing import List
import csv
import os

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from googletrans import Translator, LANGUAGES
from tkinterdnd2 import TkinterDnD, DND_FILES

# ---------------- GLOBAL STATE ---------------- #
all_translations: List["TranslationResult"] = []
translator = Translator()

# ---------------- DATA STRUCTURE ---------------- #
@dataclass
class TranslationResult:
    original_text: str
    translated_text: str
    src_lang: str
    dest_lang: str

# ---------------- HELPERS ---------------- #
def cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text

def copy_to_clipboard(text: str):
    app.clipboard_clear()
    app.clipboard_append(text)
    messagebox.showinfo("Copied", "Translation copied to clipboard")

# ---------------- DRAG & DROP ---------------- #
def drop_text_file(event):
    files = app.tk.splitlist(event.data)
    for file in files:
        if file.lower().endswith(".txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                text_entry.delete("1.0", END)
                text_entry.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("File Error", str(e))

# ---------------- EXPORT ---------------- #
def export_translations(fmt: str):
    if not all_translations:
        messagebox.showwarning("No Data", "No translations to export")
        return

    filetypes = [("Text File", "*.txt")] if fmt == "txt" else [("CSV File", "*.csv")]
    path = filedialog.asksaveasfilename(defaultextension=f".{fmt}", filetypes=filetypes)

    if not path:
        return

    try:
        if fmt == "txt":
            with open(path, "w", encoding="utf-8") as f:
                for r in all_translations:
                    f.write(f"Source ({cap(LANGUAGES[r.src_lang])})\n")
                    f.write(f"Original: {r.original_text}\n")
                    f.write(f"Target ({cap(LANGUAGES[r.dest_lang])})\n")
                    f.write(f"Translated: {r.translated_text}\n")
                    f.write("-" * 60 + "\n")
        else:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Source Language", "Target Language", "Original", "Translated"])
                for r in all_translations:
                    writer.writerow([
                        cap(LANGUAGES[r.src_lang]),
                        cap(LANGUAGES[r.dest_lang]),
                        r.original_text,
                        r.translated_text
                    ])

        messagebox.showinfo("Exported", "Translations exported successfully")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

# ---------------- TRANSLATION ---------------- #
def fetch_translations(text, langs):
    results = []
    try:
        detected = translator.detect(text).lang
        for lang in langs:
            t = translator.translate(text, src=detected, dest=lang)
            results.append(
                TranslationResult(text, t.text, detected, lang)
            )
    except Exception as e:
        messagebox.showerror("Translation Error", str(e))
    return results

# ---------------- DISPLAY ---------------- #
def display_results():
    for w in results_frame.winfo_children():
        w.destroy()

    for r in all_translations:
        card = tb.Frame(results_frame, padding=15)
        card.pack(fill=X, pady=8)

        tb.Label(
            card,
            text=f"Original ({cap(LANGUAGES[r.src_lang])})",
            font=("Segoe UI", 11)
        ).pack(anchor=W)

        tb.Label(
            card,
            text=r.original_text,
            wraplength=900
        ).pack(anchor=W)

        row = tb.Frame(card)
        row.pack(fill=X, pady=5)

        tb.Label(
            row,
            text=f"{cap(LANGUAGES[r.dest_lang])}: {r.translated_text}",
            font=("Segoe UI", 14, "bold"),
            wraplength=800
        ).pack(side=LEFT)

        tb.Button(
            row,
            text="📋 Copy",
            command=lambda t=r.translated_text: copy_to_clipboard(t)
        ).pack(side=LEFT, padx=10)

# ---------------- SEARCH FILTER ---------------- #
def filter_languages(*_):
    query = search_var.get().lower()
    lang_listbox.delete(0, END)
    for lang in all_language_names:
        if query in lang.lower():
            lang_listbox.insert(END, lang)

# ---------------- RUN TRANSLATION ---------------- #
def perform_translation():
    text = text_entry.get("1.0", END).strip()
    selections = lang_listbox.curselection()

    if not text or not selections:
        messagebox.showwarning("Input Required", "Enter text and select languages")
        return

    langs = []
    for i in selections:
        name = lang_listbox.get(i)
        for code, lang in LANGUAGES.items():
            if cap(lang) == name:
                langs.append(code)

    threading.Thread(
        target=run_translation,
        args=(text, langs),
        daemon=True
    ).start()

def run_translation(text, langs):
    global all_translations
    all_translations = fetch_translations(text, langs)
    app.after(0, display_results)

# ---------------- UI ---------------- #
app = TkinterDnD.Tk()
app.title("🌐 Machine Translation Tool")
app.geometry("1000x780")

style = tb.Style("flatly")

top = tb.Frame(app, padding=15)
top.pack(fill=X)

tb.Label(
    top,
    text="🌐 Machine Translation Tool",
    font=("Segoe UI", 18, "bold")
).pack(anchor=W)

text_entry = tk.Text(top, height=5, font=("Segoe UI", 12))
text_entry.pack(fill=X, pady=8)

# Drag & Drop
text_entry.drop_target_register(DND_FILES)
text_entry.dnd_bind("<<Drop>>", drop_text_file)

tb.Label(top, text="Search Languages:", font=("Segoe UI", 11)).pack(anchor=W)

search_var = tk.StringVar()
search_var.trace_add("write", filter_languages)

search_entry = tb.Entry(top, textvariable=search_var)
search_entry.pack(fill=X, pady=5)

lang_listbox = tk.Listbox(top, selectmode=MULTIPLE, height=8)
lang_listbox.pack(fill=X)

all_language_names = sorted(cap(v) for v in LANGUAGES.values())
for l in all_language_names:
    lang_listbox.insert(END, l)

btn_row = tb.Frame(top)
btn_row.pack(fill=X, pady=5)

tb.Button(btn_row, text="Translate", bootstyle="success", command=perform_translation).pack(side=LEFT)
tb.Button(btn_row, text="Export TXT", command=lambda: export_translations("txt")).pack(side=LEFT, padx=5)

# ---------------- RESULTS (SCROLL ONLY) ---------------- #
results_container = tb.Frame(app)
results_container.pack(fill=BOTH, expand=True)

canvas = tk.Canvas(results_container)
scroll = tb.Scrollbar(results_container, command=canvas.yview)
results_frame = tb.Frame(canvas)

canvas.create_window((0, 0), window=results_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll.set)

results_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.pack(side=LEFT, fill=BOTH, expand=True)
scroll.pack(side=RIGHT, fill=Y)

app.mainloop()
