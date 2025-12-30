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

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("FiboTool")
root.geometry("980x620")
root.minsize(900, 550)

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
count_var = tk.IntVar(value=100)
status_var = tk.StringVar(value="Ready")

# =========================
# Status
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# =========================
# Fibonacci Logic (STREAMED)
# =========================
def generate_fibonacci():
    try:
        n = count_var.get()
        if n <= 0 or n > 100000:
            raise ValueError
    except Exception:
        messagebox.showerror("Invalid Input", "Enter a number between 1 and 100,000.")
        return

    output.delete("1.0", tk.END)
    progress["value"] = 0
    progress["maximum"] = n
    set_status("Generating sequence...")

    def task():
        a, b = 0, 1
        chunk = []

        for i in range(n):
            chunk.append(str(a))
            a, b = b, a + b

            if i % 100 == 0:
                text = ", ".join(chunk) + ", "
                root.after(0, output.insert, tk.END, text)
                root.after(0, progress.step, 100)
                chunk.clear()

        if chunk:
            root.after(0, output.insert, tk.END, ", ".join(chunk))

        root.after(0, lambda: progress.config(value=n))
        root.after(0, set_status, f"Generated {n} terms")

    threading.Thread(target=task, daemon=True).start()

def copy_result():
    root.clipboard_clear()
    root.clipboard_append(output.get("1.0", tk.END))
    set_status("Copied to clipboard")

def export_txt():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )
    if not file_path:
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output.get("1.0", tk.END))

    set_status(f"Saved to {os.path.basename(file_path)}")

# =========================
# Styles
# =========================
style = ttk.Style()
style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
style.configure("Subtitle.TLabel", font=("Segoe UI", 11))
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=10)

# =========================
# Layout (GRID-BASED)
# =========================
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# ----- Header -----
header = ttk.Frame(root, padding=(24, 16))
header.grid(row=0, column=0, sticky="ew")

header.columnconfigure(1, weight=1)

ttk.Label(header, text="FiboTool", style="Title.TLabel").grid(row=0, column=0, sticky="w")
ttk.Label(
    header,
    text="High-performance Fibonacci sequence generator",
    style="Subtitle.TLabel"
).grid(row=1, column=0, sticky="w", pady=(2, 0))

controls = ttk.Frame(header)
controls.grid(row=0, column=1, rowspan=2, sticky="e")

ttk.Label(controls, text="Terms").grid(row=0, column=0, padx=6)
ttk.Entry(controls, textvariable=count_var, width=10).grid(row=0, column=1)

# ----- Main Content -----
main = ttk.Frame(root, padding=(24, 0, 24, 16))
main.grid(row=1, column=0, sticky="nsew")
main.columnconfigure(0, weight=1)
main.rowconfigure(0, weight=1)

output_card = ttk.LabelFrame(main, text="Output", padding=10)
output_card.grid(row=0, column=0, sticky="nsew")
output_card.columnconfigure(0, weight=1)
output_card.rowconfigure(0, weight=1)

scroll = ttk.Scrollbar(output_card)
scroll.grid(row=0, column=1, sticky="ns")

output = tk.Text(
    output_card,
    wrap="word",
    font=("Consolas", 10),
    yscrollcommand=scroll.set
)
output.grid(row=0, column=0, sticky="nsew")
scroll.config(command=output.yview)

# ----- Actions -----
actions = ttk.Frame(main)
actions.grid(row=1, column=0, pady=12, sticky="ew")

ttk.Button(
    actions,
    text="Generate",
    command=generate_fibonacci,
    style="Action.TButton"
).pack(side="left")

ttk.Button(actions, text="Copy", command=copy_result).pack(side="left", padx=6)
ttk.Button(actions, text="Export TXT", command=export_txt).pack(side="left")

progress = ttk.Progressbar(actions)
progress.pack(side="right", fill="x", expand=True, padx=(12, 0))

# ----- Status Bar -----
status = ttk.Label(root, textvariable=status_var, anchor="w", padding=6)
status.grid(row=2, column=0, sticky="ew")

# =========================
# Run
# =========================
root.mainloop()
