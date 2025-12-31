import sys
import os
import random
import string
import math
import time
import hashlib
import threading
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from tkinter import filedialog

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Password Security Suite")
root.geometry("720x680")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
show_password_var = tk.BooleanVar(value=False)

password_var = tk.StringVar()
entropy_var = tk.StringVar(value="Entropy: — bits")
crack_time_var = tk.StringVar(value="Time to crack: —")

length_var = tk.IntVar(value=14)
use_upper = tk.BooleanVar(value=True)
use_lower = tk.BooleanVar(value=True)
use_digits = tk.BooleanVar(value=True)
use_symbols = tk.BooleanVar(value=True)

password_history = []

CLIPBOARD_CLEAR_SECONDS = 15
GUESSES_PER_SECOND = 1e10  # realistic offline attack

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)
    password_entry.configure(background=bg, foreground=fg)

# =========================
# Core Security Logic
# =========================
def calculate_entropy(pwd):
    pool = 0
    if any(c.islower() for c in pwd): pool += 26
    if any(c.isupper() for c in pwd): pool += 26
    if any(c.isdigit() for c in pwd): pool += 10
    if any(c in string.punctuation for c in pwd): pool += len(string.punctuation)
    return round(len(pwd) * math.log2(pool), 2) if pool else 0

def estimate_crack_time(entropy):
    guesses = 2 ** entropy
    seconds = guesses / GUESSES_PER_SECOND
    units = [("years", 31536000), ("days", 86400), ("hours", 3600), ("minutes", 60)]
    for name, div in units:
        if seconds >= div:
            return f"{seconds/div:.2f} {name}"
    return f"{seconds:.2f} seconds"

def update_strength_visuals(entropy):
    progress["value"] = min(entropy, 100)

    if entropy < 40:
        color, label = "red", "Weak ❌"
    elif entropy < 60:
        color, label = "orange", "Medium ⚠️"
    elif entropy < 80:
        color, label = "green", "Strong ✅"
    else:
        color, label = "purple", "Very Strong 🔥"

    style.configure("Entropy.Horizontal.TProgressbar", background=color)
    strength_label.config(text=label)

def evaluate_password(pwd):
    entropy = calculate_entropy(pwd)
    entropy_var.set(f"Entropy: {entropy} bits")
    crack_time_var.set(f"Time to crack: {estimate_crack_time(entropy)}")
    update_strength_visuals(entropy)

def generate_password():
    chars = ""
    if use_upper.get(): chars += string.ascii_uppercase
    if use_lower.get(): chars += string.ascii_lowercase
    if use_digits.get(): chars += string.digits
    if use_symbols.get(): chars += string.punctuation
    if not chars:
        messagebox.showwarning("Error", "Select at least one character type.")
        return

    pwd = "".join(random.choice(chars) for _ in range(length_var.get()))
    password_var.set(pwd)
    evaluate_password(pwd)
    add_to_history(pwd)
    check_breach(pwd)
    set_status("Password generated")

# =========================
# Password History
# =========================
def add_to_history(pwd):
    password_history.append(pwd)
    history_list.insert(tk.END, f"{len(password_history)} • {pwd}")

# =========================
# Clipboard Handling
# =========================
def copy_password():
    pwd = password_var.get()
    if not pwd: return
    root.clipboard_clear()
    root.clipboard_append(pwd)
    set_status("Copied to clipboard (auto-clear enabled)")
    threading.Thread(target=clear_clipboard_timer, daemon=True).start()

def clear_clipboard_timer():
    time.sleep(CLIPBOARD_CLEAR_SECONDS)
    root.clipboard_clear()
    set_status("Clipboard cleared")

