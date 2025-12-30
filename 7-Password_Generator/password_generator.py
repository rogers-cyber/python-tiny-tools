import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import random
import string
import sv_ttk
import threading
import time
import csv

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("SecurePass Desktop")
root.geometry("1200x800")
root.minsize(1200, 800)

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
history_data = []
clipboard_timer = None
vault_data = []  # In-memory vault for generated passwords

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI",11,"bold"), padding=8)
style.configure("TNotebook.Tab", padding=[10,5], font=("Segoe UI",11,"bold"))

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side="bottom", fill="x")
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    sv_ttk.set_theme("dark" if dark_mode_var.get() else "light")
    set_status(f"Theme: {'Dark' if dark_mode_var.get() else 'Light'}")

# =========================
# Notebook
# =========================
tabs = ttk.Notebook(root)
tabs.pack(expand=True, fill="both", padx=20, pady=20)

# =========================
# Dashboard Tab
# =========================
dash_tab = ttk.Frame(tabs, padding=20)
tabs.add(dash_tab, text="🏠 Dashboard")

ttk.Label(dash_tab, text="SecurePass Desktop", font=("Segoe UI", 22, "bold")).pack(anchor="w")
ttk.Label(dash_tab, text="Privacy-first offline password generator for everyday digital security.", font=("Segoe UI",12)).pack(anchor="w", pady=(5,15))

ttk.Label(dash_tab, text="Key Features:", font=("Segoe UI",14,"bold")).pack(anchor="w", pady=(10,5))

features_frame = ttk.Frame(dash_tab)
features_frame.pack(fill="x", pady=5)

def create_feature_card(parent, title, desc):
    card = ttk.LabelFrame(parent, text=title, padding=10)
    ttk.Label(card, text=desc, wraplength=250, font=("Segoe UI",10), justify="left").pack(anchor="w")
    return card

create_feature_card(features_frame, "🔑 Strong Passwords",
                    "Generate secure passwords with letters, numbers, symbols or mnemonic patterns.").grid(row=0,column=0,padx=10,pady=5,sticky="nsew")
create_feature_card(features_frame, "📋 Clipboard Auto-Clear",
                    "Copy passwords safely; clipboard auto-clears after 30 seconds.").grid(row=0,column=1,padx=10,pady=5,sticky="nsew")
create_feature_card(features_frame, "💾 Export History",
                    "Export all generated passwords to TXT or CSV without PIN.").grid(row=0,column=2,padx=10,pady=5,sticky="nsew")
create_feature_card(features_frame, "🎨 Dark Mode",
                    "Switch between light and dark themes for comfortable usage.").grid(row=0,column=3,padx=10,pady=5,sticky="nsew")
features_frame.columnconfigure((0,1,2,3), weight=1)

ttk.Label(dash_tab, text="About Developer:", font=("Segoe UI",12,"bold")).pack(anchor="w", pady=(15,0))
ttk.Label(dash_tab, text="MateTools – Focused on practical, secure, and user-friendly digital tools for daily life. \nWebsite: https://matetools.gumroad.com",
          font=("Segoe UI",10), wraplength=650, justify="left").pack(anchor="w")

# =========================
# Generator Tab
# =========================
tool_tab = ttk.Frame(tabs, padding=20)
tabs.add(tool_tab, text="🔑 Generator")

# ---------------- Options ----------------
options_frame = ttk.LabelFrame(tool_tab, text="Password Options", padding=15)
options_frame.pack(fill="x", pady=10)

def validate_length(new_value):
    if not new_value:  # empty string is allowed temporarily
        return True
    try:
        value = int(new_value)
        return 6 <= value <= 64
    except ValueError:
        return False

vcmd = (root.register(validate_length), "%P")
length_var = tk.IntVar(value=16)
ttk.Label(options_frame, text="Length").grid(row=0, column=0, sticky="w")
ttk.Spinbox(
    options_frame,
    from_=6,
    to=64,
    textvariable=length_var,
    width=10,
    validate="key",
    validatecommand=vcmd
).grid(row=0, column=1, padx=10)

upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
digit_var = tk.BooleanVar(value=True)
symbol_var = tk.BooleanVar(value=True)
mnemonic_var = tk.BooleanVar(value=False)

ttk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=upper_var).grid(row=1,column=0, sticky="w")
ttk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=lower_var).grid(row=1,column=1, sticky="w")
ttk.Checkbutton(options_frame, text="Numbers (0-9)", variable=digit_var).grid(row=2,column=0, sticky="w")
ttk.Checkbutton(options_frame, text="Symbols (!@#)", variable=symbol_var).grid(row=2,column=1, sticky="w")
ttk.Checkbutton(options_frame, text="Mnemonic-friendly", variable=mnemonic_var).grid(row=3,column=0, sticky="w")

# ---------------- Result ----------------
result_var = tk.StringVar()
show_password_var = tk.BooleanVar(value=True)

ttk.Label(tool_tab, text="Generated Password", font=("Segoe UI",12,"bold")).pack(anchor="w", pady=(15,5))
result_entry = ttk.Entry(tool_tab, textvariable=result_var, font=("Consolas",16), state="readonly")
result_entry.pack(fill="x")

