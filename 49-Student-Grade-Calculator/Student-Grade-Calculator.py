import tkinter as tk
from tkinter import messagebox

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
class StudentGradeApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Student Grade Calculator")
        root.geometry("1080x740")
        root.configure(bg=APP_BG)
        root.resizable(False, False)

        # =========================
        # LEFT PANEL (Actions & Inputs)
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
            text="Student Grade Calculator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Enter up to 5 scores (0-100)",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # ===== Score Entries =====
        self.scores_entries = []
        scores_frame = tk.Frame(left, bg=PANEL_BG)
        scores_frame.pack(fill="x", padx=16, pady=(0, 16))

        for i in range(5):
            tk.Label(
                scores_frame,
                text=f"Score {i+1}:",
                bg=PANEL_BG,
                fg=SUBTEXT_CLR,
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", pady=(2, 0))
            entry = tk.Entry(scores_frame, bg=INPUT_BG, fg=INPUT_FG, font=("Segoe UI", 12))
            entry.pack(fill="x", pady=(0, 5))
            self.scores_entries.append(entry)

        # ===== Buttons =====
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

        make_btn("Calculate Grade", self.calculate_grade, ACCENT).pack(side="top", pady=8)
        make_btn("Clear", self.clear_fields, BTN_BG).pack(side="top", pady=8)
        make_btn("About", self.show_about, BTN_BG).pack(side="top", pady=20)

        # =========================
        # RIGHT PANEL (Results & History)
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        self.result_card = tk.Frame(right, bg=PANEL_BG, bd=2, relief="ridge")
        self.result_card.pack(padx=30, pady=20, fill="both", expand=True)

        # ---------- TOP: App Label ----------
        tk.Label(
            self.result_card,
            text="Student Grade Calculator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(20, 10))

        # ---------- MAIN FRAME ----------
        main_frame = tk.Frame(self.result_card, bg=PANEL_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== LEFT COLUMN: Result =====
        left_frame = tk.Frame(main_frame, bg=PANEL_BG)
        left_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(
            left_frame,
            text="Latest Grade:",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.result_label = tk.Label(
            left_frame,
            text="Grade: --",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Segoe UI", 18, "bold"),
            width=20
        )
        self.result_label.pack(anchor="w", pady=(0, 10))

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
    def calculate_grade(self):
        try:
            scores = [float(entry.get()) for entry in self.scores_entries if entry.get() != ""]
            if not scores:
                raise ValueError("No scores entered")
            average = sum(scores) / len(scores)

            if average >= 90:
                grade = "A"
            elif average >= 80:
                grade = "B"
            elif average >= 70:
                grade = "C"
            elif average >= 60:
                grade = "D"
            else:
                grade = "F"

            result_text = f"{grade} ({average:.2f}%)"
            self.result_label.config(text=f"Grade: {result_text}")

            # Add to history (last 25)
            entry = f"Scores: {', '.join([str(int(s)) for s in scores])} -> Grade: {result_text}"
            self.history.append(entry)
            self.history = self.history[-25:]
            self.update_history()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric scores (0-100)")

    def update_history(self):
        self.history_box.delete(0, tk.END)
        for item in self.history:
            self.history_box.insert(tk.END, item)

    def clear_fields(self):
        for entry in self.scores_entries:
            entry.delete(0, tk.END)
        self.result_label.config(text="Grade: --")
        self.history = []
        self.update_history()

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Student Grade Calculator\n\n"
            "• Enter up to 5 scores (0-100)\n"
            "• Calculates average and grade\n"
            "• Tracks last 25 calculated grades\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    StudentGradeApp(root)
    root.mainloop()