# =========================
# Export Password TXT
# =========================
def export_history_txt():
    if not password_history:
        messagebox.showinfo("Empty Vault", "No passwords to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Export Password History"
    )

    if not file_path:
        return  # user cancelled

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Password History Vault\n")
            f.write("=" * 30 + "\n\n")
            for i, pwd in enumerate(password_history, 1):
                f.write(f"{i}. {pwd}\n")

        set_status("Password history exported")
        messagebox.showinfo("Export Successful", "Password history saved securely.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

# =========================
# Password Visibility
# =========================
def toggle_password_visibility():
    password_entry.config(show="" if show_password_var.get() else "•")

# =========================
# HIBP Breach Check (k-Anonymity)
# =========================
def check_breach(pwd):
    sha1 = hashlib.sha1(pwd.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    try:
        res = requests.get(
            f"https://api.pwnedpasswords.com/range/{prefix}",
            timeout=5
        )
        for line in res.text.splitlines():
            if suffix in line:
                messagebox.showwarning(
                    "⚠ Breach Found",
                    "This password has appeared in known data breaches!"
                )
                set_status("Breach detected")
                return
        set_status("Password not found in breaches")
    except Exception:
        set_status("Breach check failed (offline)")

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=8)
style.configure("Entropy.Horizontal.TProgressbar", thickness=12)

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill="x")

# =========================
# UI Layout
# =========================
main = ttk.Frame(root, padding=20)
main.pack(expand=True, fill="both")

ttk.Label(main, text="Password Security Suite",
          font=("Segoe UI", 22, "bold")).pack()

password_entry = ttk.Entry(
    main, textvariable=password_var,
    font=("Segoe UI", 14), justify="center", show="•"
)
password_entry.pack(fill="x", pady=8)

ttk.Checkbutton(main, text="Show Password",
                variable=show_password_var,
                command=toggle_password_visibility).pack()

ttk.Label(main, textvariable=entropy_var,
          font=("Segoe UI", 11, "bold")).pack()

ttk.Label(main, textvariable=crack_time_var,
          font=("Segoe UI", 10)).pack()

strength_label = ttk.Label(main, text="—",
                           font=("Segoe UI", 12, "bold"))
strength_label.pack(pady=4)

progress = ttk.Progressbar(
    main, style="Entropy.Horizontal.TProgressbar",
    maximum=100, length=420
)
progress.pack(pady=8)

# =========================
# Controls
# =========================
controls = ttk.Frame(main)
controls.pack(pady=8)

ttk.Button(controls, text="🔐 Generate",
           command=generate_password,
           style="Action.TButton").pack(side="left", padx=4)

ttk.Button(controls, text="📋 Copy",
           command=copy_password,
           style="Action.TButton").pack(side="left", padx=4)

ttk.Button(controls, text="📤 Export to TXT",
           command=export_history_txt,
           style="Action.TButton").pack(side="left", padx=4)

# =========================
# History Vault
# =========================
vault = ttk.LabelFrame(main, text="Password History Vault", padding=10)
vault.pack(fill="both", expand=True, pady=10)

history_list = tk.Listbox(vault, font=("Segoe UI", 10), height=6)
history_list.pack(fill="both", expand=True)

# =========================
# Options
# =========================
options = ttk.LabelFrame(main, text="Password Options", padding=10)
options.pack(fill="x", pady=8)

ttk.Label(options, text="Length:").grid(row=0, column=0)
ttk.Spinbox(options, from_=6, to=64,
            textvariable=length_var, width=6).grid(row=0, column=1)

ttk.Checkbutton(options, text="Uppercase", variable=use_upper).grid(row=1, column=0)
ttk.Checkbutton(options, text="Lowercase", variable=use_lower).grid(row=1, column=1)
ttk.Checkbutton(options, text="Numbers", variable=use_digits).grid(row=2, column=0)
ttk.Checkbutton(options, text="Symbols", variable=use_symbols).grid(row=2, column=1)

ttk.Checkbutton(main, text="Dark Mode",
                variable=dark_mode_var,
                command=toggle_theme).pack(pady=6)

# =========================
# Run App
# =========================
root.mainloop()
