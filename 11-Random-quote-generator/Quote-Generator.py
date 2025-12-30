import sys
import os
import json
import random
import threading
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from tkinter import filedialog

def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("QuoteSpark - Ultimate Quote Generator")
root.geometry("1000x620")

root.iconbitmap(resource_path("logo.ico"))

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
dark_mode_var = tk.BooleanVar(value=False)
category_var = tk.StringVar(value="Motivation")

categories = {
    "Motivation": ["motivational", "inspirational"],
    "Tech": ["technology", "science"],
    "Life": ["life", "wisdom"]
}

fallback_quotes = [
    ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
    ("What we think, we become.", "Buddha"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
]

current_quote = {}

# =========================
# Helpers
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# Use a writable location
def get_favorites_file():
    # Store in user’s home directory (or AppData)
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, ".quotespark")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "favorites.json")

FAVORITES_FILE = get_favorites_file()

def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_favorites(data):
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Failed to save favorites:", e)


def toggle_theme():
    style.theme_use("clam")
    bg = "#2E2E2E" if dark_mode_var.get() else "#FFFFFF"
    fg = "white" if dark_mode_var.get() else "black"

    root.configure(bg=bg)
    for w in ["TFrame", "TLabel", "TLabelframe", "TLabelframe.Label", "TCheckbutton"]:
        style.configure(w, background=bg, foreground=fg)

    set_status(f"Theme switched to {'Dark' if dark_mode_var.get() else 'Light'} mode")

# =========================
# Quote APIs (Failover)
# =========================
def fetch_quotable(tags):
    try:
        url = f"https://api.quotable.io/random?tags={'|'.join(tags)}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        d = r.json()
        return d["content"], d["author"], "Quotable"
    except Exception:
        return None

def fetch_zenquotes():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=5)
        r.raise_for_status()
        d = r.json()[0]
        return d["q"], d["a"], "ZenQuotes"
    except Exception:
        return None

def fetch_theysaidso(category):
    try:
        url = f"https://quotes.rest/qod?category={category.lower()}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        d = r.json()["contents"]["quotes"][0]
        return d["quote"], d["author"], "They Said So"
    except Exception:
        return None

def fetch_quote(category):
    tags = categories.get(category, [])
    for fetcher in (
        lambda: fetch_quotable(tags),
        fetch_zenquotes,
        lambda: fetch_theysaidso(category),
    ):
        result = fetcher()
        if result:
            return result

    q, a = random.choice(fallback_quotes)
    return q, a, "Offline"

# =========================
# Quote Logic
# =========================
def generate_quote():
    set_status("Fetching quote...")
    quote_var.set("Loading...")
    author_var.set("")

    def task():
        q, a, src = fetch_quote(category_var.get())
        root.after(0, lambda: update_quote(q, a, src))

    threading.Thread(target=task, daemon=True).start()

def update_quote(q, a, src):
    quote_var.set(f"“{q}”")
    author_var.set(f"— {a}")
    source_var.set(f"Source: {src}")
    current_quote.update({
        "quote": q,
        "author": a,
        "category": category_var.get(),
        "source": src
    })
    set_status("Quote generated")

def copy_quote():
    root.clipboard_clear()
    root.clipboard_append(f'{quote_var.get()} {author_var.get()}')
    set_status("Copied to clipboard")

# =========================
# Favorites
# =========================
def save_favorite():
    if not current_quote:
        return

    favs = load_favorites()
    if current_quote in favs:
        set_status("Already in favorites")
        return

    favs.append(current_quote.copy())
    save_favorites(favs)
    set_status("Saved to favorites ❤️")

def open_favorites():
    favs = load_favorites()
    if not favs:
        messagebox.showinfo("Favorites", "No favorites to show.")
        return

    win = tk.Toplevel(root)
    win.title("❤️ Favorites")
    win.geometry("850x500")
    win.transient(root)  # keep on top
    win.iconbitmap(resource_path("logo.ico"))

    # Center the window on the main root
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    win_w = 850
    win_h = 500
    x = root_x + (root_w - win_w) // 2
    y = root_y + (root_h - win_h) // 2
    win.geometry(f"{win_w}x{win_h}+{x}+{y}")

    search_var = tk.StringVar()

    def refresh_list(filter_text=""):
        listbox.delete(0, tk.END)
        for f in favs:
            text = f'{f["quote"]} — {f["author"]} [{f["category"]}]'
            if filter_text.lower() in text.lower():
                listbox.insert(tk.END, text)

    def remove_selected():
        sel = listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if messagebox.askyesno("Remove", "Remove selected favorite?"):
            favs.pop(idx)
            save_favorites(favs)
            refresh_list(search_var.get())
            set_status("Favorite removed")

    def export_txt():
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Export Favorites to TXT"
            )
            if not file_path:
                return
            with open(file_path, "w", encoding="utf-8") as f:
                for item in favs:
                    f.write(f'{item["quote"]} — {item["author"]} [{item["category"]}]\n')
            set_status(f"Favorites exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export TXT:\n{e}")

    def export_csv():
        try:
            import csv
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Export Favorites to CSV"
            )
            if not file_path:
                return
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["quote", "author", "category", "source"])
                writer.writeheader()
                writer.writerows(favs)
            set_status(f"Favorites exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{e}")

    # UI
    ttk.Entry(win, textvariable=search_var).pack(fill="x", padx=10, pady=5)
    search_var.trace_add("write", lambda *a: refresh_list(search_var.get()))

    listbox = tk.Listbox(win, font=("Segoe UI", 10))
    listbox.pack(expand=True, fill="both", padx=10, pady=5)

    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=5)

    ttk.Button(btn_frame, text="🗑️ Remove Selected", command=remove_selected).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="📄 Export TXT", command=export_txt).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="📊 Export CSV", command=export_csv).pack(side="left", padx=5)

    refresh_list()

