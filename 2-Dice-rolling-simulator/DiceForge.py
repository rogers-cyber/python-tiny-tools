import sys
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

def resource_path(file_name):
    """Get the absolute path to a resource, works for PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("DiceForge - Dice Rolling Simulator")
root.geometry("900x620")

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
dice_count_var = tk.IntVar(value=1)
dice_sides_var = tk.IntVar(value=6)

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
        style.configure("TLabelframe", background="#2E2E2E", foreground="white")
        style.configure("TLabelframe.Label", background="#2E2E2E", foreground="white")
        style.configure("TCheckbutton", background="#2E2E2E", foreground="white")
    else:
        root.configure(bg="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="black")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TLabelframe", background="#FFFFFF", foreground="black")
        style.configure("TLabelframe.Label", background="#FFFFFF", foreground="black")
        style.configure("TCheckbutton", background="#FFFFFF", foreground="black")

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
style.map(
    "Action.TButton",
    background=[("active", "#45a049"), ("disabled", "#a5d6a7")]
)

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w",
          font=("Segoe UI", 10)).pack(side=tk.BOTTOM, fill="x")

# =========================
# Notebook
# =========================
tabs = ttk.Notebook(root)
tabs.pack(expand=True, fill="both", padx=20, pady=20)

# =========================
# Dashboard Tab
# =========================
dash_tab = ttk.Frame(tabs, padding=20)
tabs.add(dash_tab, text="🎲 Dashboard")

ttk.Label(
    dash_tab,
    text="DiceForge - Dice Rolling Simulator",
    font=("Segoe UI", 20, "bold")
).pack(anchor="w")

ttk.Label(
    dash_tab,
    text="Simulate dice rolls for games, tabletop RPGs, and probability testing.",
    font=("Segoe UI", 11)
).pack(anchor="w", pady=(5, 15))

info_frame = ttk.LabelFrame(dash_tab, text="Features", padding=15)
info_frame.pack(fill="x")

ttk.Label(
    info_frame,
    text=(
        "• Roll any number of dice\n"
        "• Choose how many sides each die has\n"
        "• See individual rolls and totals instantly\n"
        "• Clean and modern UI\n"
        "• Light and Dark mode support"
    ),
    font=("Segoe UI", 11),
    justify="left"
).pack(anchor="w")

# =========================
# Tool Tab
# =========================
tool_tab = ttk.Frame(tabs, padding=20)
tabs.add(tool_tab, text="🔧 Dice Roller")

# ---------------- Dice Settings ----------------
settings_card = ttk.LabelFrame(tool_tab, text="Dice Settings", padding=15)
settings_card.pack(fill="x", pady=10)

ttk.Label(settings_card, text="Number of Dice:", font=("Segoe UI", 11)).pack(side="left", padx=5)
dice_spin = ttk.Spinbox(
    settings_card,
    from_=1,
    to=100,
    textvariable=dice_count_var,
    width=6,
    font=("Segoe UI", 11)
)
dice_spin.pack(side="left", padx=10)

ttk.Label(settings_card, text="Sides per Die:", font=("Segoe UI", 11)).pack(side="left", padx=5)
sides_spin = ttk.Spinbox(
    settings_card,
    from_=2,
    to=1000,
    textvariable=dice_sides_var,
    width=6,
    font=("Segoe UI", 11)
)
sides_spin.pack(side="left", padx=10)

# ---------------- Roll Output ----------------
output_card = ttk.LabelFrame(tool_tab, text="Roll Results", padding=15)
output_card.pack(fill="both", expand=True, pady=10)

output_text = tk.Text(
    output_card,
    height=10,
    font=("Consolas", 12),
    state="disabled"
)
output_text.pack(fill="both", expand=True)

# ---------------- Actions ----------------
action_card = ttk.LabelFrame(tool_tab, text="Actions", padding=15)
action_card.pack(fill="x", pady=10)

def roll_dice():
    try:
        count = dice_count_var.get()
        sides = dice_sides_var.get()
        if count <= 0 or sides <= 1:
            raise ValueError

        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)

        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Rolled {count}d{sides}\n\n")
        output_text.insert(tk.END, f"Individual Rolls:\n{rolls}\n\n")
        output_text.insert(tk.END, f"Total: {total}")
        output_text.config(state="disabled")

        set_status("Dice rolled successfully.")

    except Exception:
        messagebox.showerror("Error", "Invalid dice configuration.")

ttk.Button(
    action_card,
    text="Roll Dice",
    command=roll_dice,
    style="Action.TButton"
).pack(side="left", padx=5)

ttk.Checkbutton(
    action_card,
    text="Dark Mode",
    variable=dark_mode_var,
    command=toggle_theme
).pack(side="left", padx=15)

# =========================
# Run App
# =========================
root.mainloop()
