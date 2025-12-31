import os
import json
import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from threading import Thread

# =========================
# Helpers
# =========================
CONFIG_FILE = "usernames_data.json"

def load_usernames():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_usernames():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(usernames_data, f, ensure_ascii=False, indent=4)

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def generate_username(length=8, style="Normal"):
    """Generate username based on selected style."""
    if style == "Normal":
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    elif style == "Lowercase":
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    elif style == "Uppercase":
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    elif style == "NumberEnd":
        chars = string.ascii_letters
        name = ''.join(random.choice(chars) for _ in range(length-1))
        return name + random.choice(string.digits)
    else:
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("🎲 Random Username Generator Pro")
root.geometry("970x600")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
usernames_data = load_usernames()
filtered_usernames = usernames_data.copy()
current_filter = tk.StringVar(value="")
current_sort = tk.StringVar(value="Alphabetical")
current_style = tk.StringVar(value="Normal")

# =========================
# Username Functions
# =========================
def add_username_thread(length, count, style):
    def task():
        global usernames_data
        for _ in range(count):
            username = generate_username(length, style)
            usernames_data.append(username)
        save_usernames()
        apply_filter_sort()
        set_status(f"Generated {count} username(s).")
    Thread(target=task, daemon=True).start()

def generate_usernames():
    try:
        length = int(length_entry.get())
        count = int(count_entry.get())
        if length < 3 or length > 20:
            messagebox.showwarning("Invalid Length", "Length must be between 3 and 20.")
            return
        if count < 1 or count > 1000:
            messagebox.showwarning("Invalid Count", "Count must be between 1 and 1000.")
            return
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter valid numbers.")
        return
    add_username_thread(length, count, current_style.get())

def clear_usernames():
    if messagebox.askyesno("Confirm", "Clear all saved usernames?"):
        usernames_data.clear()
        apply_filter_sort()
        save_usernames()
        set_status("All usernames cleared.")

def copy_selected(event=None):
    try:
        index = username_text.index("sel.first")
        end_index = username_text.index("sel.last")
        value = username_text.get(index, end_index)
        root.clipboard_clear()
        root.clipboard_append(value)
        set_status(f"Copied '{value}' to clipboard.")
    except tk.TclError:
        set_status("No selection to copy.")

def apply_filter_sort(*args):
    global filtered_usernames
    filter_text = current_filter.get().lower()
    if filter_text:
        filtered_usernames = [u for u in usernames_data if filter_text in u.lower()]
    else:
        filtered_usernames = usernames_data.copy()
    # Sort
    sort_option = current_sort.get()
    if sort_option == "Alphabetical":
        filtered_usernames.sort()
    elif sort_option == "Length (Short → Long)":
        filtered_usernames.sort(key=len)
    elif sort_option == "Length (Long → Short)":
        filtered_usernames.sort(key=len, reverse=True)
    update_username_text(filter_text)

def update_username_text(highlight_text=""):
    username_text.config(state=tk.NORMAL)
    username_text.delete("1.0", tk.END)
    for uname in filtered_usernames:
        start_index = username_text.index(tk.INSERT)
        username_text.insert(tk.END, uname + "\n")
        if highlight_text:
            # Highlight matching substrings
            idx = uname.lower().find(highlight_text)
            if idx != -1:
                start = f"{start_index}+{idx}c"
                end = f"{start_index}+{idx+len(highlight_text)}c"
                username_text.tag_add("highlight", start, end)
    username_text.tag_config("highlight", foreground="red", font=("Segoe UI", 12, "bold"))
    username_text.config(state=tk.DISABLED)
    total_var.set(f"Total Usernames: {len(filtered_usernames)}")

# =========================
# GUI Setup
# =========================
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")

ttk.Label(main_frame, text="🎲 Random Username Generator Pro", font=("Segoe UI", 22, "bold")).pack(pady=(0,10))

# Inputs
input_frame = ttk.LabelFrame(main_frame, text="Settings", padding=10)
input_frame.pack(fill="x", pady=5)

ttk.Label(input_frame, text="Length:").grid(row=0, column=0, padx=5)
length_entry = ttk.Entry(input_frame, width=10)
length_entry.grid(row=0, column=1, padx=5)
length_entry.insert(0, "8")

ttk.Label(input_frame, text="Count:").grid(row=0, column=2, padx=5)
count_entry = ttk.Entry(input_frame, width=10)
count_entry.grid(row=0, column=3, padx=5)
count_entry.insert(0, "10")

ttk.Label(input_frame, text="Style:").grid(row=0, column=4, padx=5)
style_combo = ttk.Combobox(input_frame, state="readonly", textvariable=current_style, width=20)
style_combo['values'] = ["Normal", "Lowercase", "Uppercase", "NumberEnd"]
style_combo.current(0)
style_combo.grid(row=0, column=5, padx=5)

ttk.Button(input_frame, text="Generate", style="Generate.TButton", command=generate_usernames).grid(row=0, column=6, padx=5)
ttk.Button(input_frame, text="Clear All", style="Clear.TButton", command=clear_usernames).grid(row=0, column=7, padx=5)
ttk.Button(input_frame, text="Copy Selected", style="Copy.TButton", command=copy_selected).grid(row=0, column=8, padx=5)

ttk.Style().configure("Generate.TButton", foreground="black", background="#4CAF50")
ttk.Style().configure("Clear.TButton", foreground="black", background="#FF9800")
ttk.Style().configure("Copy.TButton", foreground="black", background="#2196F3")

# Filter & Sort
filter_sort_frame = ttk.LabelFrame(main_frame, text="Filter & Sort", padding=10)
filter_sort_frame.pack(fill="x", pady=5)

ttk.Label(filter_sort_frame, text="Filter:").grid(row=0, column=0, padx=5)
filter_entry = ttk.Entry(filter_sort_frame, textvariable=current_filter)
filter_entry.grid(row=0, column=1, padx=5)
current_filter.trace_add("write", apply_filter_sort)

ttk.Label(filter_sort_frame, text="Sort by:").grid(row=0, column=2, padx=5)
sort_combo = ttk.Combobox(filter_sort_frame, state="readonly", textvariable=current_sort, width=25)
sort_combo['values'] = ["Alphabetical", "Length (Short → Long)", "Length (Long → Short)"]
sort_combo.current(0)
sort_combo.grid(row=0, column=3, padx=5)
sort_combo.bind("<<ComboboxSelected>>", apply_filter_sort)

# Username display with highlighting
text_frame = ttk.Frame(main_frame)
text_frame.pack(expand=True, fill="both", pady=10)

username_text = tk.Text(text_frame, font=("Segoe UI", 12), state=tk.DISABLED, wrap="none", height=10)
username_text.pack(side="left", expand=True, fill="both")

scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=username_text.yview)
scrollbar.pack(side="right", fill="y")
username_text.config(yscrollcommand=scrollbar.set)

username_text.bind("<Control-c>", copy_selected)

# Total count
total_var = tk.StringVar(value=f"Total Usernames: {len(filtered_usernames)}")
ttk.Label(main_frame, textvariable=total_var, font=("Segoe UI", 12)).pack()

# Status Bar
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side="bottom", fill="x")

# Initial load
apply_filter_sort()

# Run App
root.mainloop()
