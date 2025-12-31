import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sv_ttk
import random

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
root.title("Random Joke Generator")
root.geometry("600x500")
root.minsize(600, 500)
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
joke_result_var = tk.StringVar(value="")
joke_history = []  # List of tuples: (joke_type, joke)

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)

# =========================
# Joke Data & Generation
# =========================
JOKES = {
    "Classic": [
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don’t scientists trust atoms? Because they make up everything!",
        "I told my computer I needed a break, and it said 'No problem – I'll go to sleep.'"
    ],
    "Dad Jokes": [
        "I would avoid the sushi if I was you. It’s a little fishy.",
        "Why did the math book look sad? Because it had too many problems.",
        "I only know 25 letters of the alphabet… I don’t know y."
    ],
    "Programming": [
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "There are 10 types of people in the world: those who understand binary and those who don’t.",
        "Why did the developer go broke? Because he used up all his cache."
    ]
}

def generate_joke(joke_type):
    jokes = JOKES.get(joke_type, sum(JOKES.values(), []))
    return random.choice(jokes)

# =========================
# Joke Generation & History
# =========================
def create_joke():
    joke_type = joke_type_var.get()
    if not joke_type:
        messagebox.showwarning("Select Type", "Please select a joke type.")
        return

    set_status("Generating joke...")
    threading.Thread(target=_generate_joke_thread, args=(joke_type,), daemon=True).start()

def _generate_joke_thread(joke_type):
    joke = generate_joke(joke_type)
    joke_result_var.set(joke)
    add_to_history(joke_type, joke)
    set_status("Joke generated!")

def add_to_history(joke_type, joke):
    joke_history.append((joke_type, joke))
    preview = joke[:80] + "..." if len(joke) > 80 else joke
    history_list.insert(tk.END, f"[{joke_type}] {preview}")

def export_history_txt():
    if not joke_history:
        messagebox.showinfo("Empty History", "No jokes to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Export Joke History"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Random Joke Generator History\n")
            f.write("=" * 50 + "\n\n")
            for i, (jtype, joke) in enumerate(joke_history, 1):
                f.write(f"{i}. Type: {jtype}\n")
                f.write(f"   Joke: {joke}\n\n")
        set_status("Joke history exported")
        messagebox.showinfo("Export Successful", "Joke history saved successfully.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

def view_selected_joke(event=None):
    selection = history_list.curselection()
    if not selection:
        messagebox.showinfo("No Selection", "Please select a joke from history.")
        return
    index = selection[0]
    _, joke = joke_history[index]

    joke_window = tk.Toplevel(root)
    joke_window.title("Full Joke")
    joke_window.geometry("500x200")

    # Make it modal
    joke_window.transient(root)  # Keep above main window
    joke_window.grab_set()       # Block interaction with main window

    tk.Label(joke_window, text=joke, wraplength=480, font=("Segoe UI", 14)).pack(expand=True, fill="both", padx=10, pady=10)

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

ttk.Label(main, text="Random Joke Generator", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="ew", pady=(0,10))

# Joke Type Selection
joke_type_var = tk.StringVar()
ttk.Label(main, text="Select Joke Type:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
ttk.Combobox(main, textvariable=joke_type_var, values=list(JOKES.keys()), font=("Segoe UI", 12)).grid(row=2, column=0, sticky="ew", pady=2)

# Joke Result
ttk.Label(main, text="Generated Joke:", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
joke_result_label = ttk.Label(main, textvariable=joke_result_var, wraplength=550, font=("Segoe UI", 14))
joke_result_label.grid(row=4, column=0, sticky="w", pady=5)

# Controls
controls = ttk.Frame(main)
controls.grid(row=5, column=0, sticky="ew", pady=8)
controls.columnconfigure((0,1), weight=1)

ttk.Button(controls, text="😂 Generate Joke", command=create_joke, style="Action.TButton").grid(row=0, column=0, padx=4, sticky="ew")
ttk.Button(controls, text="📤 Export History", command=export_history_txt, style="Action.TButton").grid(row=0, column=1, padx=4, sticky="ew")

# Joke History Vault
vault = ttk.LabelFrame(main, text="Joke History Vault", padding=10)
vault.grid(row=6, column=0, sticky="nsew", pady=10)
main.rowconfigure(6, weight=1)

history_list = tk.Listbox(vault, font=("Segoe UI", 10), height=7)
history_list.pack(fill="both", expand=True)
history_list.bind("<Double-Button-1>", view_selected_joke)

# Options
options_frame = ttk.Frame(main)
options_frame.grid(row=7, column=0, sticky="w", pady=6)
ttk.Checkbutton(options_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(side="left", padx=(0,10))

# =========================
# Run App
# =========================
root.mainloop()
