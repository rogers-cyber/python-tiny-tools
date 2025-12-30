import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sv_ttk

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Prime Number Checker")
root.geometry("900x600")
root.iconbitmap("")  # Add path to your icon if needed

sv_ttk.set_theme("light")  # Default theme

# =========================
# Globals
# =========================
checked_numbers = {}  # number: True/False
dark_mode_var = tk.BooleanVar(value=False)

# =========================
# Helpers
# =========================
def toggle_theme():
    if dark_mode_var.get():
        root.configure(bg="#2E2E2E")
        style.configure("TLabel", background="#2E2E2E", foreground="white")
        style.configure("TFrame", background="#2E2E2E")
        style.configure("TButton", background="#4CAF50", foreground="white")
        style.configure("TNotebook", background="#2E2E2E")
    else:
        root.configure(bg="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="black")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TButton", background="#4CAF50", foreground="white")
        style.configure("TNotebook", background="#FFFFFF")

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def check_number():
    num_str = number_entry.get().strip()
    if not num_str.isdigit():
        messagebox.showerror("Invalid Input", "Enter a valid positive integer.")
        return
    num = int(num_str)
    prime = is_prime(num)
    checked_numbers[num] = prime
    update_results()
    number_entry.delete(0, tk.END)

def update_results():
    result_text.configure(state="normal")
    result_text.delete("1.0", tk.END)
    for num, prime in sorted(checked_numbers.items()):
        if prime:
            result_text.insert(tk.END, f"✅ {num} is a prime number.\n", "prime")
        else:
            result_text.insert(tk.END, f"❌ {num} is NOT a prime number.\n", "not_prime")
    result_text.configure(state="disabled")
    result_text.tag_configure("prime", foreground="#4CAF50")
    result_text.tag_configure("not_prime", foreground="#F44336")

def clear_history():
    checked_numbers.clear()
    update_results()

def copy_results():
    root.clipboard_clear()
    root.clipboard_append(result_text.get("1.0", tk.END))
    messagebox.showinfo("Copied", "Results copied to clipboard.")

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")

style.configure("Action.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#4CAF50", padding=8)
style.map("Action.TButton", background=[("active", "#45a049"), ("disabled", "#a5d6a7")])

style.configure("Secondary.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#2196F3", padding=8)
style.map("Secondary.TButton", background=[("active", "#1976D2"), ("disabled", "#90caf9")])

# =========================
# Layout
# =========================
top_frame = ttk.Frame(root, padding=20)
top_frame.pack(fill="x")

ttk.Label(top_frame, text="Prime Number Checker", font=("Segoe UI", 20, "bold")).pack(anchor="w")
ttk.Label(top_frame, text="Enter a number and check if it is prime.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0,10))

input_frame = ttk.Frame(root, padding=10)
input_frame.pack(fill="x")

ttk.Label(input_frame, text="Number:", font=("Segoe UI", 12)).pack(side="left", padx=(0,5))
number_entry = ttk.Entry(input_frame, width=20, font=("Segoe UI", 12))
number_entry.pack(side="left", padx=(0,10), ipady=4)

ttk.Button(input_frame, text="Check", command=check_number, style="Action.TButton").pack(side="left", padx=5)
ttk.Button(input_frame, text="Clear History", command=clear_history, style="Secondary.TButton").pack(side="left", padx=5)
ttk.Button(input_frame, text="Copy Results", command=copy_results, style="Secondary.TButton").pack(side="left", padx=5)

dark_frame = ttk.Frame(root, padding=10)
dark_frame.pack(fill="x")
ttk.Checkbutton(dark_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme, style="Action.TButton").pack(anchor="w")

result_frame = ttk.LabelFrame(root, text="Results", padding=15)
result_frame.pack(fill="both", expand=True, padx=20, pady=20)

result_text = scrolledtext.ScrolledText(result_frame, state="disabled", font=("Consolas", 12))
result_text.pack(fill="both", expand=True)

# =========================
# Run App
# =========================
root.mainloop()
