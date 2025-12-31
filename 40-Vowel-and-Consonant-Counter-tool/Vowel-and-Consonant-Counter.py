import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# =========================
# THEME
# =========================
APP_BG = "#121212"
PANEL_BG = "#1F1F1F"
BTN_BG = "#2C2C2C"
ACCENT = "#FF6F61"
TEXT_CLR = "#E0E0E0"

FONT = ("Segoe UI", 11)

# =========================
# RESOURCE PATH
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# TEXT LOGIC
# =========================
VOWELS = set("aeiouAEIOU")

def count_chars(text):
    vowels = sum(1 for c in text if c in VOWELS)
    consonants = sum(1 for c in text if c.isalpha() and c not in VOWELS)
    total_letters = vowels + consonants
    total_chars = len(text)
    words = len(text.split())

    return vowels, consonants, total_letters, words, total_chars

# =========================
# APP
# =========================
class VowelConsonantCounter:
    def __init__(self, root):
        self.root = root
        root.title("Vowel & Consonant Counter")
        root.geometry("1000x520")
        root.configure(bg=APP_BG)
        root.resizable(False, False)

        # =========================
        # LEFT PANEL
        # =========================
        left = tk.Frame(root, bg=PANEL_BG, width=420)
        left.pack(side="left", fill="y")

        tk.Label(
            left,
            text="Enter Text",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.text_box = tk.Text(
            left,
            height=17,
            bg=BTN_BG,
            fg=TEXT_CLR,
            font=FONT,
            wrap="word",
            padx=10,
            pady=10,
            relief="flat"
        )
        self.text_box.pack(fill="x", padx=12)
        self.text_box.bind("<KeyRelease>", self.update_counts)

        # =========================
        # BUTTONS
        # =========================
        btn_frame = tk.Frame(left, bg=PANEL_BG)
        btn_frame.pack(fill="x", padx=12, pady=12)

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

        make_btn("Clear Text", self.clear_text).pack(side="left", expand=True, padx=4)
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
            text="Text Statistics",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(20, 10))

        self.stats = {}
        for label in ["Vowels", "Consonants", "Total Letters", "Words", "Characters"]:
            frame = tk.Frame(stats_card, bg=PANEL_BG)
            frame.pack(fill="x", padx=40, pady=6)

            tk.Label(
                frame,
                text=label,
                bg=PANEL_BG,
                fg="#AAAAAA",
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
    def update_counts(self, event=None):
        text = self.text_box.get("1.0", "end-1c")

        v, c, letters, words, chars = count_chars(text)

        self.stats["Vowels"].config(text=str(v))
        self.stats["Consonants"].config(text=str(c))
        self.stats["Total Letters"].config(text=str(letters))
        self.stats["Words"].config(text=str(words))
        self.stats["Characters"].config(text=str(chars))

    def clear_text(self):
        self.text_box.delete("1.0", "end")
        self.update_counts()

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Vowel & Consonant Counter\n\n"
            "Counts vowels, consonants, words, and characters.\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    VowelConsonantCounter(root)
    root.mainloop()
