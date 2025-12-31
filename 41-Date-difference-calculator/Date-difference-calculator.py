import sys
import os
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from dateutil.relativedelta import relativedelta

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
# DATE LOGIC (CALENDAR-ACCURATE)
# =========================
def calculate_exact_difference(d1, d2):
    if d2 < d1:
        d1, d2 = d2, d1

    delta = relativedelta(d2, d1)
    total_days = (d2 - d1).days

    return {
        "Years": delta.years,
        "Months": delta.months,
        "Days": delta.days,
        "Total Days": total_days
    }

# =========================
# APP
# =========================
class DateDifferenceCalculator:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Date Difference Calculator")
        root.geometry("1000x520")
        root.configure(bg=APP_BG)
        root.resizable(False, False)

        # =========================
        # LEFT PANEL
        # =========================
        left = tk.Frame(root, bg=PANEL_BG, width=420)
        left.pack(side="left", fill="y")

        # =========================
        # LEFT HEADER 
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

        # Divider
        tk.Frame(left, bg=ACCENT, height=2).pack(fill="x", padx=16, pady=(0, 14))

        # =========================
        # SUB TOOL TITLE (LEFT)
        # =========================
        tk.Label(
            left,
            text="Date Difference Calculator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Calendar-accurate years, months, and days",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # =========================
        # DATE INPUTS
        # =========================
        tk.Label(
            left,
            text="Select Dates",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 6))

        self.date1 = DateEntry(
            left,
            background=BTN_BG,
            foreground=TEXT_CLR,
            borderwidth=0,
            font=FONT,
            date_pattern="yyyy-mm-dd"
        )
        self.date1.pack(fill="x", padx=16, pady=8)

        self.date2 = DateEntry(
            left,
            background=BTN_BG,
            foreground=TEXT_CLR,
            borderwidth=0,
            font=FONT,
            date_pattern="yyyy-mm-dd"
        )
        self.date2.pack(fill="x", padx=16, pady=8)

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
                width=18
            )

        make_btn("Calculate", self.calculate).pack(side="left", expand=True, padx=4)
        make_btn("About", self.show_about, ACCENT).pack(side="left", expand=True, padx=4)

        # =========================
        # RIGHT PANEL
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        # =========================
        # STATS CARD
        # =========================
        stats_card = tk.Frame(right, bg=PANEL_BG)
        stats_card.pack(padx=30, pady=40, fill="both", expand=True)

        tk.Label(
            stats_card,
            text="Exact Date Difference",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(20, 10))

        self.stats = {}
        for label in ["Years", "Months", "Days", "Total Days"]:
            frame = tk.Frame(stats_card, bg=PANEL_BG)
            frame.pack(fill="x", padx=40, pady=6)

            tk.Label(
                frame,
                text=label,
                bg=PANEL_BG,
                fg=SUBTEXT_CLR,
                font=("Segoe UI", 11)
            ).pack(side="left")

            value = tk.Label(
                frame,
                text="0",
                bg=PANEL_BG,
                fg="white",
                font=("Segoe UI", 12, "bold")
            )
            value.pack(side="right")

            self.stats[label] = value

    # =========================
    # METHODS
    # =========================
    def calculate(self):
        d1 = self.date1.get_date()
        d2 = self.date2.get_date()

        result = calculate_exact_difference(d1, d2)
        for key, value in result.items():
            self.stats[key].config(text=str(value))

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Date Difference Calculator\n\n"
            "• Calendar picker input\n"
            "• Calendar-accurate calculations\n"
            "• Leap years supported\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    DateDifferenceCalculator(root)
    root.mainloop()
