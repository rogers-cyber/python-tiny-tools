import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import random

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def generate_easy_code():
    prefixes = ["go", "url", "link", "up", "web"]
    prefix = random.choice(prefixes)
    number = random.randint(10, 999)
    return f"{prefix}{number}"

# =========================
# Storage
# =========================
STORAGE_FILE = resource_path("short_urls.json")
if os.path.exists(STORAGE_FILE):
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        url_mapping = json.load(f)
else:
    url_mapping = {}

def save_mapping():
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(url_mapping, f, indent=4)
    update_url_list()

# =========================
# Core Logic
# =========================
def shorten_url():
    original = url_var.get().strip()
    if not original:
        messagebox.showwarning("Input Required", "Enter a URL to shorten.")
        return

    for code, url in url_mapping.items():
        if url == original:
            short_var.set(code)
            set_status("URL already shortened.")
            return

    code = generate_easy_code()
    while code in url_mapping:
        code = generate_easy_code()

    url_mapping[code] = original
    save_mapping()
    short_var.set(code)
    set_status("URL shortened successfully.")

def expand_url():
    code = short_var.get().strip()
    if not code:
        messagebox.showwarning("Input Required", "Enter a short code to expand.")
        return

    original = url_mapping.get(code)
    if original:
        url_var.set(original)
        set_status("URL expanded successfully.")
    else:
        messagebox.showerror("Not Found", "Short code does not exist.")

def copy_to_clipboard(entry_var):
    root.clipboard_clear()
    root.clipboard_append(entry_var.get())
    set_status("Copied to clipboard!")

# =========================
# URL List Display
# =========================
def update_url_list():
    for widget in list_frame_inner.winfo_children():
        widget.destroy()

    for i, (code, url) in enumerate(url_mapping.items(), 1):
        ttk.Label(
            list_frame_inner,
            text=f"{i}. {code} → {url}",
            font=("Segoe UI", 10),
            anchor="w"
        ).pack(fill="x", padx=5, pady=2)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Local URL Shortener")
root.geometry("1100x650")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
url_var = tk.StringVar()
short_var = tk.StringVar()
dark_mode_var = tk.BooleanVar(value=False)

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    style.theme_use("clam")
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"

    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)

    for entry in [url_entry, short_entry]:
        entry.configure(
            bg="#1e1e1e" if dark_mode_var.get() else "white",
            fg="white" if dark_mode_var.get() else "black",
            insertbackground="white" if dark_mode_var.get() else "black"
        )

    update_url_list()
    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Action.TButton",
    font=("Segoe UI", 11, "bold"),
    foreground="white",
    background="#4CAF50",
    padding=8
)
style.map("Action.TButton", background=[("active", "#45a049")])

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill="x")

# =========================
# Main UI
# =========================
main = ttk.Frame(root, padding=20)
main.pack(expand=True, fill="both")

ttk.Label(main, text="Local URL Shortener", font=("Segoe UI", 22, "bold")).pack()
ttk.Label(main, text="Shorten URLs locally without internet", font=("Segoe UI", 11)).pack(pady=(0, 10))

# =========================
# URL Input
# =========================
url_frame = ttk.LabelFrame(main, text="Original URL", padding=10)
url_frame.pack(fill="x", pady=5)

url_entry = tk.Entry(url_frame, textvariable=url_var, font=("Segoe UI", 12))
url_entry.pack(fill="x", padx=5, pady=5)

# =========================
# Short Code
# =========================
short_frame = ttk.LabelFrame(main, text="Short Code", padding=10)
short_frame.pack(fill="x", pady=5)

short_entry = tk.Entry(short_frame, textvariable=short_var, font=("Segoe UI", 12))
short_entry.pack(fill="x", padx=5, pady=5)

# =========================
# Actions
# =========================
actions = ttk.Frame(main)
actions.pack(pady=10)

ttk.Button(actions, text="🔗 Shorten", command=shorten_url, style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="🔍 Expand", command=expand_url, style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="📋 Copy URL", command=lambda: copy_to_clipboard(url_var), style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="📋 Copy Code", command=lambda: copy_to_clipboard(short_var), style="Action.TButton").pack(side="left", padx=6)
ttk.Checkbutton(actions, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(side="left", padx=14)

# =========================
# Stored URLs List (FIXED)
# =========================
list_frame_outer = ttk.LabelFrame(main, text="Stored URLs", padding=10)
list_frame_outer.pack(fill="both", pady=10, expand=True)

# Canvas (FIX)
list_frame_canvas = tk.Canvas(list_frame_outer)
list_frame_canvas.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(list_frame_outer, orient="vertical", command=list_frame_canvas.yview)
scrollbar.pack(side="right", fill="y")

list_frame_canvas.configure(yscrollcommand=scrollbar.set)

list_frame_inner = ttk.Frame(list_frame_canvas)
list_frame_canvas.create_window((0, 0), window=list_frame_inner, anchor="nw")

def on_frame_configure(event):
    list_frame_canvas.configure(scrollregion=list_frame_canvas.bbox("all"))

list_frame_inner.bind("<Configure>", on_frame_configure)

def on_mousewheel(event):
    list_frame_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

list_frame_canvas.bind_all("<MouseWheel>", on_mousewheel)

update_url_list()

# =========================
# Run App
# =========================
root.mainloop()
