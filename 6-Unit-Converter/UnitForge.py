import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sv_ttk

def resource_path(file_name):
    """Get the absolute path to a resource, works for PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Unit Converter")
root.geometry("1100x800")
# root.iconbitmap(resource_path("logo.ico"))

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
history_data = []  # Stores last 10 conversions

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

# =========================
# Custom Styles
# =========================
style = ttk.Style()
style.theme_use("clam")

style.configure("Action.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#4CAF50", padding=8)
style.map("Action.TButton", background=[("active", "#45a049"), ("disabled", "#a5d6a7")])

style.configure("TNotebook.Tab", padding=[10,5], font=("Segoe UI",11,"bold"), background="#e0e0e0")
style.map("TNotebook.Tab", background=[("selected","#90caf9")], foreground=[("selected","black")])

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
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

ttk.Label(dash_tab, text="Unit Converter", font=("Segoe UI", 20, "bold")).pack(anchor="w")
ttk.Label(dash_tab, text="Convert between Length and Weight units quickly and accurately.", font=("Segoe UI", 11)).pack(anchor="w", pady=(5,10))

ttk.Label(dash_tab, text="Key Features:", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(10,5))
features_frame = ttk.Frame(dash_tab)
features_frame.pack(fill="x", pady=5)

def create_feature_card(parent, title, desc):
    card = ttk.LabelFrame(parent, text=title, padding=10)
    ttk.Label(card, text=desc, wraplength=200, font=("Segoe UI", 10)).pack(anchor="w")
    return card

create_feature_card(features_frame, "🧮 Length & Weight Conversion",
                    "Supports common units like meters, kilometers, miles, kilograms, pounds, and more.").grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
create_feature_card(features_frame, "📊 Conversion History",
                    "Automatically keeps the last 10 conversions for quick reference.").grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
create_feature_card(features_frame, "🎨 Dark Mode",
                    "Switch between light and dark themes for comfortable usage.").grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
features_frame.columnconfigure((0,1,2), weight=1)

desc_frame = ttk.LabelFrame(dash_tab, text="About This Tool", padding=15)
desc_frame.pack(fill="x", pady=20)
ttk.Label(
    desc_frame,
    text=(
        "Unit Converter is a simple yet powerful tool for converting values between different units of Length and Weight.\n\n"
        "• Enter a numeric value and select units to convert.\n"
        "• Supports meters, kilometers, centimeters, miles, yards, feet, inches, kilograms, grams, pounds, ounces, etc.\n"
        "• Automatic history of last 10 conversions.\n"
        "• Modern interface with light/dark mode.\n\n"
        "🏢 Built with Python & Tkinter\n"
        "🌐 Enhances productivity for engineers, students, and professionals."
    ),
    wraplength=650,
    justify="left",
    font=("Segoe UI", 10)
).pack(anchor="w")

# =========================
# Converter Tab
# =========================
tool_tab = ttk.Frame(tabs, padding=20)
tabs.add(tool_tab, text="🔧 Converter")

# Conversion Factors
length_units = {
    "Meters": 1.0,
    "Kilometers": 1000.0,
    "Centimeters": 0.01,
    "Millimeters": 0.001,
    "Miles": 1609.34,
    "Yards": 0.9144,
    "Feet": 0.3048,
    "Inches": 0.0254
}

weight_units = {
    "Kilograms": 1.0,
    "Grams": 0.001,
    "Milligrams": 0.000001,
    "Pounds": 0.453592,
    "Ounces": 0.0283495
}

# ---------------- UI ----------------
ttk.Label(tool_tab, text="Value to Convert:", font=("Segoe UI", 12)).pack(anchor="w", pady=5)
value_entry = ttk.Entry(tool_tab, font=("Segoe UI", 14))
value_entry.pack(fill="x", pady=5)

ttk.Label(tool_tab, text="Select Category:", font=("Segoe UI", 12)).pack(anchor="w", pady=5)
category_var = tk.StringVar(value="Length")
category_combo = ttk.Combobox(tool_tab, textvariable=category_var, state="readonly",
                              values=["Length", "Weight"], font=("Segoe UI", 12))
category_combo.pack(fill="x", pady=5)

ttk.Label(tool_tab, text="From Unit:", font=("Segoe UI", 12)).pack(anchor="w", pady=5)
from_unit_var = tk.StringVar(value="Meters")
from_combo = ttk.Combobox(tool_tab, textvariable=from_unit_var, state="readonly", font=("Segoe UI", 12))
from_combo.pack(fill="x", pady=5)

ttk.Label(tool_tab, text="To Unit:", font=("Segoe UI", 12)).pack(anchor="w", pady=5)
to_unit_var = tk.StringVar(value="Kilometers")
to_combo = ttk.Combobox(tool_tab, textvariable=to_unit_var, state="readonly", font=("Segoe UI", 12))
to_combo.pack(fill="x", pady=5)

result_var = tk.StringVar(value="")
ttk.Label(tool_tab, text="Result:", font=("Segoe UI", 12)).pack(anchor="w", pady=5)
ttk.Label(tool_tab, textvariable=result_var, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

# ---------------- History ----------------
history_frame = ttk.LabelFrame(tool_tab, text="Conversion History (Last 10)", padding=10)
history_frame.pack(fill="both", expand=True, pady=10)
history_text = scrolledtext.ScrolledText(history_frame, height=6, font=("Consolas", 11), state="disabled")
history_text.pack(fill="both", expand=True)

# =========================
# Functions
# =========================
def update_units(event=None):
    if category_var.get() == "Length":
        units = list(length_units.keys())
    else:
        units = list(weight_units.keys())
    from_combo["values"] = units
    to_combo["values"] = units
    from_combo.set(units[0])
    to_combo.set(units[1])

def convert_unit():
    try:
        value = float(value_entry.get())
        if category_var.get() == "Length":
            factor_from = length_units[from_unit_var.get()]
            factor_to = length_units[to_unit_var.get()]
        else:
            factor_from = weight_units[from_unit_var.get()]
            factor_to = weight_units[to_unit_var.get()]
        result = value * factor_from / factor_to
        result_var.set(f"{result:.6g}")
        set_status(f"Converted {value} {from_unit_var.get()} to {result:.6g} {to_unit_var.get()}")
        add_to_history(value, from_unit_var.get(), result, to_unit_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number")
        result_var.set("")
        set_status("Error: Invalid input")

def add_to_history(value, from_unit, result, to_unit):
    global history_data
    entry = f"{value} {from_unit} → {result:.6g} {to_unit}"
    history_data.insert(0, entry)
    if len(history_data) > 10:
        history_data = history_data[:10]
    history_text.config(state="normal")
    history_text.delete("1.0", tk.END)
    history_text.insert(tk.END, "\n".join(history_data))
    history_text.config(state="disabled")

category_combo.bind("<<ComboboxSelected>>", update_units)

ttk.Button(tool_tab, text="Convert", command=convert_unit, style="Action.TButton").pack(pady=10)

# =========================
# Dark Mode Toggle
# =========================
ttk.Checkbutton(root, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(side="bottom", pady=5)

# =========================
# Run App
# =========================
update_units()
root.mainloop()
