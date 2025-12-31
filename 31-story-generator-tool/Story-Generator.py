import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sv_ttk
import random
import time

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
root.title("Personalized AI-Assisted Story Generator")
root.geometry("850x720")
root.minsize(850, 720)
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
ai_mode_var = tk.BooleanVar(value=True)
story_title_var = tk.StringVar()
story_prompt_var = tk.StringVar()
story_characters_var = tk.StringVar()
story_settings_var = tk.StringVar()
story_plot_var = tk.StringVar()
story_result_var = tk.StringVar(value="")
story_history = []  # List of tuples: (title, story)

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)
    for entry in [title_entry, prompt_entry, characters_entry, settings_entry, plot_entry]:
        entry.configure(background=bg, foreground=fg)

# =========================
# AI-Assisted Story Generation
# =========================
DEFAULT_CHARACTERS = ["a brave knight", "a curious child", "an old wizard", "a fearless explorer", "a clever detective"]
DEFAULT_SETTINGS = ["in a distant kingdom", "on a mysterious island", "in a bustling city", "inside a magical forest", "under the deep sea"]
DEFAULT_PLOTS = ["faces a great challenge", "discovers a hidden secret", "must save a friend", "encounters a mysterious enemy", "uncovers an ancient artifact"]
RESOLUTIONS = ["overcomes the obstacle", "finds a surprising ally", "learns an important lesson", "achieves their dream", "restores peace to the land"]
DETAILS = [
    "The sky was painted with shades of orange and violet as the sun set.",
    "A chilling wind whispered secrets through the trees.",
    "Footsteps echoed in the empty hallways.",
    "A mysterious artifact glowed faintly in the moonlight.",
    "Laughter and music filled the distant town."
]
DIALOGUE = [
    '"I never thought this day would come," said the character.',
    '"We must act quickly before it is too late!"',
    '"Do not fear, together we can face anything."',
    '"What lies beyond that door may change everything..."'
]

def parse_user_input(input_str, default_list):
    items = [i.strip() for i in input_str.split(",") if i.strip()]
    return items if items else default_list

def generate_ai_paragraph(title, prompt, characters, settings, plots):
    char = random.choice(characters)
    setting = random.choice(settings)
    plot = random.choice(plots)
    resolution = random.choice(RESOLUTIONS)
    detail = random.choice(DETAILS)
    dialogue = random.choice(DIALOGUE)
    
    paragraph = (
        f"{title} begins with {char} {setting}. {detail} "
        f"One day, {char} {plot} related to {prompt}. "
        f"{dialogue} Finally, {char} {resolution}."
    )
    return paragraph

def generate_ai_story(title, prompt, characters_input, settings_input, plot_input, paragraphs=4):
    characters = parse_user_input(characters_input, DEFAULT_CHARACTERS)
    settings = parse_user_input(settings_input, DEFAULT_SETTINGS)
    plots = parse_user_input(plot_input, DEFAULT_PLOTS)
    
    story = []
    for _ in range(paragraphs):
        story.append(generate_ai_paragraph(title, prompt, characters, settings, plots))
    return "\n\n".join(story)

def generate_basic_story(title, prompt, paragraphs=3):
    templates = [
        "Once upon a time, {title} {prompt} ... And then something unexpected happened!",
        "In a land far away, {title} faced a challenge: {prompt}. What happens next will amaze you!",
        "{title} was just an ordinary character until {prompt}. The adventure begins.",
        "Long ago, in a world unknown, {title} discovered that {prompt}. This changed everything."
    ]
    story = []
    for _ in range(paragraphs):
        template = random.choice(templates)
        story.append(template.format(title=title, prompt=prompt))
    return "\n\n".join(story)

# =========================
# Story Generation & History
# =========================
def create_story():
    title = story_title_var.get().strip()
    prompt = story_prompt_var.get().strip()
    characters_input = story_characters_var.get()
    settings_input = story_settings_var.get()
    plot_input = story_plot_var.get()

    if not title or not prompt:
        messagebox.showwarning("Missing Input", "Please enter at least a story title and a prompt.")
        return

    set_status("Generating story...")
    threading.Thread(target=_generate_story_thread, args=(title, prompt, characters_input, settings_input, plot_input), daemon=True).start()

def _generate_story_thread(title, prompt, characters_input, settings_input, plot_input):
    if ai_mode_var.get():
        story = generate_ai_story(
            title, prompt, characters_input, settings_input, plot_input, paragraphs=random.randint(4, 7)
        )
    else:
        story = generate_basic_story(title, prompt, paragraphs=random.randint(3, 5))
    
    story_result_var.set(story)
    add_to_history(title, story)
    set_status("Story generated!")

def add_to_history(title, story):
    story_history.append((title, story))
    preview = story.split("\n\n")[0][:100].replace("\n", " ")  # first 100 chars
    history_list.insert(tk.END, f"{title}: {preview}...")

