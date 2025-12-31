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

FONT = ("Segoe UI", 11)

# =========================
# RESOURCE PATH
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# LOTTERY LOGIC
# =========================
def generate_lottery(min_num, max_num, count):
    if count > (max_num - min_num + 1):
        raise ValueError("Count exceeds available unique numbers.")
    return sorted(random.sample(range(min_num, max_num + 1), count))

# =========================
# APP
# =========================
class LotteryGenerator:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Random Lottery Generator")
        root.geometry("1000x520")
        root.configure(bg=APP_BG)
        root.resizable(False, False)

        # =========================
        # LEFT PANEL
        # =========================
        left = tk.Frame(root, bg=PANEL_BG, width=420)
        left.pack(side="left", fill="y")

        # =========================
        # HEADER
        # =========================
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

        # =========================
        # SUB TITLE
        # =========================
        tk.Label(
            left,
            text="Random Lottery Generator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Generate unique random lottery numbers",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # =========================
        # INPUTS
        # =========================
        def labeled_entry(label):
            tk.Label(
                left,
                text=label,
                bg=PANEL_BG,
                fg=TEXT_CLR,
                font=("Segoe UI", 11, "bold")
            ).pack(anchor="w", padx=16, pady=(10, 4))
            e = tk.Entry(
                left,
                bg=BTN_BG,
                fg="white",
                font=FONT,
                relief="flat"
            )
            e.pack(fill="x", padx=16)
            return e

        self.min_entry = labeled_entry("Minimum Number")
        self.min_entry.insert(0, "1")

        self.max_entry = labeled_entry("Maximum Number")
        self.max_entry.insert(0, "49")

        self.count_entry = labeled_entry("Numbers to Draw")
        self.count_entry.insert(0, "6")

        # =========================
        # BUTTONS
        # =========================
        btn_frame = tk.Frame(left, bg=PANEL_BG)
        btn_frame.pack(fill="x", padx=16, pady=20)

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
                width=18
            )

        make_btn("Generate", self.generate).pack(side="left", expand=True, padx=4)
        make_btn("About", self.show_about, ACCENT).pack(side="left", expand=True, padx=4)

        # =========================
        # RIGHT PANEL
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        stats_card = tk.Frame(right, bg=PANEL_BG)
        stats_card.pack(padx=30, pady=40, fill="both", expand=True)

        tk.Label(
            stats_card,
            text="Generated Numbers",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(20, 10))

        self.result_label = tk.Label(
            stats_card,
            text="—",
            bg=PANEL_BG,
            fg="white",
            font=("Segoe UI", 22, "bold")
        )
        self.result_label.pack(pady=30)

    # =========================
    # METHODS
    # =========================
    def generate(self):
        try:
            min_n = int(self.min_entry.get())
            max_n = int(self.max_entry.get())
            count = int(self.count_entry.get())

            numbers = generate_lottery(min_n, max_n, count)
            self.result_label.config(text="  ".join(map(str, numbers)))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Random Lottery Generator\n\n"
            "• Unique random numbers\n"
            "• Custom ranges & counts\n"
            "• Clean, modern UI\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    LotteryGenerator(root)
    root.mainloop()
