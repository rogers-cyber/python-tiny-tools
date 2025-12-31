import sys
import os
import tkinter as tk
from tkinter import messagebox
import random
import colorsys

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
class RandomColorGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("MateTools – Pro Random Color Generator")
        root.geometry("1000x620")
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
            text="Pro Random Color Generator",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 2))

        tk.Label(
            left,
            text="Generate random colors and copy values",
            bg=PANEL_BG,
            fg=SUBTEXT_CLR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Frame(left, bg=BTN_BG, height=1).pack(fill="x", padx=16, pady=(0, 16))

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

        make_btn("Generate Random Color", self.generate_color, ACCENT).pack(side="top", pady=8)
        make_btn("Copy HEX", self.copy_hex, BTN_BG).pack(side="top", pady=8)
        make_btn("Copy RGB", self.copy_rgb, BTN_BG).pack(side="top", pady=8)
        make_btn("Copy HSL", self.copy_hsl, BTN_BG).pack(side="top", pady=8)
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
            text="Color Preview",
            bg=PANEL_BG,
            fg=TEXT_CLR,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(20, 10))

        self.color_preview = tk.Frame(self.result_card, bg="#333333", width=300, height=200)
        self.color_preview.pack(pady=(10, 20))
        self.color_preview.pack_propagate(False)

        # Color values display
        self.hex_label = tk.Label(self.result_card, text="HEX: --", bg=PANEL_BG, fg=ACCENT, font=("Segoe UI", 14, "bold"))
        self.hex_label.pack(pady=5)

        self.rgb_label = tk.Label(self.result_card, text="RGB: --", bg=PANEL_BG, fg=TEXT_CLR, font=("Segoe UI", 14, "bold"))
        self.rgb_label.pack(pady=5)

        self.hsl_label = tk.Label(self.result_card, text="HSL: --", bg=PANEL_BG, fg=SUBTEXT_CLR, font=("Segoe UI", 14, "bold"))
        self.hsl_label.pack(pady=5)

        # Store current color
        self.current_color = "#FFFFFF"

    # =========================
    # METHODS
    # =========================
    def generate_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.current_color = f"#{r:02X}{g:02X}{b:02X}"
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        hsl_str = f"{int(h*360)}, {int(s*100)}%, {int(l*100)}%"

        self.color_preview.config(bg=self.current_color)
        self.hex_label.config(text=f"HEX: {self.current_color}")
        self.rgb_label.config(text=f"RGB: {r}, {g}, {b}")
        self.hsl_label.config(text=f"HSL: {hsl_str}")

    def copy_hex(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_color)
        messagebox.showinfo("Copied", f"{self.current_color} copied to clipboard!")

    def copy_rgb(self):
        rgb_text = self.rgb_label.cget("text").replace("RGB: ", "")
        self.root.clipboard_clear()
        self.root.clipboard_append(rgb_text)
        messagebox.showinfo("Copied", f"{rgb_text} copied to clipboard!")

    def copy_hsl(self):
        hsl_text = self.hsl_label.cget("text").replace("HSL: ", "")
        self.root.clipboard_clear()
        self.root.clipboard_append(hsl_text)
        messagebox.showinfo("Copied", f"{hsl_text} copied to clipboard!")

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MateTools – Pro Random Color Generator\n\n"
            "• Generate random colors instantly\n"
            "• View HEX, RGB, and HSL values\n"
            "• Copy color values to clipboard\n\n"
            "Built by MateTools"
        )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    RandomColorGeneratorApp(root)
    root.mainloop()