def toggle_password_visibility():
    result_entry.config(show="" if show_password_var.get() else "*")
ttk.Checkbutton(tool_tab, text="Show password", variable=show_password_var, command=toggle_password_visibility).pack(anchor="w", pady=5)

# ---------------- Strength ----------------
strength_var = tk.StringVar(value="Strength: —")
strength_label = ttk.Label(tool_tab, textvariable=strength_var, font=("Segoe UI",11,"bold"))
strength_label.pack(anchor="w", pady=5)

def evaluate_strength(pwd):
    score=0
    if len(pwd)>=12: score+=1
    if any(c.isupper() for c in pwd): score+=1
    if any(c.islower() for c in pwd): score+=1
    if any(c.isdigit() for c in pwd): score+=1
    if any(c in string.punctuation for c in pwd): score+=1
    if score<=2: return "Weak ❌"
    elif score==3: return "Medium ⚠️"
    elif score==4: return "Strong ✅"
    else: return "Very Strong 🔒"

# =========================
# Password Logic
# =========================
def generate_password():
    if mnemonic_var.get():
        consonants="bcdfghjklmnpqrstvwxyz"
        vowels="aeiou"
        password="".join(random.choice(consonants if i%2==0 else vowels) for i in range(length_var.get()))
    else:
        charset=""
        if upper_var.get(): charset+=string.ascii_uppercase
        if lower_var.get(): charset+=string.ascii_lowercase
        if digit_var.get(): charset+=string.digits
        if symbol_var.get(): charset+=string.punctuation
        if not charset:
            messagebox.showerror("Error","Select at least one character type")
            return
        password="".join(random.choice(charset) for _ in range(length_var.get()))
    result_var.set(password)
    strength_var.set(f"Strength: {evaluate_strength(password)}")
    add_to_history(password)
    vault_data.append(password)
    set_status("Password generated")

def add_to_history(password):
    history_data.insert(0,password)
    del history_data[10:]
    history_text.config(state="normal")
    history_text.delete("1.0",tk.END)
    history_text.insert(tk.END,"\n".join(history_data))
    history_text.config(state="disabled")

# =========================
# Clipboard
# =========================
def clear_clipboard_after_delay():
    time.sleep(30)
    root.clipboard_clear()
    set_status("Clipboard cleared")

def copy_to_clipboard():
    pwd=result_var.get()
    if not pwd: return
    root.clipboard_clear()
    root.clipboard_append(pwd)
    set_status("Password copied (auto-clears in 30s)")
    threading.Thread(target=clear_clipboard_after_delay, daemon=True).start()

# =========================
# Export
# =========================
def export_passwords():
    if not vault_data:
        messagebox.showwarning("Warning","No passwords to export")
        return
    file_path=filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file","*.txt"),("CSV file","*.csv")])
    if not file_path: return
    if file_path.endswith(".txt"):
        with open(file_path,"w") as f: f.write("\n".join(vault_data))
    else:
        with open(file_path,"w",newline="") as f:
            writer=csv.writer(f)
            for pwd in vault_data: writer.writerow([pwd])
    set_status(f"Passwords exported to {file_path}")
    messagebox.showinfo("Exported",f"Passwords exported to {file_path}")

# =========================
# Buttons Row
# =========================
btn_frame = ttk.Frame(tool_tab)
btn_frame.pack(pady=15)

ttk.Button(btn_frame,text="🔑 Generate",command=generate_password,style="Action.TButton").grid(row=0,column=0,padx=5)
ttk.Button(btn_frame,text="📋 Copy",command=copy_to_clipboard,style="Action.TButton").grid(row=0,column=1,padx=5)
ttk.Button(btn_frame,text="🧹 Clear",command=lambda: result_var.set(""),style="Action.TButton").grid(row=0,column=2,padx=5)
ttk.Button(btn_frame,text="💾 Export",command=export_passwords,style="Action.TButton").grid(row=0,column=3,padx=5)

# =========================
# History
# =========================
history_frame = ttk.LabelFrame(tool_tab, text="Temporary History (Auto-Clears)", padding=10)
history_frame.pack(fill="both", expand=False, pady=10)  # don't expand fully

history_text = scrolledtext.ScrolledText(history_frame, font=("Consolas", 11), state="disabled", height=8)
history_text.pack(fill="both", expand=True)

# =========================
# Bottom Controls
# =========================
ttk.Checkbutton(root,text="Dark Mode",variable=dark_mode_var,command=toggle_theme).pack(side="bottom",pady=5)

# =========================
# Auto-clear History Timer
# =========================
def auto_clear_history():
    while True:
        time.sleep(600)  # Clear every 10 minutes
        history_data.clear()
        vault_data.clear()
        history_text.config(state="normal")
        history_text.delete("1.0",tk.END)
        history_text.config(state="disabled")
        set_status("Temporary history cleared automatically")

threading.Thread(target=auto_clear_history,daemon=True).start()

# =========================
# Run
# =========================
root.mainloop()
