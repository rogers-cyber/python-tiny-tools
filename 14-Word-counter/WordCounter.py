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
root.title("WordCounter Pro")
root.geometry("1050x650")
# root.iconbitmap(resource_path("logo.ico"))

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)

stats_vars = {
    "words": tk.StringVar(value="0"),
    "characters": tk.StringVar(value="0"),
    "characters_no_space": tk.StringVar(value="0"),
    "lines": tk.StringVar(value="0"),
    "sentences": tk.StringVar(value="0"),
    "reading_time": tk.StringVar(value="0 min"),
}

keyword_var = tk.StringVar()
keyword_density_var = tk.StringVar(value="0%")

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

    text_area.configure(
        bg="#1e1e1e" if dark_mode_var.get() else "white",
        fg="white" if dark_mode_var.get() else "black",
        insertbackground="white" if dark_mode_var.get() else "black"
    )

    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Core Logic
# =========================
def count_text():
    content = text_area.get("1.0", tk.END).strip()

    if not content:
        for key in stats_vars:
            stats_vars[key].set("0" if key != "reading_time" else "0 min")
        keyword_density_var.set("0%")
        return

    words_list = content.split()
    words = len(words_list)
    characters = len(content)
    characters_no_space = len(content.replace(" ", "").replace("\n", ""))
    lines = len(content.splitlines())
    sentences = sum(content.count(x) for x in ".!?")

    # ⏱ Reading time (200 WPM)
    reading_minutes = max(1, round(words / 200))
    stats_vars["reading_time"].set(f"{reading_minutes} min")

    stats_vars["words"].set(words)
    stats_vars["characters"].set(characters)
    stats_vars["characters_no_space"].set(characters_no_space)
    stats_vars["lines"].set(lines)
    stats_vars["sentences"].set(sentences)

    # 🔍 Keyword density
    keyword = keyword_var.get().strip().lower()
    if keyword:
        occurrences = sum(1 for w in words_list if w.lower() == keyword)
        density = (occurrences / words) * 100
        keyword_density_var.set(f"{density:.2f}%")
    else:
        keyword_density_var.set("0%")

    set_status("Text analyzed")

def delayed_count(event=None):
    threading.Timer(0.1, count_text).start()

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
            text_area.delete("1.0", tk.END)
            text_area.insert("1.0", f.read())
        count_text()
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
            f.write(text_area.get("1.0", tk.END))
        set_status(f"Saved to {path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_text():
    if messagebox.askyesno("Clear", "Clear all text?"):
        text_area.delete("1.0", tk.END)
        count_text()
        set_status("Text cleared")

# =========================
# Help Window
# =========================
def show_help():
    win = tk.Toplevel(root)
    win.title("WordCounter Pro - Help")
    win.geometry("480x360")
    win.configure(bg="#2e2e2e")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    # win.iconbitmap(resource_path("logo.ico"))

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

    help_text = """📊 WordCounter Pro — Quick Help

• Type or paste text to see live statistics
• Counts words, characters, sentences, and lines
• Enter a keyword to calculate density (%)
• Reading time based on 200 words per minute
• Open and save .txt files
• Toggle Dark Mode for comfort

All processing is done locally.

Built by MateTools
https://matetools.gumroad.com
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

ttk.Label(main, text="WordCounter Pro", font=("Segoe UI", 22, "bold")).pack()
ttk.Label(main, text="Advanced word & text analysis tool",
          font=("Segoe UI", 11)).pack(pady=(0, 10))

# =========================
# Text Area
# =========================
text_frame = ttk.LabelFrame(main, text="Text Input", padding=10)
text_frame.pack(fill="both", pady=10)

text_area = tk.Text(
    text_frame,
    font=("Segoe UI", 11),
    wrap="word",
    height=10
)
text_area.pack(fill="both")
text_area.bind("<KeyRelease>", delayed_count)

# =========================
# Statistics
# =========================
stats_frame = ttk.LabelFrame(main, text="Statistics", padding=15)
stats_frame.pack(fill="x", pady=8)

for i, (label, var) in enumerate(stats_vars.items()):
    ttk.Label(stats_frame, text=label.replace("_", " ").title() + ":",
              font=("Segoe UI", 10, "bold")).grid(row=0, column=i * 2, padx=4, sticky="e")
    ttk.Label(stats_frame, textvariable=var,
              font=("Segoe UI", 10)).grid(row=0, column=i * 2 + 1, padx=6, sticky="w")

# =========================
# Keyword Density
# =========================
keyword_frame = ttk.LabelFrame(main, text="Keyword Density", padding=12)
keyword_frame.pack(fill="x", pady=8)

ttk.Label(keyword_frame, text="Keyword:",
          font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 6))

keyword_entry = ttk.Entry(keyword_frame, textvariable=keyword_var, width=22)
keyword_entry.pack(side="left")
keyword_entry.bind("<KeyRelease>", delayed_count)

ttk.Label(keyword_frame, text="Density:",
          font=("Segoe UI", 10, "bold")).pack(side="left", padx=(15, 6))

ttk.Label(keyword_frame, textvariable=keyword_density_var,
          font=("Segoe UI", 10)).pack(side="left")

# =========================
# Actions
# =========================
actions = ttk.Frame(main)
actions.pack(pady=12)

ttk.Button(actions, text="📂 Open", command=open_file,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="💾 Save", command=save_file,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="🧹 Clear", command=clear_text,
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
