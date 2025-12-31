import tkinter as tk
from tkinter import messagebox
import random

# =========================
# THEME
# =========================
APP_BG = "#121212"
PANEL_BG = "#1F1F1F"
BTN_BG = "#2C2C2C"
BTN_HOVER = "#3A3A3A"
BTN_ACTIVE = "#FF6F61"
ACCENT = "#FF6F61"
TEXT_CLR = "#E0E0E0"
SUBTEXT_CLR = "#AAAAAA"
INPUT_BG = "#333333"
INPUT_FG = "#FFFFFF"

# =========================
# APP
# =========================
class DiceGameApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Dice Game")
        root.geometry("1000x500")
        root.configure(bg=APP_BG)
        root.resizable(False, False)

        # =========================
        # LEFT PANEL (Actions)
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
            text="Dice Game",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Play against the computer",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        btn_frame = tk.Frame(left, bg=PANEL_BG)
        btn_frame.pack(fill="x", padx=16, pady=16)

        def make_btn(text, cmd, color=BTN_BG):
            btn = tk.Button(
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
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BTN_HOVER))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
            btn.bind("<ButtonPress-1>", lambda e, b=btn: b.config(bg=BTN_ACTIVE))
            btn.bind("<ButtonRelease-1>", lambda e, b=btn, c=color: b.config(bg=BTN_HOVER))
            return btn

        make_btn("Roll Dice", self.roll_dice, ACCENT).pack(side="top", pady=8)
        make_btn("Clear History", self.clear_history, BTN_BG).pack(side="top", pady=8)
        make_btn("About", self.show_about, BTN_BG).pack(side="top", pady=20)

        # =========================
        # RIGHT PANEL (Game UI)
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        self.result_card = tk.Frame(right, bg=PANEL_BG, bd=2, relief="ridge")
        self.result_card.pack(padx=30, pady=20, fill="both", expand=True)

        # ---------- TOP: Game Label ----------
        tk.Label(
            self.result_card,
            text="Dice Game vs Computer",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(20, 10))

        # ---------- MAIN FRAME ----------
        main_frame = tk.Frame(self.result_card, bg=PANEL_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== LEFT COLUMN: Dice Results =====
        left_frame = tk.Frame(main_frame, bg=PANEL_BG)
        left_frame.pack(side="left", fill="y", padx=(0, 15))

        # Player result
        tk.Label(
            left_frame,
            text="Your Roll:",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 2))
        self.player_label = tk.Label(
            left_frame,
            text="--",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Segoe UI", 18, "bold")
        )
        self.player_label.pack(anchor="w", pady=(0, 10))

        # Computer result
        tk.Label(
            left_frame,
            text="Computer Roll:",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 2))
        self.computer_label = tk.Label(
            left_frame,
            text="--",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Segoe UI", 18, "bold")
        )
        self.computer_label.pack(anchor="w", pady=(0, 10))

        # Winner
        tk.Label(
            left_frame,
            text="Winner:",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 2))
        self.winner_label = tk.Label(
            left_frame,
            text="--",
            bg=PANEL_BG,
            fg=ACCENT,
            width=13,
            font=("Segoe UI", 18, "bold")
        )
        self.winner_label.pack(anchor="w", pady=(0, 10))

        # ===== RIGHT COLUMN: History =====
        right_frame = tk.Frame(main_frame, bg=PANEL_BG)
        right_frame.pack(side="right", fill="both", expand=True)

        history_card = tk.Frame(right_frame, bg="#1C1C1C", bd=1, relief="ridge")
        history_card.pack(fill="both", expand=True)

        tk.Label(
            history_card,
            text="History",
            bg="#1C1C1C",
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.history_box = tk.Listbox(
            history_card,
            bg=INPUT_BG,
            fg=INPUT_FG,
            font=("Segoe UI", 12),
            height=20,
            selectbackground=ACCENT,
            relief="flat"
        )
        self.history_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.history = []

    # =========================
    # METHODS
    # =========================
    def roll_dice(self):
        player_roll = random.randint(1, 6)
        computer_roll = random.randint(1, 6)
        self.player_label.config(text=str(player_roll))
        self.computer_label.config(text=str(computer_roll))

        if player_roll > computer_roll:
            winner = "You Win!"
        elif player_roll < computer_roll:
            winner = "Computer Wins!"
        else:
            winner = "Draw!"
        self.winner_label.config(text=winner)

        entry = f"Player: {player_roll} | Computer: {computer_roll} -> {winner}"
        self.history.append(entry)
        self.history = self.history[-10:]  # last 10 rolls
        self.update_history()

    def update_history(self):
        self.history_box.delete(0, tk.END)
        for item in self.history:
            self.history_box.insert(tk.END, item)

    def clear_history(self):
        self.history = []
        self.update_history()
        self.player_label.config(text="--")
        self.computer_label.config(text="--")
        self.winner_label.config(text="--")

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Dice Game\n\n"
            "• Roll dice against the computer\n"
            "• Keep track of last 10 rolls\n"
            "• Winner is displayed each round\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    DiceGameApp(root)
    root.mainloop()
