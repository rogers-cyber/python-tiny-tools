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

FONT = ("Segoe UI", 11)

# =========================
# APP
# =========================
class CaesarCipherApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Caesar Cipher")
        root.geometry("800x500")
        root.configure(bg=APP_BG)
        root.resizable(False, False)

        # =========================
        # LEFT PANEL
        # =========================
        left = tk.Frame(root, bg=PANEL_BG, width=350)
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
            text="Caesar Cipher Tool",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Encrypt or decrypt text using Caesar cipher",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # =========================
        # INPUT
        # =========================
        tk.Label(left, text="Enter Text:", bg=PANEL_BG, fg=TEXT_CLR, font=FONT).pack(anchor="w", padx=16)
        self.input_text = tk.Text(left, height=5, width=40, bg="#1E1E1E", fg=TEXT_CLR, font=FONT)
        self.input_text.pack(padx=16, pady=(0, 10))

        tk.Label(left, text="Shift:", bg=PANEL_BG, fg=TEXT_CLR, font=FONT).pack(anchor="w", padx=16)
        self.shift_var = tk.IntVar(value=3)
        tk.Entry(left, textvariable=self.shift_var, bg="#1E1E1E", fg=TEXT_CLR, font=FONT, width=5).pack(padx=16, pady=(0, 16))

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

        make_btn("Encrypt", self.encrypt_text, ACCENT).pack(side="left", expand=True, padx=4)
        make_btn("Decrypt", self.decrypt_text, "#4CAF50").pack(side="left", expand=True, padx=4)

        # =========================
        # RIGHT PANEL
        # =========================
        right = tk.Frame(root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        self.output_card = tk.Frame(right, bg=PANEL_BG)
        self.output_card.pack(padx=30, pady=40, fill="both", expand=True)

        tk.Label(
            self.output_card,
            text="Output",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(20, 10))

        self.output_text = tk.Text(self.output_card, height=10, bg="#1E1E1E", fg=TEXT_CLR, font=FONT)
        self.output_text.pack(padx=16, pady=10, fill="both", expand=True)

    # =========================
    # METHODS
    # =========================
    def encrypt_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        shift = self.shift_var.get()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, self.caesar_cipher(text, shift))

    def decrypt_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        shift = self.shift_var.get()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, self.caesar_cipher(text, -shift))

    def caesar_cipher(self, text, shift):
        result = ""
        for char in text:
            if char.isupper():
                result += chr((ord(char) - 65 + shift) % 26 + 65)
            elif char.islower():
                result += chr((ord(char) - 97 + shift) % 26 + 97)
            else:
                result += char
        return result

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    CaesarCipherApp(root)
    root.mainloop()