def export_history_txt():
    if not story_history:
        messagebox.showinfo("Empty History", "No stories to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Export Story History"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Personalized AI-Assisted Story Generator History\n")
            f.write("=" * 50 + "\n\n")
            for i, (title, story) in enumerate(story_history, 1):
                f.write(f"{i}. Title: {title}\n")
                f.write(f"   Story:\n{story}\n\n")
        set_status("Story history exported")
        messagebox.showinfo("Export Successful", "Story history saved successfully.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

# =========================
# Scrollable Story Viewer with Typing Effect
# =========================
def view_selected_story(event=None):
    selection = history_list.curselection()
    if not selection:
        messagebox.showinfo("No Selection", "Please select a story from the history vault.")
        return
    index = selection[0]
    title, story = story_history[index]

    story_window = tk.Toplevel(root)
    story_window.title(f"Full Story - {title}")
    story_window.geometry("800x600")
    story_window.rowconfigure(0, weight=1)
    story_window.columnconfigure(0, weight=1)

    # Make it modal
    story_window.transient(root)  # Keep above main window
    story_window.grab_set()       # Block interaction with main window

    frame = ttk.Frame(story_window, padding=10)
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

    paragraphs = story.split("\n\n")
    
    def type_paragraph(idx=0):
        if idx >= len(paragraphs):
            text_widget.configure(state="disabled")
            # Release modal behavior when typing finished
            story_window.grab_release()
            return
        
        text = paragraphs[idx]
        char_idx = 0
        
        def type_char():
            nonlocal char_idx
            if char_idx < len(text):
                text_widget.insert(tk.END, text[char_idx])
                text_widget.see(tk.END)
                char_idx += 1
                text_widget.after(5, type_char)
            else:
                text_widget.insert(tk.END, "\n\n")
                text_widget.after(200, lambda: type_paragraph(idx+1))
        
        type_char()
    
    type_paragraph()
    story_window.focus()

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

ttk.Label(main, text="Personalized AI-Assisted Story Generator", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="ew", pady=(0,10))

# Inputs
ttk.Label(main, text="Story Title:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
title_entry = ttk.Entry(main, textvariable=story_title_var, font=("Segoe UI", 14))
title_entry.grid(row=2, column=0, sticky="ew", pady=2)

ttk.Label(main, text="Story Prompt/Theme:", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
prompt_entry = ttk.Entry(main, textvariable=story_prompt_var, font=("Segoe UI", 14))
prompt_entry.grid(row=4, column=0, sticky="ew", pady=2)

ttk.Label(main, text="Characters (comma-separated, optional):", font=("Segoe UI", 12)).grid(row=5, column=0, sticky="w")
characters_entry = ttk.Entry(main, textvariable=story_characters_var, font=("Segoe UI", 12))
characters_entry.grid(row=6, column=0, sticky="ew", pady=2)

ttk.Label(main, text="Settings/Locations (comma-separated, optional):", font=("Segoe UI", 12)).grid(row=7, column=0, sticky="w")
settings_entry = ttk.Entry(main, textvariable=story_settings_var, font=("Segoe UI", 12))
settings_entry.grid(row=8, column=0, sticky="ew", pady=2)

ttk.Label(main, text="Plot Elements (comma-separated, optional):", font=("Segoe UI", 12)).grid(row=9, column=0, sticky="w")
plot_entry = ttk.Entry(main, textvariable=story_plot_var, font=("Segoe UI", 12))
plot_entry.grid(row=10, column=0, sticky="ew", pady=2)

# Controls
controls = ttk.Frame(main)
controls.grid(row=11, column=0, sticky="ew", pady=8)
controls.columnconfigure((0,1), weight=1)

ttk.Button(controls, text="📖 Generate Story", command=create_story, style="Action.TButton").grid(row=0, column=0, padx=4, sticky="ew")
ttk.Button(controls, text="📤 Export History", command=export_history_txt, style="Action.TButton").grid(row=0, column=1, padx=4, sticky="ew")

# Story History Vault
vault = ttk.LabelFrame(main, text="Story History Vault", padding=10)
vault.grid(row=12, column=0, sticky="nsew", pady=10)
main.rowconfigure(12, weight=1)

history_list = tk.Listbox(vault, font=("Segoe UI", 10), height=7)
history_list.pack(fill="both", expand=True)
history_list.bind("<Double-Button-1>", view_selected_story)

# Options
options_frame = ttk.Frame(main)
options_frame.grid(row=13, column=0, sticky="w", pady=6)
ttk.Checkbutton(options_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(side="left", padx=(0,10))
ttk.Checkbutton(options_frame, text="AI-Assisted Mode", variable=ai_mode_var).pack(side="left")

# =========================
# Run App
# =========================
root.mainloop()
