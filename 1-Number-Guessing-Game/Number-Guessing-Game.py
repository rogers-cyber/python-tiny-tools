import sys
import os
import random
import json
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

# =========================
# Resource Path Helper
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# Globals
# =========================
root = tk.Tk()
root.title("Number Guessing Game with Leaderboard & Stats")
root.geometry("750x600")
# root.iconbitmap(resource_path("logo.ico"))

sv_ttk.set_theme("light")

target_number = None
attempts = 0
max_attempts = 0
score = 0
number_range = (1, 100)
dark_mode_var = tk.BooleanVar(value=False)
difficulty_var = tk.StringVar(value="Medium")

leaderboard_file = resource_path("leaderboard.json")
stats_file = resource_path("player_stats.json")
leaderboard_data = []
player_stats = {
    "total_games": 0,
    "attempts_list": [],
    "high_score_streak": 0,
    "current_streak": 0
}

# =========================
# Helper Functions
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def toggle_theme():
    style.theme_use("clam")
    if dark_mode_var.get():
        root.configure(bg="#2E2E2E")
        style.configure("TLabel", background="#2E2E2E", foreground="white")
        style.configure("TFrame", background="#2E2E2E")
        style.configure("TButton", background="#4CAF50", foreground="white")
        style.configure("Treeview", background="#3C3C3C", foreground="white", fieldbackground="#3C3C3C")
    else:
        root.configure(bg="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="black")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TButton", background="#4CAF50", foreground="white")
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
    update_leaderboard_tree()
    update_stats_labels()
    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Leaderboard Functions
# =========================
def load_leaderboard():
    global leaderboard_data
    if os.path.exists(leaderboard_file):
        try:
            with open(leaderboard_file, "r", encoding="utf-8") as f:
                leaderboard_data = json.load(f)
        except:
            leaderboard_data = []
    else:
        leaderboard_data = []

def save_leaderboard():
    with open(leaderboard_file, "w", encoding="utf-8") as f:
        json.dump(leaderboard_data, f, indent=4)

def update_leaderboard_tree():
    for row in leaderboard_tree.get_children():
        leaderboard_tree.delete(row)
    for entry in sorted(leaderboard_data, key=lambda x: x["score"], reverse=True)[:10]:
        leaderboard_tree.insert("", "end", values=(entry["name"], entry["score"], entry["difficulty"]))

# =========================
# Player Stats Functions
# =========================
def load_stats():
    global player_stats
    if os.path.exists(stats_file):
        try:
            with open(stats_file, "r", encoding="utf-8") as f:
                player_stats = json.load(f)
        except:
            player_stats = {
                "total_games": 0,
                "attempts_list": [],
                "high_score_streak": 0,
                "current_streak": 0
            }
    else:
        player_stats = {
            "total_games": 0,
            "attempts_list": [],
            "high_score_streak": 0,
            "current_streak": 0
        }

def save_stats():
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(player_stats, f, indent=4)

def update_stats_labels():
    total_games_label.config(text=f"Total Games Played: {player_stats['total_games']}")
    avg_attempts = (sum(player_stats['attempts_list']) / len(player_stats['attempts_list'])) if player_stats['attempts_list'] else 0
    avg_attempts_label.config(text=f"Average Attempts per Game: {avg_attempts:.2f}")
    high_streak_label.config(text=f"High Score Streak: {player_stats['high_score_streak']}")

# =========================
# Difficulty & Game Logic
# =========================
def set_difficulty():
    global max_attempts, number_range
    diff = difficulty_var.get()
    if diff == "Easy":
        max_attempts = 15
        number_range = (1, 50)
    elif diff == "Medium":
        max_attempts = 10
        number_range = (1, 100)
    elif diff == "Hard":
        max_attempts = 5
        number_range = (1, 200)
    start_game()

def start_game():
    global target_number, attempts
    target_number = random.randint(*number_range)
    attempts = 0
    feedback_label.config(text="")
    attempts_label.config(text=f"Attempts left: {max_attempts}")
    guess_entry.delete(0, tk.END)
    set_status(f"New game! Guess a number between {number_range[0]} and {number_range[1]}.")

def check_guess():
    global attempts, score
    guess = guess_entry.get()
    if not guess.isdigit():
        messagebox.showwarning("Invalid Input", "Please enter a valid number!")
        return
    guess = int(guess)
    attempts += 1
    remaining = max_attempts - attempts
    diff = abs(target_number - guess)

    if guess < target_number:
        hint = "📉 Too low!"
    elif guess > target_number:
        hint = "📈 Too high!"
    else:
        hint = f"🎉 Correct! The number was {target_number}"
        points = max(0, 100 - attempts * 5)
        update_score(points)
        feedback_label.config(text=hint)
        save_score_dialog()
        return

    if diff <= 2:
        hint += " 🔥 Very close!"
    elif diff <= 5:
        hint += " 😊 Close!"

    feedback_label.config(text=hint)

    if remaining <= 0:
        feedback_label.config(text=f"💥 Game Over! The number was {target_number}")
        set_status("Game Over! Start a new game.")

    else:
        attempts_label.config(text=f"Attempts left: {remaining}")
        set_status(f"Attempts used: {attempts}, remaining: {remaining}")

