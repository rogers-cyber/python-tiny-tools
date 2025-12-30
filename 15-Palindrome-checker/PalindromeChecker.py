import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sv_ttk

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Palindrome Checker Pro")
root.geometry("1000x720")

sv_ttk.set_theme("light")  # Default theme

# =========================
# Globals
# =========================
history = []
dark_mode_var = tk.BooleanVar(value=False)
ignore_case_var = tk.BooleanVar(value=True)
status_var = tk.StringVar(value="Ready")

# =========================
# Helpers
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def toggle_theme():
    style.theme_use("clam")
    if dark_mode_var.get():
        root.configure(bg="#2E2E2E")
        style.configure("TLabel", background="#2E2E2E", foreground="white")
        style.configure("TFrame", background="#2E2E2E")
        style.configure("TNotebook", background="#2E2E2E")
        style.configure("TNotebook.Tab", background="#444444", foreground="white")
        style.map("TNotebook.Tab", background=[("selected", "#90caf9")], foreground=[("selected", "black")])
    else:
        root.configure(bg="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="black")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TNotebook", background="#FFFFFF")
        style.configure("TNotebook.Tab", background="#e0e0e0", foreground="black")
        style.map("TNotebook.Tab", background=[("selected", "#90caf9")], foreground=[("selected", "black")])
    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

def clean_text(txt):
    if ignore_case_var.get():
        return ''.join(c.lower() for c in txt if c.isalnum())
    else:
        return ''.join(c for c in txt if c.isalnum())

# =========================
# Custom Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), foreground="white", background="#4CAF50", padding=8)
style.map("Action.TButton", background=[("active", "#45a049"), ("disabled", "#a5d6a7")])
style.configure("Replace.TButton", font=("Segoe UI", 11, "bold"), foreground="white", background="#2196F3", padding=8)
style.map("Replace.TButton", background=[("active", "#1976D2"), ("disabled", "#90caf9")])
style.configure("Tall.TCheckbutton", font=("Segoe UI", 11, "bold"), padding=6)

# =========================
# Status Bar
# =========================
ttk.Label(root, textvariable=status_var, anchor="w", font=("Segoe UI", 10)).pack(side=tk.BOTTOM, fill="x")

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

ttk.Label(dash_tab, text="Palindrome Checker Pro", font=("Segoe UI", 22, "bold")).pack(anchor="w")
ttk.Label(dash_tab, text="Check if your text, multiple entries, or file contents are palindromes.", font=("Segoe UI", 12)).pack(anchor="w", pady=(5,15))

# Features
features_frame = ttk.Frame(dash_tab)
features_frame.pack(fill="x", pady=10)

def create_feature_card(parent, title, desc):
    card = ttk.LabelFrame(parent, text=title, padding=15)
    ttk.Label(card, text=desc, wraplength=250, font=("Segoe UI", 10)).pack(anchor="w")
    return card

# First row
create_feature_card(features_frame, "📝 Multi-line Input", "Check multiple lines at once.").grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
create_feature_card(features_frame, "📂 File Input", "Load a text file and check each line.").grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
# Second row
create_feature_card(features_frame, "⚙️ Options", "Toggle ignore case and dark mode.").grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
create_feature_card(features_frame, "👀 History & Preview", "View results with visual history of all checks.").grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

features_frame.columnconfigure((0,1), weight=1)

# About Developer
about_frame = ttk.LabelFrame(dash_tab, text="About Developer", padding=15)
about_frame.pack(fill="x", pady=20)
ttk.Label(about_frame, text="Developed by MateTools\nWebsite: https://matetools.gumroad.com", font=("Segoe UI", 10)).pack(anchor="w")

# =========================
# Tool Tab
# =========================
tool_tab = ttk.Frame(tabs, padding=20)
tabs.add(tool_tab, text="🔧 Checker")

# Step 1: Input
input_card = ttk.LabelFrame(tool_tab, text="Step 1: Enter Texts or Load File", padding=15)
input_card.pack(fill="both", pady=10, expand=True)

text_input = scrolledtext.ScrolledText(input_card, font=("Consolas", 11), height=5)
text_input.pack(fill="both", expand=True)

# Load from file
def load_file():
    file_path = filedialog.askopenfilename(title="Select a text file", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        text_input.delete("1.0", tk.END)
        text_input.insert(tk.END, content)
        set_status(f"Loaded file: {os.path.basename(file_path)}")

ttk.Button(input_card, text="Load File", command=load_file, style="Action.TButton").pack(side="right", padx=5, pady=5)

# Step 2: Options
options_card = ttk.LabelFrame(tool_tab, text="Step 2: Options", padding=15)
options_card.pack(fill="x", pady=10)

ttk.Checkbutton(options_card, text="Ignore Case", variable=ignore_case_var, style="Tall.TCheckbutton").pack(side="left", padx=10)
ttk.Checkbutton(options_card, text="Dark Mode", variable=dark_mode_var, command=toggle_theme, style="Tall.TCheckbutton").pack(side="left", padx=10)

# Step 3: Results
preview_card = ttk.LabelFrame(tool_tab, text="Step 3: Results / History", padding=15)
preview_card.pack(fill="both", expand=True, pady=10)

preview_text = scrolledtext.ScrolledText(preview_card, font=("Consolas", 10), height=5)
preview_text.pack(fill="both", expand=True)

# Step 4: Actions
action_card = ttk.Frame(tool_tab, padding=15)
action_card.pack(fill="x", pady=10)

def check_palindromes():
    global history
    lines = text_input.get("1.0", tk.END).splitlines()
    if not any(line.strip() for line in lines):
        messagebox.showwarning("Warning", "Please enter text to check.")
        return

    for line in lines:
        cleaned = clean_text(line)
        result = cleaned == cleaned[::-1]
        history.append((line.strip(), result))
    update_preview()
    set_status(f"Checked {len(lines)} entries")

def update_preview():
    preview_text.delete("1.0", tk.END)
    for idx, (txt, result) in enumerate(reversed(history), 1):
        preview_text.insert(tk.END, f"{idx}. {txt} -> {'Palindrome ✅' if result else 'Not ❌'}\n")

ttk.Button(action_card, text="Check Palindromes", command=check_palindromes, style="Action.TButton").pack(side="left", padx=5)
ttk.Button(action_card, text="Clear History", command=lambda: (history.clear(), preview_text.delete('1.0', tk.END), set_status("History cleared")), style="Replace.TButton").pack(side="left", padx=5)

# =========================
# Run App
# =========================
root.mainloop()
