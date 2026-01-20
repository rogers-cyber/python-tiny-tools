import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText
import threading
import time
import json
import csv
import requests
import re
import os
import sys
from collections import defaultdict
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}
SEARCH_URL = "https://www.google.com/search"

emails_found = set()
sources = defaultdict(list)
stop_event = threading.Event()
scrape_completed = False

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# =================== Utility ===================
def resource_path(file_name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def show_error(t, m): messagebox.showerror(t, m)
def show_info(t, m): messagebox.showinfo(t, m)

# ================= APP =================
app = tb.Window("EmailScout – Public Contact Finder", themename="superhero", size=(1300, 680))
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=1)

# ================= INPUT =================
input_card = tb.Labelframe(app, text="Search Keywords", padding=15)
input_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

tb.Label(input_card, text="One search per line (e.g. 'AI developer contact email')").pack(anchor="w")
keywords_input = ScrolledText(input_card, height=7)
keywords_input.pack(fill="both", expand=True)

# ================= OUTPUT =================
output_card = tb.Labelframe(app, text="Live Results", padding=15)
output_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

log = ScrolledText(output_card)
log.pack(fill="both", expand=True)
log.text.config(state="disabled")

# ================= FOOTER =================
footer = tb.Frame(app)
footer.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

start_btn = tb.Button(footer, text="Start", bootstyle="success", width=18,
                      command=lambda: threading.Thread(target=start_scraping, daemon=True).start())
start_btn.pack(side="left", padx=5)

stop_btn = tb.Button(footer, text="Stop", bootstyle="danger", width=15, command=lambda: stop_scraping())
stop_btn.pack(side="left", padx=5)
stop_btn.config(state="disabled")

export_txt = tb.Button(footer, text="Export TXT", width=15, command=lambda: export_file("txt"))
export_txt.pack(side="left", padx=5)

export_csv = tb.Button(footer, text="Export CSV", width=15, command=lambda: export_file("csv"))
export_csv.pack(side="left", padx=5)

export_json = tb.Button(footer, text="Export JSON", width=15, command=lambda: export_file("json"))
export_json.pack(side="left", padx=5)

# ================= LOG =================
def log_line(t):
    log.text.config(state="normal")
    log.text.insert("end", t + "\n")
    log.text.see("end")
    log.text.config(state="disabled")

# ================= SCRAPER =================
def google_search(query):
    params = {"q": query, "num": 5}
    r = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    return [a["href"] for a in soup.select("a") if a.get("href", "").startswith("http")]

def scrape_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return set(EMAIL_REGEX.findall(r.text))
    except:
        return set()

def run_scraper(queries):
    global scrape_completed

    for q in queries:
        if stop_event.is_set(): return
        log_line(f"🔍 Searching: {q}")

        urls = google_search(q)
        for url in urls:
            if stop_event.is_set(): return

            emails = scrape_page(url)
            for e in emails:
                if e not in emails_found:
                    emails_found.add(e)
                    sources[e].append(url)
                    log_line(e)

            time.sleep(0.6)

    scrape_completed = True
    show_info("Done", f"Found {len(emails_found)} public emails.")
    stop_btn.config(state="disabled")
    start_btn.config(state="normal")

def start_scraping():
    global scrape_completed
    scrape_completed = False
    stop_event.clear()
    emails_found.clear()
    sources.clear()

    queries = [q.strip() for q in keywords_input.get("1.0", "end").splitlines() if q.strip()]
    if not queries:
        show_error("Input Error", "Please enter at least one search query.")
        return

    log.text.config(state="normal")
    log.text.delete("1.0", "end")
    log.text.config(state="disabled")

    stop_btn.config(state="normal")
    start_btn.config(state="disabled")

    threading.Thread(target=run_scraper, args=(queries,), daemon=True).start()

def stop_scraping():
    stop_event.set()
    log_line("⛔ Stopped by user")
    stop_btn.config(state="disabled")
    start_btn.config(state="normal")

# ================= EXPORT =================
def export_file(fmt):
    if not emails_found or not scrape_completed:
        show_error("Export Error", "Nothing to export.")
        return

    path = filedialog.asksaveasfilename(defaultextension=f".{fmt}")
    if not path: return

    if fmt == "txt":
        with open(path, "w") as f:
            for e in sorted(emails_found):
                f.write(e + "\n")

    elif fmt == "csv":
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["email", "source"])
            for e, s in sources.items():
                w.writerow([e, ", ".join(s)])

    elif fmt == "json":
        with open(path, "w") as f:
            json.dump(sources, f, indent=2)

    show_info("Exported", "File saved successfully.")

app.mainloop()
