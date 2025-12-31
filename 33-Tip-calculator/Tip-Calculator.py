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
root.title("Interactive Tip Calculator")
root.geometry("600x700")
root.minsize(600, 700)
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
bill_var = tk.StringVar()
tip_var = tk.StringVar(value="15")
people_var = tk.StringVar(value="1")
tip_per_person_var = tk.StringVar(value="$0.00")
total_per_person_var = tk.StringVar(value="$0.00")
calculation_history = []  # List of tuples: (bill, tip%, people, tip_pp, total_pp)

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)
    for entry in [bill_entry, tip_entry, people_entry]:
        entry.configure(background=bg, foreground=fg)

# =========================
# Tip Calculation with Animation
# =========================
def calculate_tip(real_time=False):
    try:
        bill = float(bill_var.get())
        tip_percent = float(tip_var.get())
        people = int(people_var.get())
        if bill < 0 or tip_percent < 0 or people < 1:
            raise ValueError
    except ValueError:
        if not real_time:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
        return
    
    tip_total = bill * (tip_percent / 100)
    total_bill = bill + tip_total
    tip_per_person = tip_total / people
    total_per_person = total_bill / people

    animate_split(tip_per_person, total_per_person)

    if not real_time:
        add_to_history(bill, tip_percent, people, tip_per_person, total_per_person)
        set_status("Calculation completed!")

# =========================
# Animation Function
# =========================
def animate_split(tip_final, total_final, steps=30, interval=15):
    tip_current = 0.0
    total_current = 0.0
    tip_step = tip_final / steps
    total_step = total_final / steps

    def step_animation(count=0):
        nonlocal tip_current, total_current
        if count >= steps:
            tip_per_person_var.set(f"${tip_final:.2f}")
            total_per_person_var.set(f"${total_final:.2f}")
            return
        tip_current += tip_step
        total_current += total_step
        tip_per_person_var.set(f"${tip_current:.2f}")
        total_per_person_var.set(f"${total_current:.2f}")
        root.after(interval, lambda: step_animation(count + 1))

    step_animation()

# =========================
# Preset Tip Buttons
# =========================
def set_tip(value):
    tip_var.set(str(value))
    calculate_tip(real_time=True)

# =========================
# History Management
# =========================
def add_to_history(bill, tip_percent, people, tip_pp, total_pp):
    calculation_history.append((bill, tip_percent, people, tip_pp, total_pp))
    preview = f"${bill:.2f} | {tip_percent}% | {people} person(s) → Tip: ${tip_pp:.2f}, Total: ${total_pp:.2f}"
    history_list.insert(tk.END, preview)

