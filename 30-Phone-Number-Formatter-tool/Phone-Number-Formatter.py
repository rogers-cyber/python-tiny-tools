import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sv_ttk
import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat, PhoneNumberType
import pycountry

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def get_country_name(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code

def get_example_number(region_code):
    """Returns an example national number for the region"""
    try:
        example = phonenumbers.example_number_for_type(region_code, PhoneNumberType.MOBILE)
        if example:
            return phonenumbers.format_number(example, PhoneNumberFormat.NATIONAL)
        return ""
    except:
        return ""

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Universal Phone Formatter")
root.geometry("780x750")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
phone_var = tk.StringVar()
formatted_result_var = tk.StringVar(value="Result: —")
phone_history = []
region_var = tk.StringVar(value="US")
region_example_var = tk.StringVar(value="")

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)
    phone_entry.configure(background=bg, foreground=fg)
    region_entry.configure(background=bg, foreground=fg)

# =========================
# Update Example Number
# =========================
def update_region_example(*args):
    region = region_var.get().strip().upper()
    example = get_example_number(region)
    region_example_var.set(f"Example format for {region}: {example}" if example else "No example available")

region_var.trace_add("write", update_region_example)
update_region_example()  # Initial example

# =========================
# Phone Formatting Logic
# =========================
def format_phone_number(number, region=None):
    try:
        parsed = phonenumbers.parse(number, region) if region else phonenumbers.parse(number, None)
        if not phonenumbers.is_possible_number(parsed):
            return None
        if not phonenumbers.is_valid_number(parsed):
            return None
        international = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
        national = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
        country = get_country_name(phonenumbers.region_code_for_number(parsed))
        return f"{international} (National: {national}, Country: {country})"
    except NumberParseException:
        return None

def validate_phone():
    number = phone_var.get().strip()
    region = region_var.get().strip().upper()
    if not number:
        messagebox.showwarning("Error", "Please enter a phone number.")
        return

    set_status("Formatting phone number...")
    threading.Thread(target=_validate_phone_thread, args=(number, region), daemon=True).start()

def _validate_phone_thread(number, region):
    formatted = format_phone_number(number, region)
    if formatted:
        formatted_result_var.set(f"Result: ✅ {formatted}")
        add_to_history(formatted)
    else:
        formatted_result_var.set("Result: ❌ Invalid phone number")
    set_status("Formatting complete")

# =========================
# Phone History
# =========================
def add_to_history(formatted_number):
    phone_history.append(formatted_number)
    history_list.insert(tk.END, f"{len(phone_history)} • {formatted_number}")

def export_history_txt():
    if not phone_history:
        messagebox.showinfo("Empty History", "No phone numbers to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Export Phone History"
    )

    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Universal Phone Number History\n")
            f.write("=" * 50 + "\n\n")
            for i, number in enumerate(phone_history, 1):
                f.write(f"{i}. {number}\n")
        set_status("Phone history exported")
        messagebox.showinfo("Export Successful", "Phone history saved successfully.")
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

ttk.Label(main, text="Universal Phone Formatter",
          font=("Segoe UI", 22, "bold")).pack()

ttk.Label(main, text="Enter Phone Number:", font=("Segoe UI", 12)).pack(pady=(10,0))
phone_entry = ttk.Entry(main, textvariable=phone_var, font=("Segoe UI", 14), justify="center")
phone_entry.pack(fill="x", pady=6)

ttk.Label(main, text="Default Region (for local numbers, e.g., US, GB, IN):", font=("Segoe UI", 10)).pack(pady=(4,0))
region_entry = ttk.Entry(main, textvariable=region_var, font=("Segoe UI", 12), justify="center")
region_entry.pack(fill="x", pady=4)

ttk.Label(main, textvariable=region_example_var, font=("Segoe UI", 10, "italic")).pack(pady=(2,6))

ttk.Label(main, textvariable=formatted_result_var, font=("Segoe UI", 12, "bold")).pack(pady=8)

# =========================
# Controls
# =========================
controls = ttk.Frame(main)
controls.pack(pady=8)

ttk.Button(controls, text="✅ Format", command=validate_phone, style="Action.TButton").pack(side="left", padx=4)
ttk.Button(controls, text="📤 Export History", command=export_history_txt, style="Action.TButton").pack(side="left", padx=4)

# =========================
# History Vault
# =========================
vault = ttk.LabelFrame(main, text="Phone History Vault", padding=10)
vault.pack(fill="both", expand=True, pady=10)

history_list = tk.Listbox(vault, font=("Segoe UI", 10), height=12)
history_list.pack(fill="both", expand=True)

# =========================
# Options
# =========================
ttk.Checkbutton(main, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(pady=6)

# =========================
# Run App
# =========================
root.mainloop()
