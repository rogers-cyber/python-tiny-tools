import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sv_ttk

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
root.title("Binary → Decimal Converter Pro")
root.geometry("1200x680")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
binary_var = tk.StringVar()
decimal_var = tk.StringVar(value="0")
batch_list = []
stats_vars = {
    "total_binaries": tk.StringVar(value="0"),
    "valid": tk.StringVar(value="0"),
    "invalid": tk.StringVar(value="0"),
    "sum": tk.StringVar(value="0"),
}

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

    input_entry.configure(
        bg="#1e1e1e" if dark_mode_var.get() else "white",
        fg="white" if dark_mode_var.get() else "black",
        insertbackground="white" if dark_mode_var.get() else "black"
    )

    batch_text.configure(
        bg="#1e1e1e" if dark_mode_var.get() else "white",
        fg="white" if dark_mode_var.get() else "black",
        insertbackground="white" if dark_mode_var.get() else "black"
    )

    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Core Logic
# =========================
def convert_single_binary():
    bin_str = binary_var.get().strip()
    if not bin_str:
        decimal_var.set("0")
        set_status("Enter a binary number")
        return

    if not all(c in "01" for c in bin_str):
        decimal_var.set("Error")
        set_status("Invalid binary number")
        return

    decimal_var.set(str(int(bin_str, 2)))
    set_status(f"Converted {bin_str} → {decimal_var.get()}")

def convert_batch():
    content = batch_text.get("1.0", tk.END).strip().splitlines()
    batch_list.clear()
    valid_count = 0
    invalid_count = 0
    total_sum = 0
    results = []

    for line in content:
        line = line.strip()
        if not line:
            continue
        if all(c in "01" for c in line):
            dec = int(line, 2)
            results.append(f"{line} → {dec}")
            valid_count += 1
            total_sum += dec
            batch_list.append((line, dec))
        else:
            results.append(f"{line} → Invalid")
            invalid_count += 1
            batch_list.append((line, "Invalid"))

    batch_text.delete("1.0", tk.END)
    batch_text.insert("1.0", "\n".join(results))

    stats_vars["total_binaries"].set(len(content))
    stats_vars["valid"].set(valid_count)
    stats_vars["invalid"].set(invalid_count)
    stats_vars["sum"].set(total_sum)

    set_status("Batch conversion completed")

def delayed_single_convert(event=None):
    threading.Timer(0.1, convert_single_binary).start()

def delayed_batch_convert(event=None):
    threading.Timer(0.2, convert_batch).start()

# =========================
# File Operations
# =========================
def open_file():
    path = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            batch_text.delete("1.0", tk.END)
            batch_text.insert("1.0", f.read())
        convert_batch()
        set_status(f"Loaded: {os.path.basename(path)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_file():
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(batch_text.get("1.0", tk.END))
        set_status(f"Saved to {path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_all():
    if messagebox.askyesno("Clear", "Clear all inputs and outputs?"):
        binary_var.set("")
        decimal_var.set("0")
        batch_text.delete("1.0", tk.END)
        for key in stats_vars:
            stats_vars[key].set("0")
        set_status("Cleared all inputs and outputs")

# =========================
# Help Window
# =========================
def show_help():
    win = tk.Toplevel(root)
    win.title("Binary → Decimal Converter Pro - Help")
    win.geometry("500x400")
    win.configure(bg="#2e2e2e")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    frame = tk.Frame(win, bg="#2e2e2e")
    frame.pack(fill="both", expand=True, padx=12, pady=12)

    text = tk.Text(
        frame,
        bg="#2e2e2e",
        fg="#f0f0f0",
        font=("Segoe UI", 11),
        wrap="word",
        borderwidth=0
    )
    text.pack(fill="both", expand=True)

    help_text = """💻 Binary → Decimal Converter Pro

• Single binary input → decimal output
• Batch conversion: multiple binaries, one per line
• Automatic detection of invalid binaries
• Live statistics: total, valid, invalid, sum of decimals
• Open/save .txt files for batch processing
• Clear all inputs and outputs with one click
• Dark Mode toggle for comfortable viewing

Built with Python & Tkinter
"""
    text.insert("1.0", help_text)
    text.config(state="disabled")

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

ttk.Label(main, text="Binary → Decimal Converter Pro", font=("Segoe UI", 20, "bold")).pack()
ttk.Label(main, text="Single & Batch Conversion Tool", font=("Segoe UI", 11)).pack(pady=(0, 10))

# =========================
# Single Conversion Frame
# =========================
single_frame = ttk.LabelFrame(main, text="Single Conversion", padding=12)
single_frame.pack(fill="x", pady=6)

ttk.Label(single_frame, text="Binary Input:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
input_entry = ttk.Entry(single_frame, textvariable=binary_var, font=("Segoe UI", 12))
input_entry.pack(fill="x", pady=4)
input_entry.bind("<KeyRelease>", delayed_single_convert)

ttk.Label(single_frame, text="Decimal Output:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8,0))
ttk.Label(single_frame, textvariable=decimal_var, font=("Segoe UI", 12, "bold")).pack(anchor="w")

# =========================
# Batch Conversion Frame
# =========================
batch_frame = ttk.LabelFrame(main, text="Batch Conversion", padding=12)
batch_frame.pack(fill="both", expand=True, pady=6)

batch_text = tk.Text(batch_frame, font=("Segoe UI", 11), height=5, wrap="none")
batch_text.pack(fill="both", expand=True)
batch_text.bind("<KeyRelease>", delayed_batch_convert)

# =========================
# Statistics Frame
# =========================
stats_frame = ttk.LabelFrame(main, text="Statistics", padding=12)
stats_frame.pack(fill="x", pady=6)

for i, (label, var) in enumerate(stats_vars.items()):
    ttk.Label(stats_frame, text=label.replace("_", " ").title() + ":",
              font=("Segoe UI", 10, "bold")).grid(row=0, column=i * 2, padx=4, sticky="e")
    ttk.Label(stats_frame, textvariable=var,
              font=("Segoe UI", 10)).grid(row=0, column=i * 2 + 1, padx=6, sticky="w")

# =========================
# Actions
# =========================
actions = ttk.Frame(main)
actions.pack(pady=12)

ttk.Button(actions, text="📂 Open", command=open_file,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="💾 Save", command=save_file,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="🧹 Clear", command=clear_all,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="❓ Help", command=show_help,
           style="Action.TButton").pack(side="left", padx=6)

ttk.Checkbutton(
    actions,
    text="Dark Mode",
    variable=dark_mode_var,
    command=toggle_theme
).pack(side="left", padx=14)

# =========================
# Run App
# =========================
root.mainloop()