def export_history_txt():
    if not calculation_history:
        messagebox.showinfo("Empty History", "No calculations to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Export Tip History"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Tip Calculator History\n")
            f.write("=" * 40 + "\n\n")
            for i, (bill, tip, people, tip_pp, total_pp) in enumerate(calculation_history, 1):
                f.write(f"{i}. Bill: ${bill:.2f}, Tip: {tip}%, People: {people}\n")
                f.write(f"   Tip per person: ${tip_pp:.2f}, Total per person: ${total_pp:.2f}\n\n")
        set_status("History exported successfully")
        messagebox.showinfo("Export Successful", "Tip calculation history saved.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

# =========================
# History Viewer with Animation
# =========================
def view_selected_history(event=None):
    selection = history_list.curselection()
    if not selection:
        messagebox.showinfo("No Selection", "Please select a calculation from the history.")
        return
    index = selection[0]
    bill, tip, people, tip_pp, total_pp = calculation_history[index]

    history_window = tk.Toplevel(root)
    history_window.title(f"Calculation Details")
    history_window.geometry("500x400")
    history_window.rowconfigure(0, weight=1)
    history_window.columnconfigure(0, weight=1)
    history_window.transient(root)
    history_window.grab_set()

    frame = ttk.Frame(history_window, padding=10)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    text_widget = tk.Text(frame, wrap="word", font=("Segoe UI", 12))
    text_widget.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    text_widget.configure(yscrollcommand=scrollbar.set)
    text_widget.configure(state="normal")
    text_widget.delete("1.0", tk.END)

    lines = [
        f"Bill Amount: ${bill:.2f}",
        f"Tip Percentage: {tip}%",
        f"Number of People: {people}",
        f"Tip per Person: ${tip_pp:.2f}",
        f"Total per Person: ${total_pp:.2f}"
    ]

    def type_lines(idx=0):
        if idx >= len(lines):
            text_widget.configure(state="disabled")
            history_window.grab_release()
            return
        
        line = lines[idx]
        char_idx = 0

        def type_char():
            nonlocal char_idx
            if char_idx < len(line):
                text_widget.insert(tk.END, line[char_idx])
                text_widget.see(tk.END)
                char_idx += 1
                text_widget.after(20, type_char)
            else:
                text_widget.insert(tk.END, "\n")
                text_widget.after(100, lambda: type_lines(idx + 1))

        type_char()

    type_lines()
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

ttk.Label(main, text="Interactive Tip Calculator", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="ew", pady=(0,10))

# Inputs
ttk.Label(main, text="Bill Amount ($):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
bill_entry = ttk.Entry(main, textvariable=bill_var, font=("Segoe UI", 14))
bill_entry.grid(row=2, column=0, sticky="ew", pady=2)

ttk.Label(main, text="Tip Percentage (%):", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
tip_entry = ttk.Entry(main, textvariable=tip_var, font=("Segoe UI", 14))
tip_entry.grid(row=4, column=0, sticky="ew", pady=2)

# Preset Tip Buttons
preset_frame = ttk.Frame(main)
preset_frame.grid(row=5, column=0, sticky="ew", pady=(0,10))
preset_frame.columnconfigure((0,1,2), weight=1)
ttk.Button(preset_frame, text="10%", command=lambda: set_tip(10)).grid(row=0, column=0, sticky="ew", padx=2)
ttk.Button(preset_frame, text="15%", command=lambda: set_tip(15)).grid(row=0, column=1, sticky="ew", padx=2)
ttk.Button(preset_frame, text="20%", command=lambda: set_tip(20)).grid(row=0, column=2, sticky="ew", padx=2)

ttk.Label(main, text="Number of People:", font=("Segoe UI", 12)).grid(row=6, column=0, sticky="w")
people_entry = ttk.Entry(main, textvariable=people_var, font=("Segoe UI", 14))
people_entry.grid(row=7, column=0, sticky="ew", pady=2)

# Output
ttk.Label(main, text="Tip per Person:", font=("Segoe UI", 12)).grid(row=8, column=0, sticky="w", pady=(10,0))
ttk.Label(main, textvariable=tip_per_person_var, font=("Segoe UI", 14, "bold")).grid(row=9, column=0, sticky="w")

ttk.Label(main, text="Total per Person:", font=("Segoe UI", 12)).grid(row=10, column=0, sticky="w", pady=(10,0))
ttk.Label(main, textvariable=total_per_person_var, font=("Segoe UI", 14, "bold")).grid(row=11, column=0, sticky="w")

# Controls
controls = ttk.Frame(main)
controls.grid(row=12, column=0, sticky="ew", pady=12)
controls.columnconfigure((0,1), weight=1)
ttk.Button(controls, text="💰 Calculate Tip", command=calculate_tip, style="Action.TButton").grid(row=0, column=0, padx=4, sticky="ew")
ttk.Button(controls, text="📤 Export History", command=export_history_txt, style="Action.TButton").grid(row=0, column=1, padx=4, sticky="ew")

# History Vault
vault = ttk.LabelFrame(main, text="Calculation History Vault", padding=10)
vault.grid(row=13, column=0, sticky="nsew", pady=10)
main.rowconfigure(13, weight=1)
history_list = tk.Listbox(vault, font=("Segoe UI", 10), height=7)
history_list.pack(fill="both", expand=True)
history_list.bind("<Double-Button-1>", view_selected_history)

# Options
options_frame = ttk.Frame(main)
options_frame.grid(row=14, column=0, sticky="w", pady=6)
ttk.Checkbutton(options_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(side="left", padx=(0,10))

# =========================
# Real-Time Calculation Bindings
# =========================
bill_var.trace_add("write", lambda *args: calculate_tip(real_time=True))
tip_var.trace_add("write", lambda *args: calculate_tip(real_time=True))
people_var.trace_add("write", lambda *args: calculate_tip(real_time=True))

# =========================
# Run App
# =========================
root.mainloop()
