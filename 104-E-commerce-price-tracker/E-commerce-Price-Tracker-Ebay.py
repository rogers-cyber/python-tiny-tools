import threading
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
from urllib.parse import urlparse

from urllib.parse import urlparse

ALLOWED_HOSTS = {"www.ebay.com", "ebay.com"}

def is_allowed_ebay_url(url):
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname.lower() if parsed.hostname else ""
        return hostname in ALLOWED_HOSTS
    except Exception:
        return False

# =================== Utility Functions ===================
def resource_path(file_name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ------------------- eBay URL Cleaning -------------------
def clean_ebay_url(url):
    """Return canonical eBay URL (strip query parameters)."""
    if "ebay.com/itm/" in url:
        parts = url.split("/itm/")
        item_id = parts[1].split("?")[0]
        return f"https://www.ebay.com/itm/{item_id}"
    return url

# ------------------- Price Fetching -------------------
def fetch_price(url):
    """Fetch price from Amazon or eBay product page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        # Clean eBay URLs
        if is_allowed_ebay_url(url):
            url = clean_ebay_url(url)
        else:
            return "Error: URL not allowed"

        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # ---------------- eBay ----------------
        if is_allowed_ebay_url(url):
            selectors = [
                'span[itemprop="price"]',  # auction
                'span#prcIsum',            # buy-it-now
                'span#mm-saleDscPrc',      # discounted
                'span.s-item__price',      # modern layout
                'span.notranslate',        # sometimes price
            ]
            # try each selector
            for sel in selectors:
                el = soup.select_one(sel)
                if el and "$" in el.get_text(strip=True):
                    return el.get_text(strip=True)
            # fallback: find any <span> with $ in text
            for el in soup.find_all("span"):
                text = el.get_text(strip=True)
                if "$" in text:
                    return text
            return "Price not found"

        else:
            return "Unsupported site"

    except Exception as e:
        return f"Error: {str(e)}"

# =================== E-commerce Price Tracker ===================
class PriceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("E-commerce Price Tracker - Ebay.com")
        self.root.geometry("1000x600")
        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except Exception:
            pass

        # ===== Buttons Frame =====
        button_frame = tb.Frame(self.root)
        button_frame.pack(pady=10)

        self.track_btn = tb.Button(button_frame, text="📈 Track Prices", bootstyle="success-outline", width=20,
                                   command=self.start_tracking)
        self.track_btn.grid(row=0, column=0, padx=5)

        self.clear_btn = tb.Button(button_frame, text="🧹 Clear Log", bootstyle="warning-outline", width=20,
                                   command=self.clear_log)
        self.clear_btn.grid(row=0, column=1, padx=5)

        self.cancel_btn = tb.Button(button_frame, text="❌ Cancel", bootstyle="danger-outline", width=20,
                                    state="disabled", command=self.cancel_tracking)
        self.cancel_btn.grid(row=0, column=2, padx=5)

        self.about_btn = tb.Button(button_frame, text="ℹ️ About", bootstyle="secondary-outline", width=20,
                                   command=self.show_about_guide)
        self.about_btn.grid(row=0, column=3, padx=5)

        # ===== Log Area =====
        self.log_area = scrolledtext.ScrolledText(self.root, wrap="word", font=("Arial", 12))
        self.log_area.pack(expand=True, fill="both", padx=10, pady=10)

        # ===== Progress Bar =====
        progress_frame = tb.Frame(self.root)
        progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_label = tb.Label(progress_frame, text="Ready")
        self.progress_label.pack(side="left", padx=(0, 10))
        self.progress = tb.Progressbar(progress_frame, bootstyle="success-striped", mode="determinate")
        self.progress.pack(side="right", fill="x", expand=True)

        # ===== Drag & Drop =====
        self.urls_to_track = []
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._handle_drop)

        # ===== Cancel Event =====
        self.cancel_event = threading.Event()

    # ===== Drag & Drop =====
    def _handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        for path in paths:
            if os.path.isfile(path):
                with open(path, "r") as f:
                    urls = [line.strip() for line in f if line.strip()]
                    self.urls_to_track.extend(urls)
        self._log(f"Loaded {len(paths)} file(s) with URLs.")

    # ===== Logging =====
    def _log(self, message):
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")

    def clear_log(self):
        self.log_area.delete(1.0, "end")

    # ===== Cancel =====
    def cancel_tracking(self):
        self.cancel_event.set()
        self.progress_label.config(text="Cancelling...")

    # ===== Worker Thread =====
    def _track_worker(self, urls):
        total = len(urls)
        if total == 0:
            self._log("No URLs to track.")
            self.root.after(0, self._reset_ui)
            return

        step = 100 / total
        current_progress = 0

        for url in urls:
            if self.cancel_event.is_set():
                self.root.after(0, self._reset_ui)
                self._log("Tracking cancelled.")
                return
            price = fetch_price(url)
            self._log(f"{url} → {price}")
            current_progress += step
            self.root.after(0, self._update_progress, current_progress)
            time.sleep(0.5)  # avoid spamming requests

        self.root.after(0, self._reset_ui)
        self._log("Tracking completed.")

    # ===== Progress Update =====
    def _update_progress(self, value):
        self.progress["value"] = value
        self.progress_label.config(text=f"Processing... {int(value)}%")

    # ===== Reset UI =====
    def _reset_ui(self):
        self.progress["value"] = 0
        self.progress_label.config(text="Ready")
        self.track_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.cancel_event.clear()
        self.urls_to_track.clear()

    # ===== Start Tracking =====
    def start_tracking(self):
        if not self.urls_to_track:
            paths = filedialog.askopenfilenames(title="Select text files containing product URLs")
            if not paths:
                return
            for path in paths:
                with open(path, "r") as f:
                    urls = [line.strip() for line in f if line.strip()]
                    self.urls_to_track.extend(urls)
        if not self.urls_to_track:
            self._log("No URLs provided.")
            return

        self.cancel_event.clear()
        self.track_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_label.config(text="Preparing...")
        self.progress["value"] = 0

        threading.Thread(target=self._track_worker, args=(self.urls_to_track,), daemon=True).start()

    # ===== About / Guide =====
    def show_about_guide(self):
        guide_window = tb.Toplevel(self.root)
        guide_window.title("📘 About / Guide")
        guide_window.geometry("700x500")
        guide_window.resizable(False, False)
        guide_window.grab_set()
        guide_window.attributes("-toolwindow", True)

        self.root.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        win_width = 700
        win_height = 500
        pos_x = root_x + (root_width // 2) - (win_width // 2)
        pos_y = root_y + (root_height // 2) - (win_height // 2)
        guide_window.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")

        container = tb.Frame(guide_window)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, borderwidth=0)
        scrollbar = tb.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas, padding=10)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        sections = {
            "About Price Tracker": (
                "This tool tracks prices of Amazon and eBay products from given URLs.\n"
                "Supports loading URLs from text files or drag & drop, with progress and logging."
            ),
            "Key Features": (
                "- Track prices from multiple URLs\n"
                "- Supports drag & drop of text files with URLs\n"
                "- Real-time progress updates\n"
                "- Cancel tracking anytime\n"
                "- Clean, modern UI"
            ),
            "Usage": (
                "1. Drag & drop text files containing product URLs or select them manually.\n"
                "2. Click 'Track Prices'.\n"
                "3. The tool fetches and logs prices of all products.\n"
                "4. Cancel anytime if needed."
            ),
            "Supported Sites": (
                "- eBay.com\n"
                "Automatically cleans eBay URLs and detects auction or buy-it-now prices."
            ),
            "Developer": (
                "Developed by MateTools\n"
                "https://matetools.gumroad.com"
            )
        }

        for title, text in sections.items():
            tb.Label(scrollable_frame, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 0))
            tb.Label(scrollable_frame, text=text, font=("Segoe UI", 10), wraplength=660, justify="left").pack(anchor="w", pady=(2, 5))

        tb.Button(scrollable_frame, text="Close", bootstyle="danger-outline", width=15,
                  command=guide_window.destroy).pack(pady=10)

# =================== Main ===================
if __name__ == "__main__":
    app = TkinterDnD.Tk()
    style = tb.Style(theme="cosmo")
    PriceTracker(app)
    app.mainloop()
