import sys
import os
import re
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from tkinter import filedialog
import dns.resolver  # For domain MX record checks

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
root.title("Email Validation Tool")
root.geometry("720x680")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
email_var = tk.StringVar()
validation_result_var = tk.StringVar(value="Result: —")
email_history = []

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)
    email_entry.configure(background=bg, foreground=fg)

# =========================
# Email Validation Logic
# =========================
def is_valid_email_format(email):
    # Basic regex email validation
    regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(regex, email) is not None

def has_mx_record(domain):
    # Check if domain has MX records
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return bool(records)
    except Exception:
        return False

def validate_email():
    email = email_var.get().strip()
    if not email:
        messagebox.showwarning("Error", "Please enter an email address.")
        return

    set_status("Validating email...")
    threading.Thread(target=_validate_email_thread, args=(email,), daemon=True).start()

def _validate_email_thread(email):
    # Check format
    if not is_valid_email_format(email):
        validation_result_var.set("Result: ❌ Invalid format")
        set_status("Validation complete")
        return

    # Check MX record
    domain = email.split("@")[1]
    if has_mx_record(domain):
        validation_result_var.set("Result: ✅ Valid email")
    else:
        validation_result_var.set("Result: ⚠ Domain may not receive emails")

    add_to_history(email)
    set_status("Validation complete")

# =========================
# Email History
# =========================
def add_to_history(email):
    email_history.append(email)
    history_list.insert(tk.END, f"{len(email_history)} • {email}")

def export_history_txt():
    if not email_history:
        messagebox.showinfo("Empty History", "No emails to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Export Email History"
    )

    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Email Validation History\n")
            f.write("=" * 30 + "\n\n")
            for i, email in enumerate(email_history, 1):
                f.write(f"{i}. {email}\n")
        set_status("Email history exported")
        messagebox.showinfo("Export Successful", "Email history saved successfully.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=8)

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

ttk.Label(main, text="Email Validation Tool",
          font=("Segoe UI", 22, "bold")).pack()

email_entry = ttk.Entry(
    main, textvariable=email_var,
    font=("Segoe UI", 14), justify="center"
)
email_entry.pack(fill="x", pady=8)

ttk.Label(main, textvariable=validation_result_var,
          font=("Segoe UI", 12, "bold")).pack(pady=4)

# =========================
# Controls
# =========================
controls = ttk.Frame(main)
controls.pack(pady=8)

ttk.Button(controls, text="✅ Validate",
           command=validate_email,
           style="Action.TButton").pack(side="left", padx=4)

ttk.Button(controls, text="📤 Export History",
           command=export_history_txt,
           style="Action.TButton").pack(side="left", padx=4)

# =========================
# History Vault
# =========================
vault = ttk.LabelFrame(main, text="Email History Vault", padding=10)
vault.pack(fill="both", expand=True, pady=10)

history_list = tk.Listbox(vault, font=("Segoe UI", 10), height=10)
history_list.pack(fill="both", expand=True)

# =========================
# Options
# =========================
ttk.Checkbutton(main, text="Dark Mode",
                variable=dark_mode_var,
                command=toggle_theme).pack(pady=6)

# =========================
# Run App
# =========================
root.mainloop()
