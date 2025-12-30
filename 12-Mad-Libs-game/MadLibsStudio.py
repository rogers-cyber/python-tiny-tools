import sys
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Mad Libs Studio")
root.geometry("1100x700")

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
story_var = tk.StringVar(value="Adventure")
status_var = tk.StringVar(value="Choose a story and fill in the words ✍️")

stories = {
    "Adventure": {
        "template": (
            "One day, a {adjective} {noun} decided to {verb} through the {place}. "
            "Suddenly, it encountered a {adjective2} {animal}! "
            "Without hesitation, the {noun} shouted '{exclamation}!' and ran away."
        ),
        "fields": [
            ("adjective", "Adjective"),
            ("noun", "Noun"),
            ("verb", "Verb"),
            ("place", "Place"),
            ("adjective2", "Adjective"),
            ("animal", "Animal"),
            ("exclamation", "Exclamation"),
        ]
    },
    "Funny": {
        "template": (
            "At lunch, I saw a {adjective} person eating a {food}. "
            "They suddenly started to {verb} loudly, causing everyone to {reaction}. "
            "It was the most {adjective2} thing ever."
        ),
        "fields": [
            ("adjective", "Adjective"),
            ("food", "Food"),
            ("verb", "Verb"),
            ("reaction", "Reaction"),
            ("adjective2", "Adjective"),
        ]
    },
    "Sci-Fi": {
        "template": (
            "In the year {number}, humans discovered a {adjective} planet called {planet}. "
            "The inhabitants could {verb} and communicated using {plural_noun}. "
            "Earth was forever {adjective2}."
        ),
        "fields": [
            ("number", "Number"),
            ("adjective", "Adjective"),
            ("planet", "Planet Name"),
            ("verb", "Verb"),
            ("plural_noun", "Plural Noun"),
            ("adjective2", "Adjective"),
        ]
    }
}

input_vars = {}
generated_story = ""

# =========================
# Helpers
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)

    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)

    set_status(f"{'Dark' if dark_mode_var.get() else 'Light'} mode enabled")

# =========================
# Story Logic
# =========================
def build_inputs():
    for widget in input_frame.winfo_children():
        widget.destroy()
    input_vars.clear()

    story = stories[story_var.get()]

    for i, (key, label) in enumerate(story["fields"]):
        var = tk.StringVar()
        input_vars[key] = var

        row = ttk.Frame(input_frame)
        row.grid(row=i // 2, column=i % 2, padx=10, pady=6, sticky="ew")

        ttk.Label(row, text=f"{label}").pack(anchor="w")
        ttk.Entry(row, textvariable=var, width=32).pack(fill="x")

    set_status("Fill in all fields, then generate your story 🎲")

def generate_story():
    global generated_story
    story = stories[story_var.get()]
    data = {}

    for key, _ in story["fields"]:
        value = input_vars[key].get().strip()
        if not value:
            messagebox.showwarning("Missing Input", "Please fill in all fields.")
            return
        data[key] = value

    generated_story = story["template"].format(**data)

    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert("1.0", generated_story)
    output_text.config(state="disabled")

    set_status("Story generated! 🎉")

def copy_story():
    if not generated_story:
        return
    root.clipboard_clear()
    root.clipboard_append(generated_story)
    set_status("Story copied to clipboard 📋")

def show_help():
    messagebox.showinfo(
        "Mad Libs Studio",
        "1️⃣ Choose a story type\n"
        "2️⃣ Fill in the word prompts\n"
        "3️⃣ Click Generate\n"
        "4️⃣ Laugh, copy, and share 😄"
    )

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Primary.TButton",
    font=("Segoe UI", 11, "bold"),
    padding=10,
    foreground="white",
    background="#4CAF50"
)

style.map(
    "Primary.TButton",
    background=[("active", "#43a047")]
)

# =========================
# Status Bar
# =========================
ttk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill="x")

# =========================
# Main UI
# =========================
main = ttk.Frame(root, padding=30)
main.pack(expand=True, fill="both")

# Header
ttk.Label(main, text="🎭 Mad Libs Studio", font=("Segoe UI", 26, "bold")).pack()
ttk.Label(
    main,
    text="Fill in the blanks. Create chaos. Laugh responsibly.",
    font=("Segoe UI", 12)
).pack(pady=(0, 20))

# Story Selector
selector = ttk.Frame(main)
selector.pack(pady=10)

ttk.Label(selector, text="Story Type", font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)

ttk.Combobox(
    selector,
    values=list(stories.keys()),
    textvariable=story_var,
    state="readonly",
    width=26
).pack(side="left")

# Inputs Card
input_card = ttk.LabelFrame(main, text="✏️ Your Words", padding=20)
input_card.pack(fill="x", pady=10)

input_frame = ttk.Frame(input_card)
input_frame.pack(fill="x")

# Output Card
output_card = ttk.LabelFrame(main, text="📖 Your Story", padding=20)
output_card.pack(expand=True, fill="both", pady=10)

output_text = tk.Text(
    output_card,
    wrap="word",
    font=("Segoe UI", 13),
    height=7,
    state="disabled"
)
output_text.pack(side="left", expand=True, fill="both")

scroll = ttk.Scrollbar(output_card, command=output_text.yview)
scroll.pack(side="right", fill="y")
output_text.config(yscrollcommand=scroll.set)

# Actions
actions = ttk.Frame(main)
actions.pack(pady=18)

ttk.Button(actions, text="🎲 Generate Story", command=generate_story,
           style="Primary.TButton").pack(side="left", padx=6)

ttk.Button(actions, text="📋 Copy", command=copy_story).pack(side="left", padx=6)
ttk.Button(actions, text="❓ Help", command=show_help).pack(side="left", padx=6)

ttk.Checkbutton(actions, text="Dark Mode",
                variable=dark_mode_var,
                command=toggle_theme).pack(side="left", padx=14)

# =========================
# Init
# =========================
build_inputs()
story_var.trace_add("write", lambda *a: build_inputs())

# =========================
# Run App
# =========================
root.mainloop()
