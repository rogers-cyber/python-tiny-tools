import sys
import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import requests

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

DATA_FILE = resource_path("rates_live.json")

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("CurrencyTool Pro")
root.geometry("980x620")
root.minsize(900, 550)

sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
amount_var = tk.DoubleVar(value=100.0)
from_var = tk.StringVar(value="USD")
to_var = tk.StringVar(value="EUR")
result_var = tk.StringVar(value="—")
status_var = tk.StringVar(value="Ready")
mode_var = tk.StringVar(value="Offline")

# Default fallback rates
RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 157.0,
    "AUD": 1.52,
    "CAD": 1.36,
    "CHF": 0.88,
    "CNY": 7.18
}

# =========================
# Persistence
# =========================
def load_rates():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                RATES.clear()
                RATES.update(data)
                RATES["USD"] = 1.0
                mode_var.set("Online")
        except Exception:
            pass

def save_rates():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(RATES, f, indent=2)

# =========================
# Status
# =========================
def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# =========================
# Live Rate Fetch
# =========================
def fetch_live_rates():
    update_btn.config(state="disabled")
    set_status("🌐 Fetching live rates...")
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=6)
        data = r.json()

        if data.get("result") != "success":
            raise RuntimeError

        RATES.clear()
        RATES.update(data["rates"])
        RATES["USD"] = 1.0

        save_rates()
        refresh_currency_lists()

        mode_var.set("Online")
        set_status("🌐 Live rates updated & saved")

    except Exception:
        messagebox.showwarning(
            "Live Update Failed",
            "Unable to fetch live rates.\nUsing offline data."
        )
        set_status("Offline mode")

    finally:
        update_btn.config(state="normal")

# =========================
# Conversion
# =========================
def convert_currency():
    try:
        amount = amount_var.get()
        f, t = from_var.get(), to_var.get()

        usd = amount / RATES[f]
        result = usd * RATES[t]

        result_var.set(f"{result:,.4f} {t}")
        set_status(f"Converted ({mode_var.get()})")

    except Exception:
        messagebox.showerror("Error", "Invalid amount or currency.")

def swap_currencies():
    f, t = from_var.get(), to_var.get()
    from_var.set(t)
    to_var.set(f)

# =========================
# Rate Editor
# =========================
def open_rate_editor():
    editor = tk.Toplevel(root)
    editor.title("✏️ Manual Rate Override (USD Base)")

    # Center the window
    w, h = 420, 520
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    editor.geometry(f"{w}x{h}+{x}+{y}")
    editor.transient(root)
    editor.grab_set()

    frame = ttk.Frame(editor, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Manual Rate Override",
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w")

    ttk.Label(
        frame,
        text="Saving switches app to Offline mode",
        foreground="#666"
    ).pack(anchor="w", pady=(2, 10))

    # Scrollable frame
    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    entries = {}

    for c in sorted(RATES.keys()):
        row = ttk.Frame(scrollable_frame)
        row.pack(fill="x", pady=2)

        ttk.Label(row, text=c, width=6).pack(side="left")

        v = tk.DoubleVar(value=RATES[c])
        ttk.Entry(row, textvariable=v, width=12).pack(side="left", padx=4)
        entries[c] = v

        def make_save(currency):
            return lambda: save_single_rate(currency)

        ttk.Button(
            row,
            text="💾",
            width=3,
            command=make_save(c),
            style="Action.TButton"
        ).pack(side="right")

    def save_single_rate(currency):
        try:
            RATES[currency] = float(entries[currency].get())
            save_rates()  # Save to JSON
            refresh_currency_lists()
            mode_var.set("Offline")
            set_status(f"💾 {currency} rate saved")
        except Exception:
            messagebox.showerror("Invalid Input", "Rate must be numeric.")


# =========================
# UI Refresh
# =========================
def refresh_currency_lists():
    cur = sorted(RATES.keys())
    from_combo["values"] = cur
    to_combo["values"] = cur

# =========================
# Styles
# =========================
style = ttk.Style()
style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
style.configure("Subtitle.TLabel", font=("Segoe UI", 11))
style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=10)
style.configure("Result.TLabel", font=("Segoe UI", 18, "bold"))

