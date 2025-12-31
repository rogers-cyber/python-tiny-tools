import sys
import os
import tkinter as tk
from tkinter import messagebox
import random

# =========================
# THEME
# =========================
APP_BG = "#121212"
PANEL_BG = "#1F1F1F"
BTN_BG = "#2C2C2C"
ACCENT = "#FF6F61"
TEXT_CLR = "#E0E0E0"
SUBTEXT_CLR = "#AAAAAA"
INPUT_BG = "#333333"
INPUT_FG = "#FFFFFF"

FONT = ("Segoe UI", 11)

# =========================
# APP
# =========================
class RandomStoryTitleApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Random Story Title Generator")
        root.geometry("1000x580")
        root.configure(bg=APP_BG)
        root.resizable(False, False)

        # =========================
        # LEFT PANEL
        # =========================
        left = tk.Frame(root, bg=PANEL_BG, width=420)
        left.pack(side="left", fill="y")

        header = tk.Frame(left, bg=PANEL_BG)
        header.pack(fill="x", padx=16, pady=(18, 10))

        tk.Label(
            header,
            text="MateTools",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Segoe UI", 20, "bold")
        ).pack(side="left")

        tk.Frame(left, bg=ACCENT, height=2).pack(fill="x", padx=16, pady=(0, 14))

        tk.Label(
            left,
            text="Random Story Title Generator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Generate epic fantasy or modern thriller titles",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # =========================
        # STYLE SELECTION
        # =========================
        tk.Label(left, text="Select Style:", bg=PANEL_BG, fg=TEXT_CLR, font=FONT).pack(anchor="w", padx=16, pady=(0,4))
        self.style_var = tk.StringVar(value="Epic Fantasy")
        style_menu = tk.OptionMenu(left, self.style_var, "Epic Fantasy", "Modern Thriller")
        style_menu.config(bg=BTN_BG, fg="white", relief="flat", font=FONT, width=40)
        style_menu["menu"].config(bg=PANEL_BG, fg=TEXT_CLR)
        style_menu.pack(anchor="w", padx=16, pady=(0,16))

        # =========================
        # BUTTONS
        # =========================
        btn_frame = tk.Frame(left, bg=PANEL_BG)
        btn_frame.pack(fill="x", padx=16, pady=16)

        def make_btn(text, cmd, color=BTN_BG):
            return tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg=color,
                fg="white",
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                height=2,
                width=20
            )

        make_btn("Generate Story Title", self.generate_title, ACCENT).pack(side="top", pady=8)
        make_btn("Copy Title", self.copy_title, BTN_BG).pack(side="top", pady=8)
        make_btn("About", self.show_about, BTN_BG).pack(side="top", pady=20)

        # =========================
        # RIGHT PANEL
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        self.result_card = tk.Frame(right, bg=PANEL_BG)
        self.result_card.pack(padx=30, pady=40, fill="both", expand=True)

        tk.Label(
            self.result_card,
            text="Generated Title",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(20, 10))

        self.title_label = tk.Label(
            self.result_card,
            text="--",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Segoe UI", 18, "bold"),
            wraplength=500,
            justify="center"
        )
        self.title_label.pack(pady=40)

        # Store current title
        self.current_title = ""

        # =========================
        # WORD POOLS FOR STYLES
        # =========================
        self.word_pools = {
            "Epic Fantasy": {
                "adjectives": [
                    "Lost", "Hidden", "Dark", "Silent", "Mysterious", "Forgotten", "Enchanted",
                    "Shimmering", "Forsaken", "Crimson", "Eternal", "Haunted", "Sacred", "Cursed",
                    "Glorious", "Majestic", "Fallen", "Infinite", "Broken", "Burning", "Whispering",
                    "Frozen", "Twisted", "Radiant", "Ancient", "Lonely", "Stormy", "Golden", "Silver",
                    "Bleak", "Wild", "Secret", "Vengeful", "Peaceful", "Sinister", "Veiled",
                    "Shattered", "Celestial", "Arcane", "Luminous", "Obsidian", "Fading"
                ],
                "nouns": [
                    "Kingdom", "Forest", "Legacy", "Prophecy", "Journey", "Secret", "Night", "Treasure",
                    "Empire", "Dragon", "Coven", "Throne", "Labyrinth", "Moon", "Star", "Crown", "Shadow",
                    "Sword", "Flame", "Horizon", "Temple", "River", "Tower", "City", "Sea", "Island",
                    "Mountain", "Valley", "Garden", "Catacomb", "Scroll", "Book", "Key", "Mirror",
                    "Portal", "Beacon", "Oath", "Revelation", "Curse", "Blessing", "Chamber", "Legend"
                ],
                "actions": [
                    "Awakens", "Rises", "Falls", "Returns", "Hides", "Whispers", "Shines", "Calls",
                    "Beckons", "Slumbers", "Fades", "Burns", "Echoes", "Dances", "Cries", "Summons",
                    "Dreams", "Flees", "Blooms", "Shatters", "Reigns", "Hunts", "Glows", "Drifts",
                    "Wanders", "Bleeds", "Spreads", "Roars", "Shimmers", "Forges", "Breaks"
                ]
            },
            "Modern Thriller": {
                "adjectives": [
                    "Cold", "Silent", "Deadly", "Hidden", "Dark", "Criminal", "Dangerous", "Lost",
                    "Vanishing", "Suspicious", "Shadowy", "Secret", "Twisted", "Final", "Unknown",
                    "Fractured", "Broken", "Relentless", "Urgent", "Fierce", "Fatal", "Urgent"
                ],
                "nouns": [
                    "File", "Case", "Witness", "City", "Night", "Agent", "Truth", "Secret",
                    "Evidence", "Shadow", "Crime", "Code", "Law", "Network", "Target", "Enemy",
                    "Conspiracy", "Identity", "Report", "Mystery"
                ],
                "actions": [
                    "Hunts", "Flees", "Exposes", "Catches", "Chases", "Unfolds", "Reveals",
                    "Escapes", "Targets", "Stalks", "Warns", "Fights", "Tracks", "Breaks",
                    "Confronts", "Shadows"
                ]
            }
        }

    # =========================
    # METHODS
    # =========================
    def generate_title(self):
        style = self.style_var.get()
        pool = self.word_pools[style]

        # Randomly choose 1–2 adjectives
        adjectives = random.sample(pool["adjectives"], random.choice([1, 2]))
        # Randomly choose 1–2 nouns
        nouns = random.sample(pool["nouns"], random.choice([1, 2]))
        # Randomly choose 1–2 actions
        actions = random.sample(pool["actions"], random.choice([1, 2]))

        self.current_title = "The " + " ".join(adjectives + nouns + actions)
        self.title_label.config(text=self.current_title)

    def copy_title(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_title)
        messagebox.showinfo("Copied", f"'{self.current_title}' copied to clipboard!")

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Random Story Title Generator\n\n"
            "• Generate epic fantasy or modern thriller titles\n"
            "• Titles now have 4–6 words for realism\n"
            "• Copy titles to clipboard\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    RandomStoryTitleApp(root)
    root.mainloop()
