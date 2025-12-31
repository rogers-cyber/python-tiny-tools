import sys
import os
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
INPUT_BG = "#333333"
INPUT_FG = "#FFFFFF"

FONT = ("Segoe UI", 11)

# =========================
# APP
# =========================
class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – BMI Calculator")
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
            text="BMI Calculator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Calculate your Body Mass Index",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # =========================
        # INPUT FIELDS
        # =========================
        input_frame = tk.Frame(left, bg=PANEL_BG)
        input_frame.pack(padx=16, pady=16, fill="x")

        tk.Label(input_frame, text="Height (cm):", bg=PANEL_BG, fg=TEXT_CLR, font=FONT).pack(anchor="w")
        self.height_entry = tk.Entry(input_frame, bg=INPUT_BG, fg=INPUT_FG, font=FONT)
        self.height_entry.pack(fill="x", pady=(0, 10))

        tk.Label(input_frame, text="Weight (kg):", bg=PANEL_BG, fg=TEXT_CLR, font=FONT).pack(anchor="w")
        self.weight_entry = tk.Entry(input_frame, bg=INPUT_BG, fg=INPUT_FG, font=FONT)
        self.weight_entry.pack(fill="x", pady=(0, 10))

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

        make_btn("Calculate BMI", self.calculate_bmi, ACCENT).pack(side="left", expand=True, padx=4)
        make_btn("About", self.show_about, BTN_BG).pack(side="left", expand=True, padx=4)

        # =========================
        # RIGHT PANEL
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        self.result_card = tk.Frame(right, bg=PANEL_BG)
        self.result_card.pack(padx=30, pady=40, fill="both", expand=True)

        tk.Label(
            self.result_card,
            text="Your BMI Result",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(20, 10))

        # BMI Value display
        self.bmi_value_label = tk.Label(
            self.result_card,
            text="--",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Segoe UI", 40, "bold")
        )
        self.bmi_value_label.pack(pady=(10, 5))

        # BMI Status display
        self.bmi_status_label = tk.Label(
            self.result_card,
            text="Enter your height and weight to calculate BMI",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 16, "bold")
        )
        self.bmi_status_label.pack(pady=(5, 20))

        # BMI Progress Bar
        self.bmi_bar_bg = tk.Frame(self.result_card, bg="#333333", height=30)
        self.bmi_bar_bg.pack(fill="x", padx=40, pady=(10, 0))
        self.bmi_bar_fg = tk.Frame(self.bmi_bar_bg, bg=ACCENT, width=0, height=30)
        self.bmi_bar_fg.place(x=0, y=0)

        # BMI labels along the bar
        self.bmi_labels_frame = tk.Frame(self.result_card, bg=PANEL_BG)
        self.bmi_labels_frame.pack(fill="x", padx=40, pady=(5, 0))
        tk.Label(self.bmi_labels_frame, text="Underweight", bg=PANEL_BG, fg="#87CEEB", font=("Segoe UI", 10)).pack(side="left")
        tk.Label(self.bmi_labels_frame, text="Normal", bg=PANEL_BG, fg="#32CD32", font=("Segoe UI", 10)).pack(side="left", expand=True)
        tk.Label(self.bmi_labels_frame, text="Overweight", bg=PANEL_BG, fg="#FFD700", font=("Segoe UI", 10)).pack(side="left")
        tk.Label(self.bmi_labels_frame, text="Obesity", bg=PANEL_BG, fg="#FF4500", font=("Segoe UI", 10)).pack(side="right")

    # =========================
    # METHODS
    # =========================
    def calculate_bmi(self):
        try:
            height_cm = float(self.height_entry.get())
            weight_kg = float(self.weight_entry.get())

            if height_cm <= 0 or weight_kg <= 0:
                raise ValueError

            height_m = height_cm / 100
            bmi = weight_kg / (height_m ** 2)
            bmi = round(bmi, 2)

            # Determine BMI status and color
            if bmi < 18.5:
                status = "Underweight"
                color = "#87CEEB"
            elif 18.5 <= bmi < 25:
                status = "Normal weight"
                color = "#32CD32"
            elif 25 <= bmi < 30:
                status = "Overweight"
                color = "#FFD700"
            else:
                status = "Obesity"
                color = "#FF4500"

            # Update BMI number and status
            self.bmi_value_label.config(text=str(bmi), fg=color)
            self.bmi_status_label.config(text=status, fg=color)

            # Update progress bar
            # Scale BMI from 0-40 as max width
            max_width = self.bmi_bar_bg.winfo_width() or 400
            bmi_width = min(bmi / 40, 1) * max_width
            self.bmi_bar_fg.config(width=bmi_width, bg=color)

        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numeric values for height and weight.")

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – BMI Calculator\n\n"
            "• Calculate Body Mass Index (BMI)\n"
            "• Provides BMI category with color-coded visual\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    BMICalculatorApp(root)
    root.mainloop()
