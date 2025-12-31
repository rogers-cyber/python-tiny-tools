import sys
import os
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
root.title("Pattern History Printer")
root.geometry("600x700")
root.minsize(600, 700)
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
rows_var = tk.StringVar(value="5")
pattern_type_var = tk.StringVar(value="Pyramid")
pattern_history = []  # List of tuples: (pattern_type, rows, pattern_str)

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)
    for entry in [rows_entry]:
        entry.configure(background=bg, foreground=fg)

# =========================
# Pattern Generation
# =========================
def generate_pattern():
    try:
        rows = int(rows_var.get())
        if rows < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive integer for rows.")
        return
    
    p_type = pattern_type_var.get()
    pattern_lines = []

    if p_type == "Pyramid":
        for i in range(1, rows + 1):
            line = " " * (rows - i) + "*" * (2 * i - 1)
            pattern_lines.append(line)
    elif p_type == "Right Triangle":
        for i in range(1, rows + 1):
            pattern_lines.append("*" * i)
    elif p_type == "Inverted Pyramid":
        for i in range(rows, 0, -1):
            line = " " * (rows - i) + "*" * (2 * i - 1)
            pattern_lines.append(line)
    else:
        pattern_lines.append("Unknown pattern type!")

    pattern_str = "\n".join(pattern_lines)
    add_to_history(p_type, rows, pattern_str)
    set_status("Pattern generated! Click a history entry to view details.")

# =========================
# History Management
# =========================
def add_to_history(p_type, rows, pattern_str):
    pattern_history.append((p_type, rows, pattern_str))
    preview = f"{p_type} | Rows: {rows}"
    history_list.insert(tk.END, preview)

def export_history_txt():
    if not pattern_history:
        messagebox.showinfo("Empty History", "No patterns to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Export Pattern History"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Pattern History\n")
            f.write("=" * 40 + "\n\n")
            for i, (ptype, rows, pstr) in enumerate(pattern_history, 1):
                f.write(f"{i}. {ptype} | Rows: {rows}\n")
                f.write(pstr + "\n\n")
        set_status("History exported successfully")
        messagebox.showinfo("Export Successful", "Pattern history saved.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

# =========================
# History Viewer
# =========================
def view_selected_history(event=None):
    selection = history_list.curselection()
    if not selection:
        messagebox.showinfo("No Selection", "Please select a pattern from the history.")
        return
    index = selection[0]
    p_type, rows, pattern_str = pattern_history[index]

    history_window = tk.Toplevel(root)
    history_window.title(f"{p_type} | Rows: {rows}")
    history_window.geometry("500x400")
    history_window.grab_set()

    frame = ttk.Frame(history_window, padding=10)
    frame.pack(expand=True, fill="both")

    text_widget = tk.Text(frame, wrap="none", font=("Consolas", 12))
    text_widget.pack(expand=True, fill="both")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.insert(tk.END, pattern_str)
    text_widget.configure(state="disabled")
    history_window.focus()

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
main.columnconfigure(0, weight=1)

ttk.Label(main, text="Pattern History Printer", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="ew", pady=(0,10))

# Inputs
ttk.Label(main, text="Number of Rows:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
rows_entry = ttk.Entry(main, textvariable=rows_var, font=("Segoe UI", 14))
rows_entry.grid(row=2, column=0, sticky="ew", pady=2)

ttk.Label(main, text="Pattern Type:", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
pattern_combo = ttk.Combobox(main, textvariable=pattern_type_var, values=["Pyramid", "Right Triangle", "Inverted Pyramid"], font=("Segoe UI", 14), state="readonly")
pattern_combo.grid(row=4, column=0, sticky="ew", pady=2)

# Controls
controls = ttk.Frame(main)
controls.grid(row=5, column=0, sticky="ew", pady=12)
controls.columnconfigure((0,1), weight=1)
ttk.Button(controls, text="✨ Generate Pattern", command=generate_pattern, style="Action.TButton").grid(row=0, column=0, padx=4, sticky="ew")
ttk.Button(controls, text="📤 Export History", command=export_history_txt, style="Action.TButton").grid(row=0, column=1, padx=4, sticky="ew")

# History Vault
vault = ttk.LabelFrame(main, text="Pattern History Vault", padding=10)
vault.grid(row=6, column=0, sticky="nsew", pady=10)
main.rowconfigure(6, weight=1)
history_list = tk.Listbox(vault, font=("Segoe UI", 10), height=15)
history_list.pack(fill="both", expand=True)
history_list.bind("<Double-Button-1>", view_selected_history)

# Options
options_frame = ttk.Frame(main)
options_frame.grid(row=7, column=0, sticky="w", pady=6)
ttk.Checkbutton(options_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(side="left", padx=(0,10))

# =========================
# Run App
# =========================
root.mainloop()
