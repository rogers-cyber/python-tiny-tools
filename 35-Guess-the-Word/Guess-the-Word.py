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

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Animated Hangman Game")
root.geometry("700x850")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
word_list = ["PYTHON", "HANGMAN", "COMPUTER", "AI", "PROGRAMMING", "DEVELOPER"]
current_word = ""
guessed_letters = set()
wrong_guesses = 0
max_wrong = 6
display_word_var = tk.StringVar()
status_var = tk.StringVar(value="Ready")
lives_var = tk.StringVar(value=f"Lives: {max_wrong}")

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"
    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)
    guess_entry.configure(background=bg, foreground=fg)
    hangman_canvas.configure(bg=bg)

# =========================
# Game Logic
# =========================
def start_new_game():
    global current_word, guessed_letters, wrong_guesses
    current_word = random.choice(word_list).upper()
    guessed_letters = set()
    wrong_guesses = 0
    update_display_word()
    lives_var.set(f"Lives: {max_wrong - wrong_guesses}")
    draw_hangman(animated=False)
    set_status("New game started! Guess a letter.")

def update_display_word():
    display = " ".join([c if c in guessed_letters else "_" for c in current_word])
    display_word_var.set(display)
    if "_" not in display:
        set_status("Congratulations! You guessed the word!")
        messagebox.showinfo("Winner!", f"You correctly guessed: {current_word}")

def guess_letter():
    global wrong_guesses
    letter = guess_var.get().strip().upper()
    guess_var.set("")
    if not letter or len(letter) != 1 or not letter.isalpha():
        set_status("Please enter a single letter.")
        return
    if letter in guessed_letters:
        set_status(f"You already guessed '{letter}'.")
        return
    guessed_letters.add(letter)
    if letter not in current_word:
        wrong_guesses += 1
        lives_var.set(f"Lives: {max_wrong - wrong_guesses}")
        set_status(f"Wrong guess! {max_wrong - wrong_guesses} tries left.")
        draw_hangman(animated=True)
        if wrong_guesses >= max_wrong:
            messagebox.showinfo("Game Over", f"You lost! The word was: {current_word}")
            start_new_game()
            return
    update_display_word()

# =========================
# Hangman Drawing with Animation
# =========================
def draw_hangman(animated=True):
    hangman_canvas.delete("all")
    # Base
    hangman_canvas.create_line(50, 350, 250, 350, width=3)
    # Pole
    hangman_canvas.create_line(150, 350, 150, 50, width=3)
    hangman_canvas.create_line(150, 50, 300, 50, width=3)
    hangman_canvas.create_line(300, 50, 300, 100, width=3)

    parts = []
    if wrong_guesses >= 1:  # Head
        parts.append(("oval", 275, 100, 325, 150))
    if wrong_guesses >= 2:  # Body
        parts.append(("line", 300, 150, 300, 250))
    if wrong_guesses >= 3:  # Left Arm
        parts.append(("line", 300, 170, 250, 200))
    if wrong_guesses >= 4:  # Right Arm
        parts.append(("line", 300, 170, 350, 200))
    if wrong_guesses >= 5:  # Left Leg
        parts.append(("line", 300, 250, 250, 300))
    if wrong_guesses >= 6:  # Right Leg
        parts.append(("line", 300, 250, 350, 300))

    if animated:
        animate_parts(parts)
    else:
        for p in parts:
            if p[0] == "oval":
                hangman_canvas.create_oval(*p[1:], width=3)
            elif p[0] == "line":
                hangman_canvas.create_line(*p[1:], width=3)

def animate_parts(parts, idx=0):
    if idx >= len(parts):
        return
    p = parts[idx]
    if p[0] == "oval":
        # Animate head as growing circle
        x1, y1, x2, y2 = p[1:]
        for i in range(0, 101, 5):
            hangman_canvas.after(i, lambda x1=x1, y1=y1, x2=x2, y2=y2: hangman_canvas.create_oval(x1, y1, x2, y2, width=3))
    elif p[0] == "line":
        # Animate line drawing in steps
        x1, y1, x2, y2 = p[1:]
        steps = 20
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        for i in range(1, steps + 1):
            hangman_canvas.after(i * 20, lambda i=i, x1=x1, y1=y1, dx=dx, dy=dy: hangman_canvas.create_line(x1, y1, x1 + dx * i, y1 + dy * i, width=3))
    hangman_canvas.after(400, lambda: animate_parts(parts, idx + 1))

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=8)

# =========================
# UI Layout
# =========================
main = ttk.Frame(root, padding=20)
main.pack(expand=True, fill="both")
main.columnconfigure(0, weight=1)

ttk.Label(main, text="Animated Hangman Game", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="ew", pady=(0,10))

# Hangman Canvas
hangman_canvas = tk.Canvas(main, width=400, height=400, bg="white")
hangman_canvas.grid(row=1, column=0, pady=10)

# Word display
ttk.Label(main, textvariable=display_word_var, font=("Segoe UI", 28)).grid(row=2, column=0, pady=20)

# Lives display
ttk.Label(main, textvariable=lives_var, font=("Segoe UI", 16, "bold")).grid(row=3, column=0, pady=5)

# Letter input
input_frame = ttk.Frame(main)
input_frame.grid(row=4, column=0, pady=10)
guess_var = tk.StringVar()
guess_entry = ttk.Entry(input_frame, textvariable=guess_var, font=("Segoe UI", 16), width=5)
guess_entry.pack(side="left", padx=(0,10))
ttk.Button(input_frame, text="Guess", command=guess_letter, style="Action.TButton").pack(side="left")

# Controls
controls = ttk.Frame(main)
controls.grid(row=5, column=0, pady=10, sticky="ew")
ttk.Button(controls, text="New Game", command=start_new_game, style="Action.TButton").pack(side="left")

# Options
options_frame = ttk.Frame(main)
options_frame.grid(row=6, column=0, sticky="w", pady=6)
ttk.Checkbutton(options_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(side="left")

# Status Bar
ttk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill="x")

# =========================
# Run App
# =========================
start_new_game()
root.mainloop()