def show_help():
    help_win = tk.Toplevel(root)
    help_win.title("QuoteSpark - Help")
    help_win.geometry("480x350")
    help_win.configure(bg="#2e2e2e")
    help_win.resizable(False, False)
    help_win.transient(root)
    help_win.grab_set()

    help_win.iconbitmap(resource_path("logo.ico"))

    # Center window
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - 480) // 2
    y = root.winfo_y() + (root.winfo_height() - 350) // 2
    help_win.geometry(f"480x350+{x}+{y}")

    frame = tk.Frame(help_win, bg="#2e2e2e")
    frame.pack(fill="both", expand=True, padx=12, pady=12)

    text = tk.Text(
        frame,
        bg="#2e2e2e",
        fg="#f0f0f0",
        font=("Segoe UI", 11),
        wrap="word",
        borderwidth=0,
        padx=10,
        pady=10
    )
    text.pack(fill="both", expand=True)

    help_text = """📖 QuoteSpark — Quick Help

• Choose a category and click Generate to fetch a quote.
• Quotes are pulled from multiple APIs with offline fallback.
• Save quotes you like using ❤️ Save.
• View, search, and remove saved quotes in Favorites.
• Copy the current quote to your clipboard instantly.
• Toggle Dark Mode for a different look.

ℹ️ Notes:
• Internet is required for live quotes.
• Favorites are stored locally on your device.

Built by MateTools
https://matetools.gumroad.com
"""

    text.insert("1.0", help_text)
    text.config(state="disabled")

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#4CAF50", padding=8)
style.map("Action.TButton", background=[("active", "#45a049")])

# =========================
# Status Bar
# =========================
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill="x")

# =========================
# Main UI
# =========================
main = ttk.Frame(root, padding=25)
main.pack(expand=True, fill="both")

ttk.Label(main, text="QuoteSpark", font=("Segoe UI", 22, "bold")).pack()
ttk.Label(main, text="Smart quotes with favorites & failover APIs",
          font=("Segoe UI", 11)).pack(pady=(0, 10))

cat_frame = ttk.Frame(main)
cat_frame.pack(pady=(5, 15))

ttk.Label(
    cat_frame,
    text="Category",
    font=("Segoe UI", 10, "bold")
).pack(side="left", padx=(0, 8))

ttk.Combobox(
    cat_frame,
    values=list(categories.keys()),
    textvariable=category_var,
    state="readonly",
    width=28,
    font=("Segoe UI", 10)
).pack(side="left")

card = ttk.LabelFrame(main, text="Quote", padding=25)
card.pack(expand=True, fill="both", pady=15)

quote_var = tk.StringVar(value="Click Generate to begin ✨")
author_var = tk.StringVar()
source_var = tk.StringVar()

ttk.Label(card, textvariable=quote_var, wraplength=820,
          justify="center", font=("Segoe UI", 14, "italic")).pack(pady=(20, 10))
ttk.Label(card, textvariable=author_var,
          font=("Segoe UI", 11, "bold")).pack()
ttk.Label(card, textvariable=source_var,
          font=("Segoe UI", 9)).pack(pady=(5, 0))

actions = ttk.Frame(main)
actions.pack(pady=15)

ttk.Button(actions, text="Generate", command=generate_quote,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="❤️ Save", command=save_favorite,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="📖 Favorites", command=open_favorites,
           style="Action.TButton").pack(side="left", padx=6)
ttk.Button(actions, text="Copy", command=copy_quote,
           style="Action.TButton").pack(side="left", padx=6)

ttk.Button(actions, text="❓ Help", command=show_help,
           style="Action.TButton").pack(side="left", padx=6)

ttk.Checkbutton(actions, text="Dark Mode",
                variable=dark_mode_var,
                command=toggle_theme).pack(side="left", padx=12)

# =========================
# Run App
# =========================
root.mainloop()
