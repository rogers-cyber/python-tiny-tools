import sys
import os
import threading
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

def delayed_update(event=None):
    threading.Timer(0.1, update_ui).start()

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("AdventureQuest")
root.geometry("900x600")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)

story_var = tk.StringVar(value="Welcome to AdventureQuest!\nYour journey begins...\n")
action_var = tk.StringVar()

player = {
    "health": 100,
    "gold": 0,
    "location": "forest",
    "attack": 10,
}

inventory = []

locations = {
    "forest": {
        "description": "You are in a dark forest. Paths lead north and east.",
        "actions": {"north": "cave", "east": "village"}
    },
    "cave": {
        "description": "A spooky cave. You see a shiny sword.",
        "actions": {"south": "forest", "take sword": None}
    },
    "village": {
        "description": "A small village with friendly villagers.",
        "actions": {"west": "forest", "shop": None}
    },
}

enemies = {
    "forest": {"Goblin": {"health": 30, "attack": 5}, "Wolf": {"health": 25, "attack": 6}},
    "cave": {"Bat": {"health": 20, "attack": 4}, "Skeleton": {"health": 40, "attack": 8}},
}

treasures = {
    "forest": ["gold coin", "healing herb"],
    "cave": ["gold coin", "magic potion"],
    "village": ["gold coin"]
}

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
# Game Logic
# =========================
def update_ui():
    location = player["location"]
    loc_info = locations[location]
    story_text = f"{loc_info['description']}\n"
    story_text += f"\nHealth: {player['health']} | Gold: {player['gold']} | Inventory: {', '.join(inventory) if inventory else 'Empty'}"
    story_var.set(story_text)

def encounter_enemy():
    location = player["location"]
    if location in enemies and random.random() < 0.6:  # 60% chance
        enemy_name = random.choice(list(enemies[location].keys()))
        enemy = enemies[location][enemy_name]
        set_status(f"⚔️ You encounter a {enemy_name}!")
        combat(enemy_name, enemy)

def find_treasure():
    location = player["location"]
    if location in treasures and random.random() < 0.5:  # 50% chance
        item = random.choice(treasures[location])
        inventory.append(item)
        set_status(f"💎 You found a {item}!")

def combat(enemy_name, enemy):
    while enemy["health"] > 0 and player["health"] > 0:
        damage = player["attack"] + (5 if "sword" in inventory else 0)
        enemy["health"] -= damage
        set_status(f"You hit {enemy_name} for {damage} damage!")
        root.update()
        root.after(500)

        if enemy["health"] <= 0:
            gold_found = random.randint(5, 20)
            player["gold"] += gold_found
            set_status(f"🎉 You defeated {enemy_name} and gained {gold_found} gold!")
            root.update()
            root.after(500)
            return

        # Enemy attacks
        player["health"] -= enemy["attack"]
        set_status(f"{enemy_name} hits you for {enemy['attack']} damage!")
        root.update()
        root.after(500)

        if player["health"] <= 0:
            set_status("💀 You were defeated! Game over.")
            messagebox.showinfo("Game Over", "You have died! Restarting game...")
            reset_game()
            return

def reset_game():
    player["health"] = 100
    player["gold"] = 0
    player["location"] = "forest"
    inventory.clear()
    update_ui()

def process_action():
    action = action_var.get().strip().lower()
    location = player["location"]
    loc_info = locations[location]
    valid_actions = loc_info["actions"]

    if action in valid_actions:
        # Move to another location
        if valid_actions[action]:
            player["location"] = valid_actions[action]
            set_status(f"You move to {valid_actions[action].capitalize()}.")
            encounter_enemy()
            find_treasure()
        else:
            # Special actions
            if action == "take sword" and "sword" not in inventory:
                inventory.append("sword")
                set_status("🗡 You picked up the sword!")
            elif action == "shop":
                if player["gold"] >= 10:
                    player["gold"] -= 10
                    inventory.append("potion")
                    set_status("💊 You bought a healing potion!")
                else:
                    set_status("Not enough gold!")
    else:
        set_status("❌ Invalid action!")

    action_var.set("")
    update_ui()

# =========================
# Help Window
# =========================
def show_help():
    win = tk.Toplevel(root)
    win.title("AdventureQuest - Help")
    win.geometry("480x360")
    win.configure(bg="#2e2e2e")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

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

    help_text = """🗺 AdventureQuest — Quick Help

• Read the story in the main window.
• Type actions (commands) in the input box:
  - Directions: north, south, east, west
  - Special: take sword, shop, etc.
• Combat occurs randomly when exploring.
• You can find treasures randomly.
• Press 'Enter' or click 'Act' to perform action.
• Keep track of health, gold, and inventory.

Your adventure awaits!"""
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

ttk.Label(main, text="AdventureQuest", font=("Segoe UI", 22, "bold")).pack()
ttk.Label(main, text="A text-based adventure game", font=("Segoe UI", 11)).pack(pady=(0, 10))

# =========================
# Text Area
# =========================
text_frame = ttk.LabelFrame(main, text="Story", padding=10)
text_frame.pack(fill="both", pady=10, expand=True)

text_area = tk.Text(
    text_frame,
    font=("Segoe UI", 11),
    wrap="word",
    height=15,
    state="disabled"
)
text_area.pack(fill="both", expand=True)

def refresh_story(*args):
    text_area.config(state="normal")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", story_var.get())
    text_area.config(state="disabled")

story_var.trace_add("write", refresh_story)

# =========================
# Action Input
# =========================
action_frame = ttk.Frame(main)
action_frame.pack(fill="x", pady=8)

ttk.Label(action_frame, text="Your Action:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 6))

action_entry = ttk.Entry(action_frame, textvariable=action_var, width=30)
action_entry.pack(side="left", padx=(0, 6))
action_entry.bind("<Return>", lambda e: process_action())

ttk.Button(action_frame, text="Act", command=process_action, style="Action.TButton").pack(side="left", padx=6)
ttk.Button(action_frame, text="❓ Help", command=show_help, style="Action.TButton").pack(side="left", padx=6)

ttk.Checkbutton(
    action_frame,
    text="Dark Mode",
    variable=dark_mode_var,
    command=toggle_theme
).pack(side="right", padx=14)

# =========================
# Start Game
# =========================
update_ui()
root.mainloop()