# =========================
# Layout
# =========================
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# ----- Header -----
header = ttk.Frame(root, padding=(24, 16))
header.grid(row=0, column=0, sticky="ew")
header.columnconfigure(1, weight=1)

ttk.Label(header, text="CurrencyTool Pro", style="Title.TLabel").grid(row=0, column=0, sticky="w")
ttk.Label(
    header,
    text="Live + Offline currency converter with persistence",
    style="Subtitle.TLabel"
).grid(row=1, column=0, sticky="w", pady=(2, 0))

controls = ttk.Frame(header)
controls.grid(row=0, column=1, rowspan=2, sticky="e")

# 🌐 Update Live Rates button
update_btn = ttk.Button(
    controls,
    text="🌐 Update Live Rates",
    command=lambda: threading.Thread(target=fetch_live_rates, daemon=True).start(),
    style="Action.TButton"
)
update_btn.pack(side="right", padx=6)

# ✏️ Manual Override button
manual_btn = ttk.Button(
    controls,
    text="✏️ Manual Override",
    command=open_rate_editor,
    style="Action.TButton"
)
manual_btn.pack(side="right", padx=6)

# ----- Main Converter Card -----
main = ttk.Frame(root, padding=(24, 0, 24, 16))
main.grid(row=1, column=0, sticky="nsew")
main.columnconfigure(0, weight=1)

card = ttk.LabelFrame(main, text="Converter", padding=20)
card.grid(row=0, column=0, sticky="ew")
for i in range(4):
    card.columnconfigure(i, weight=1)

# Amount
ttk.Label(card, text="Amount").grid(row=0, column=0, sticky="w", pady=(0, 4))
ttk.Entry(card, textvariable=amount_var, font=("Segoe UI", 11)).grid(row=1, column=0, sticky="ew", padx=(0, 10))

# From currency
ttk.Label(card, text="From").grid(row=0, column=1, sticky="w", pady=(0, 4))
from_combo = ttk.Combobox(card, textvariable=from_var, state="readonly", font=("Segoe UI", 11))
from_combo.grid(row=1, column=1, sticky="ew", padx=(0, 10))

# To currency
ttk.Label(card, text="To").grid(row=0, column=2, sticky="w", pady=(0, 4))
to_combo = ttk.Combobox(card, textvariable=to_var, state="readonly", font=("Segoe UI", 11))
to_combo.grid(row=1, column=2, sticky="ew", padx=(0, 10))

# Swap button
ttk.Button(card, text="⇄", command=swap_currencies, style="Action.TButton").grid(row=1, column=3, sticky="ew")

# Result
ttk.Label(card, text="Result", style="Subtitle.TLabel").grid(
    row=2, column=0, columnspan=4, pady=(20, 4), sticky="w"
)
ttk.Label(card, textvariable=result_var, style="Result.TLabel", font=("Segoe UI", 14, "bold")).grid(
    row=3, column=0, columnspan=4, sticky="w"
)

# ----- Actions -----
actions = ttk.Frame(main, padding=(0, 0, 0, 12))
actions.grid(row=1, column=0, pady=16, sticky="ew")
actions.columnconfigure(0, weight=1)

ttk.Button(
    actions,
    text="Convert",
    command=convert_currency,
    style="Action.TButton"
).pack(side="left")

ttk.Label(actions, textvariable=mode_var, foreground="#666", font=("Segoe UI", 10)).pack(side="right")

# ----- Status -----
status = ttk.Label(root, textvariable=status_var, anchor="w", padding=6)
status.grid(row=2, column=0, sticky="ew")

# =========================
# Init
# =========================
load_rates()
refresh_currency_lists()

# =========================
# Run
# =========================
root.mainloop()
