import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import random
import sv_ttk
import threading
import time

# =========================
# Helper: Resource Path
# =========================
def resource_path(file_name):
    """Get absolute path for resources (works with PyInstaller)."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Rock–Paper–Scissors Mini-Game")
root.geometry("650x600")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
choices = ["Rock", "Paper", "Scissors"]
icons = {}
user_choice = tk.StringVar(value="None")
computer_choice = tk.StringVar(value="None")
result_var = tk.StringVar(value="Make your move!")
dark_mode_var = tk.BooleanVar(value=False)
shuffling = False  # Prevent multiple clicks during animation

# Scoreboard
score = {"Wins": 0, "Losses": 0, "Ties": 0}
score_label_values = {"Wins": 0, "Losses": 0, "Ties": 0}

# =========================
# Load Icons
# =========================
def load_icons():
    for choice in choices:
        path = resource_path(f"{choice.lower()}.png")
        if os.path.exists(path):
            img = Image.open(path).resize((64, 64), Image.ANTIALIAS)
            icons[choice] = ImageTk.PhotoImage(img)
        else:
            icons[choice] = None

load_icons()

# =========================
# Helper Functions
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def compute_result(user, comp):
    if user == comp:
        return "It's a tie!"
    elif (user == "Rock" and comp == "Scissors") or \
         (user == "Paper" and comp == "Rock") or \
         (user == "Scissors" and comp == "Paper"):
        return "You win! 🎉"
    else:
        return "Computer wins! 💻"

def display_result(user, comp, final_result):
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)

    # Display user choice
    if icons.get(user):
        result_text.image_create(tk.END, image=icons[user])
        result_text.insert(tk.END, f" You chose {user}\n", "user")
    else:
        result_text.insert(tk.END, f"You chose {user}\n", "user")

    # Display computer choice
    if icons.get(comp):
        result_text.image_create(tk.END, image=icons[comp])
        result_text.insert(tk.END, f" Computer chose {comp}\n", "comp")
    else:
        result_text.insert(tk.END, f"Computer chose {comp}\n", "comp")

    # Display final result
    result_text.insert(tk.END, f"\n{final_result}", "result")
    result_text.config(state="disabled")
    result_var.set(final_result)
    update_scoreboard(final_result)
    set_status(f"You chose {user}, Computer chose {comp} -> {final_result}")

# =========================
# Scoreboard
# =========================
def animate_score(key, new_value):
    current = score_label_values[key]
    step = 1 if new_value > current else -1
    for val in range(current + step, new_value + step, step):
        score_label_values[key] = val
        update_scoreboard_label()
        time.sleep(0.05)

def update_scoreboard(result):
    global score_label_values
    score_label_values = {"Wins": score["Wins"], "Losses": score["Losses"], "Ties": score["Ties"]}
    if "win" in result.lower():
        score["Wins"] += 1
        threading.Thread(target=animate_score, args=("Wins", score["Wins"]), daemon=True).start()
    elif "loss" in result.lower():
        score["Losses"] += 1
        threading.Thread(target=animate_score, args=("Losses", score["Losses"]), daemon=True).start()
    else:
        score["Ties"] += 1
        threading.Thread(target=animate_score, args=("Ties", score["Ties"]), daemon=True).start()

def update_scoreboard_label():
    score_label.config(text=f"Wins: {score_label_values['Wins']}  "
                            f"Losses: {score_label_values['Losses']}  "
                            f"Ties: {score_label_values['Ties']}")

# =========================
# Dark Mode Toggle
# =========================
def toggle_theme():
    if dark_mode_var.get():
        root.configure(bg="#2E2E2E")
        style.configure("TLabel", background="#2E2E2E", foreground="white")
        style.configure("TFrame", background="#2E2E2E")
        style.configure("TButton", background="#444444", foreground="white")
        result_text.configure(bg="#3A3A3A", fg="white", insertbackground="white")
        score_label.configure(bg="#2E2E2E", fg="white")
    else:
        root.configure(bg="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="black")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TButton", background="#e0e0e0", foreground="black")
        result_text.configure(bg="white", fg="black", insertbackground="black")
        score_label.configure(bg="#FFFFFF", fg="black")
    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Animate Computer Choice
# =========================
def shuffle_computer(user_choice_selected, iterations=15, delay=50):
    global shuffling
    if shuffling:
        return
    shuffling = True
    count = [0]

    def animate():
        nonlocal count
        if count[0] < iterations:
            temp_choice = random.choice(choices)
            computer_choice.set(temp_choice)
            result_text.config(state="normal")
            result_text.delete("1.0", tk.END)
            if icons.get(user_choice_selected):
                result_text.image_create(tk.END, image=icons[user_choice_selected])
                result_text.insert(tk.END, f" You chose {user_choice_selected}\n", "user")
            else:
                result_text.insert(tk.END, f"You chose {user_choice_selected}\n", "user")
            result_text.insert(tk.END, f" Computer is choosing...\n", "comp")
            result_text.config(state="disabled")
            count[0] += 1
            root.after(delay, animate)
        else:
            final_comp = random.choice(choices)
            computer_choice.set(final_comp)
            final_result = compute_result(user_choice_selected, final_comp)
            display_result(user_choice_selected, final_comp, final_result)
            global shuffling
            shuffling = False

    animate()

def play(choice):
    shuffle_computer(choice)

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 12, "bold"),
                foreground="white", background="#4CAF50", padding=10)
style.map("Action.TButton", background=[("active", "#45a049")])
style.configure("TLabel", font=("Segoe UI", 12))

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w", font=("Segoe UI", 10)).pack(side=tk.BOTTOM, fill="x")

# =========================
# Main Frame
# =========================
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")

ttk.Label(main_frame, text="Rock–Paper–Scissors Mini-Game", font=("Segoe UI", 18, "bold")).pack(pady=10)
ttk.Label(main_frame, text="Choose your move:", font=("Segoe UI", 12)).pack(pady=5)

button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=10)

for c in choices:
    btn = ttk.Button(button_frame, text=c, command=lambda ch=c: play(ch), style="Action.TButton")
    btn.pack(side="left", padx=5)

# Result display
result_text = scrolledtext.ScrolledText(main_frame, height=10, font=("Consolas", 12))
result_text.pack(fill="both", expand=True, pady=15)
result_text.tag_configure("user", foreground="#4CAF50", font=("Consolas", 12, "bold"))
result_text.tag_configure("comp", foreground="#F44336", font=("Consolas", 12, "bold"))
result_text.tag_configure("result", foreground="#2196F3", font=("Consolas", 14, "bold"))
result_text.config(state="disabled")

# Scoreboard
score_label = tk.Label(main_frame, text=f"Wins: 0  Losses: 0  Ties: 0", font=("Segoe UI", 12, "bold"))
score_label.pack(pady=5)

# Dark mode toggle
ttk.Checkbutton(main_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(pady=10)

# =========================
# Run App
# =========================
root.mainloop()
