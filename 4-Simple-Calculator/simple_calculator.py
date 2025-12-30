import sys
import os
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
root.title("Simple Calculator")
root.geometry("360x520")
root.resizable(False, False)

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
expression = tk.StringVar(value="")
dark_mode_var = tk.BooleanVar(value=False)

# =========================
# Helpers
# =========================
def set_expression(value):
    expression.set(value)

def append_value(val):
    expression.set(expression.get() + str(val))

def clear_all():
    expression.set("")

def calculate():
    try:
        result = eval(expression.get())
        expression.set(str(result))
    except Exception:
        messagebox.showerror("Error", "Invalid Expression")
        expression.set("")

def toggle_theme():
    if dark_mode_var.get():
        sv_ttk.set_theme("dark")
    else:
        sv_ttk.set_theme("light")

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Calc.TButton",
    font=("Segoe UI", 14, "bold"),
    padding=10
)

style.configure(
    "Equals.TButton",
    font=("Segoe UI", 14, "bold"),
    padding=10
)

# =========================
# Display
# =========================
display_frame = ttk.Frame(root, padding=10)
display_frame.pack(fill="x")

display = ttk.Entry(
    display_frame,
    textvariable=expression,
    font=("Consolas", 20),
    justify="right"
)
display.pack(fill="x", ipady=10)

# =========================
# Buttons
# =========================
btn_frame = ttk.Frame(root, padding=10)
btn_frame.pack(expand=True, fill="both")

buttons = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("C", 4, 2), ("+", 4, 3),
]

for (text, r, c) in buttons:
    action = clear_all if text == "C" else lambda t=text: append_value(t)
    ttk.Button(
        btn_frame,
        text=text,
        command=action,
        style="Calc.TButton"
    ).grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

# Equals button
ttk.Button(
    btn_frame,
    text="=",
    command=calculate,
    style="Equals.TButton"
).grid(row=5, column=0, columnspan=4, sticky="nsew", padx=5, pady=10)

# =========================
# Options
# =========================
options_frame = ttk.Frame(root, padding=10)
options_frame.pack(fill="x")

ttk.Checkbutton(
    options_frame,
    text="Dark Mode",
    variable=dark_mode_var,
    command=toggle_theme
).pack(anchor="w")

# =========================
# Grid Configuration
# =========================
for i in range(4):
    btn_frame.columnconfigure(i, weight=1)
for i in range(6):
    btn_frame.rowconfigure(i, weight=1)

# =========================
# Run App
# =========================
root.mainloop()