def update_score(points):
    global score
    score += points
    score_label.config(text=f"Score: {score}")

# =========================
# Score Saving
# =========================
def save_score_dialog():
    def save_name():
        name = name_entry.get().strip()
        if name:
            # Update leaderboard
            leaderboard_data.append({
                "name": name,
                "score": score,
                "difficulty": difficulty_var.get()
            })
            save_leaderboard()
            update_leaderboard_tree()
            # Update player stats
            player_stats['total_games'] += 1
            player_stats['attempts_list'].append(attempts)
            # High score streak logic (score >= 80)
            if score >= 80:
                player_stats['current_streak'] += 1
                player_stats['high_score_streak'] = max(player_stats['high_score_streak'], player_stats['current_streak'])
            else:
                player_stats['current_streak'] = 0
            save_stats()
            update_stats_labels()
            dialog.destroy()
        else:
            messagebox.showwarning("Invalid Input", "Please enter your name.")

    dialog = tk.Toplevel(root)
    dialog.title("Save Score")
    dialog.geometry("300x150")
    ttk.Label(dialog, text=f"Congratulations! Score: {score}", font=("Segoe UI", 12)).pack(pady=10)
    ttk.Label(dialog, text="Enter your name:", font=("Segoe UI", 11)).pack(pady=5)
    name_entry = ttk.Entry(dialog, font=("Segoe UI", 12))
    name_entry.pack(pady=5)
    ttk.Button(dialog, text="Save", command=save_name, style="Action.TButton").pack(pady=5)
    dialog.grab_set()

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#4CAF50", padding=8)
style.map("Action.TButton", background=[("active", "#45a049")])

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Welcome to Number Guessing Game!")
ttk.Label(root, textvariable=status_var, anchor="w", font=("Segoe UI", 10)).pack(side=tk.BOTTOM, fill="x")

# =========================
# Notebook
# =========================
tabs = ttk.Notebook(root)
tabs.pack(expand=True, fill="both", padx=20, pady=20)

# =========================
# Game Tab
# =========================
game_tab = ttk.Frame(tabs, padding=20)
tabs.add(game_tab, text="🎮 Play Game")

# Difficulty
ttk.Label(game_tab, text="Select Difficulty:", font=("Segoe UI", 12)).pack(pady=(5,2))
ttk.Combobox(game_tab, textvariable=difficulty_var, values=["Easy","Medium","Hard"],
             state="readonly", font=("Segoe UI", 12)).pack(pady=2)
ttk.Button(game_tab, text="Apply Difficulty", command=set_difficulty, style="Action.TButton").pack(pady=5)

# Guess input
ttk.Label(game_tab, text="Enter your guess:", font=("Segoe UI", 12)).pack(pady=(10,5))
guess_entry = ttk.Entry(game_tab, font=("Segoe UI", 14))
guess_entry.pack(pady=5)

# Feedback, attempts, score
feedback_label = ttk.Label(game_tab, text="", font=("Segoe UI", 12, "bold"))
feedback_label.pack(pady=10)
attempts_label = ttk.Label(game_tab, text=f"Attempts left: {max_attempts}", font=("Segoe UI", 12))
attempts_label.pack(pady=5)
score_label = ttk.Label(game_tab, text=f"Score: {score}", font=("Segoe UI", 12, "bold"))
score_label.pack(pady=5)

# Buttons
ttk.Button(game_tab, text="Start New Game", command=start_game, style="Action.TButton").pack(pady=5)
ttk.Button(game_tab, text="Submit Guess", command=check_guess, style="Action.TButton").pack(pady=5)

# Dark Mode
ttk.Checkbutton(game_tab, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(pady=10)

# =========================
# Leaderboard Tab
# =========================
leader_tab = ttk.Frame(tabs, padding=20)
tabs.add(leader_tab, text="🏆 Leaderboard")

leaderboard_tree = ttk.Treeview(leader_tab, columns=("Name", "Score", "Difficulty"), show="headings", height=15)
leaderboard_tree.heading("Name", text="Name")
leaderboard_tree.heading("Score", text="Score")
leaderboard_tree.heading("Difficulty", text="Difficulty")
leaderboard_tree.pack(fill="both", expand=True, pady=10)

# =========================
# Stats Tab
# =========================
stats_tab = ttk.Frame(tabs, padding=20)
tabs.add(stats_tab, text="📊 Player Stats")

total_games_label = ttk.Label(stats_tab, text="Total Games Played: 0", font=("Segoe UI", 12))
total_games_label.pack(pady=5)
avg_attempts_label = ttk.Label(stats_tab, text="Average Attempts per Game: 0", font=("Segoe UI", 12))
avg_attempts_label.pack(pady=5)
high_streak_label = ttk.Label(stats_tab, text="High Score Streak: 0", font=("Segoe UI", 12))
high_streak_label.pack(pady=5)

# =========================
# Run App
# =========================
load_leaderboard()
load_stats()
update_leaderboard_tree()
update_stats_labels()
set_difficulty()
root.mainloop()
