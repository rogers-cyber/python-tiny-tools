import sys
import os
import random
import tkinter as tk
from tkinter import messagebox

# =========================
# THEME
# =========================
APP_BG = "#121212"
PANEL_BG = "#1F1F1F"
BTN_BG = "#2C2C2C"
ACCENT = "#FF6F61"
TEXT_CLR = "#E0E0E0"
SUBTEXT_CLR = "#AAAAAA"
BALL_BG = "#333333"
BALL_FG = "#FFFFFF"

FONT = ("Segoe UI", 11)

# =========================
# LOTTERY CONFIG
# =========================
LOTTERY_PRESETS = {
    "Powerball": {"main_numbers": (1, 69), "main_count": 5, "special_numbers": (1, 26), "special_count": 1},
    "Mega Millions": {"main_numbers": (1, 70), "main_count": 5, "special_numbers": (1, 25), "special_count": 1},
}

# =========================
# APP
# =========================
class LotteryGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Lottery Number Generator")
        root.geometry("1000x520")
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
            text="Lottery Number Generator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Generate random numbers for Powerball / Mega Millions",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # =========================
        # LOTTERY SELECT BUTTONS
        # =========================
        tk.Label(
            left,
            text="Select Lottery",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 6))

        self.lottery_var = tk.StringVar(value="Powerball")
        self.lottery_buttons = {}
        btn_frame = tk.Frame(left, bg=PANEL_BG)
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        for lottery in LOTTERY_PRESETS.keys():
            btn = tk.Button(
                btn_frame,
                text=lottery,
                command=lambda l=lottery: self.select_lottery(l),
                bg=BTN_BG if lottery != "Powerball" else ACCENT,
                fg="white" if lottery == "Powerball" else TEXT_CLR,
                font=FONT,
                relief="flat",
                height=2,
                width=18
            )
            btn.pack(side="left", expand=True, padx=4)
            self.lottery_buttons[lottery] = btn

        # =========================
        # BUTTONS
        # =========================
        btn_frame2 = tk.Frame(left, bg=PANEL_BG)
        btn_frame2.pack(fill="x", padx=16, pady=16)

        def make_btn(text, cmd, color=BTN_BG):
            return tk.Button(
                btn_frame2,
                text=text,
                command=cmd,
                bg=color,
                fg="white",
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                height=2,
                width=18
            )

        make_btn("Generate Numbers", self.generate_numbers).pack(side="left", expand=True, padx=4)
        make_btn("About", self.show_about, ACCENT).pack(side="left", expand=True, padx=4)

        # =========================
        # RIGHT PANEL
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        self.stats_card = tk.Frame(right, bg=PANEL_BG)
        self.stats_card.pack(padx=30, pady=40, fill="both", expand=True)

        tk.Label(
            self.stats_card,
            text="Generated Numbers",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(20, 10))

        self.numbers_frame = tk.Frame(self.stats_card, bg=PANEL_BG)
        self.numbers_frame.pack(pady=20)

    # =========================
    # METHODS
    # =========================
    def select_lottery(self, lottery):
        self.lottery_var.set(lottery)
        for name, btn in self.lottery_buttons.items():
            if name == lottery:
                btn.config(bg=ACCENT, fg="white")
            else:
                btn.config(bg=BTN_BG, fg=TEXT_CLR)

    def generate_numbers(self):
        # Clear previous numbers
        for widget in self.numbers_frame.winfo_children():
            widget.destroy()

        lottery = self.lottery_var.get()
        preset = LOTTERY_PRESETS[lottery]

        main = random.sample(range(preset["main_numbers"][0], preset["main_numbers"][1] + 1), preset["main_count"])
        special = random.sample(range(preset["special_numbers"][0], preset["special_numbers"][1] + 1), preset["special_count"])

        main.sort()

        # Display main numbers as balls
        for num in main:
            ball = tk.Label(
                self.numbers_frame,
                text=str(num),
                bg="#1E90FF",
                fg="white",
                font=("Segoe UI", 16, "bold"),
                width=4,
                height=2,
                relief="raised",
                bd=2
            )
            ball.pack(side="left", padx=5)

        # Display special numbers
        for num in special:
            ball = tk.Label(
                self.numbers_frame,
                text=str(num),
                bg="#FF4500",
                fg="white",
                font=("Segoe UI", 16, "bold"),
                width=4,
                height=2,
                relief="raised",
                bd=2
            )
            ball.pack(side="left", padx=5)

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Lottery Number Generator\n\n"
            "• Random number generation\n"
            "• Presets for Powerball and Mega Millions\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    LotteryGeneratorApp(root)
    root.mainloop()
