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
class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Pro Calculator")
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
            text="Pro Calculator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Perform calculations with history",
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
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BTN_HOVER))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
            btn.bind("<ButtonPress-1>", lambda e, b=btn: b.config(bg=BTN_ACTIVE))
            btn.bind("<ButtonRelease-1>", lambda e, b=btn, c=color: b.config(bg=BTN_HOVER))
            return btn

        make_btn("Clear Input", self.clear_input, ACCENT).pack(side="top", pady=8)
        make_btn("Clear History", self.clear_history, BTN_BG).pack(side="top", pady=8)
        make_btn("About", self.show_about, BTN_BG).pack(side="top", pady=20)

        # =========================
        # RIGHT PANEL (Calculator UI)
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        self.result_card = tk.Frame(right, bg=PANEL_BG, bd=2, relief="ridge")
        self.result_card.pack(padx=30, pady=20, fill="both", expand=True)

        # ---------- TOP: Calculator Label ----------
        tk.Label(
            self.result_card,
            text="Calculator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(20, 10))

        # ---------- MAIN FRAME: split left/right ----------
        main_frame = tk.Frame(self.result_card, bg=PANEL_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== LEFT COLUMN: Input + Buttons =====
        left_frame = tk.Frame(main_frame, bg=PANEL_BG)
        left_frame.pack(side="left", fill="y", padx=(0, 15))

        # Input Entry
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            left_frame,
            textvariable=self.input_var,
            bg=INPUT_BG,
            fg=INPUT_FG,
            font=("Segoe UI", 18),
            relief="flat",
            justify="right"
        )
        self.input_entry.pack(fill="x", pady=(0, 10))
        self.input_entry.bind("<Return>", lambda event: self.calculate())

        # Button Grid
        btn_frame = tk.Frame(left_frame, bg=PANEL_BG)
        btn_frame.pack()

        buttons = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '=', '+'),
        ]

        for r, row in enumerate(buttons):
            for c, char in enumerate(row):
                if char == '=':
                    btn = tk.Button(
                        btn_frame, text=char, bg=ACCENT, fg="white",
                        font=("Segoe UI", 14, "bold"), relief="flat",
                        width=5, height=2,
                        command=self.calculate
                    )
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#FF8679"))
                    btn.bind("<Leave>", lambda e, b=btn: b.config(bg=ACCENT))
                    btn.bind("<ButtonPress-1>", lambda e, b=btn: b.config(bg="#FF4F3F"))
                    btn.bind("<ButtonRelease-1>", lambda e, b=btn: b.config(bg="#FF8679"))
                else:
                    btn = tk.Button(
                        btn_frame, text=char, bg=BTN_BG, fg="white",
                        font=("Segoe UI", 14, "bold"), relief="flat",
                        width=5, height=2,
                        command=lambda ch=char: self.add_to_input(ch)
                    )
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BTN_HOVER))
                    btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BTN_BG))
                    btn.bind("<ButtonPress-1>", lambda e, b=btn: b.config(bg=BTN_ACTIVE))
                    btn.bind("<ButtonRelease-1>", lambda e, b=btn: b.config(bg=BTN_HOVER))
                btn.grid(row=r, column=c, padx=5, pady=5)

        # ===== RIGHT COLUMN: Result + History =====
        right_frame = tk.Frame(main_frame, bg=PANEL_BG)
        right_frame.pack(side="right", fill="both", expand=True)

        # Result display in card-like style
        result_card = tk.Frame(right_frame, bg="#1C1C1C", bd=1, relief="ridge")
        result_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            result_card,
            text="Result",
            bg="#1C1C1C",
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.result_label = tk.Label(
            result_card,
            text="--",
            bg="#1C1C1C",
            fg=ACCENT,
            font=("Segoe UI", 18, "bold")
        )
        self.result_label.pack(anchor="e", padx=10, pady=(0, 5))

        # History display in scrollable frame
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
            height=10,
            selectbackground=ACCENT,
            relief="flat"
        )
        self.history_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.history = []

    # =========================
    # METHODS
    # =========================
    def add_to_input(self, char):
        self.input_var.set(self.input_var.get() + char)

    def calculate(self):
        expr = self.input_var.get()
        if not expr.strip():
            return
        try:
            result = round(eval(expr), 6)  # Round to 6 decimal places
            self.result_label.config(text=f"{result}")
            # Append to history and keep only last 10 items
            self.history.append(f"{expr} = {result}")
            self.history = self.history[-10:]
            self.update_history()
            self.input_var.set(str(result))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression: {e}")

    def update_history(self):
        self.history_box.delete(0, tk.END)
        for item in self.history:
            self.history_box.insert(tk.END, item)

    def clear_input(self):
        self.input_var.set("")

    def clear_history(self):
        self.history = []
        self.update_history()

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Pro Calculator\n\n"
            "• Perform calculations instantly\n"
            "• Click buttons or type expressions\n"
            "• Keep track of history (last 10 calculations)\n"
            "• Results are rounded to 6 decimal places\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()
