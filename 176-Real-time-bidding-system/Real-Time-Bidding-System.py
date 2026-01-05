import threading
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time
import random

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

# ---------------- CONFIG ---------------- #
RESULTS_PER_PAGE = 6
BID_REFRESH_INTERVAL = 2  # seconds

# ---------------- GLOBAL STATE ---------------- #
all_auctions: List["AuctionItem"] = []
current_page = 1
bidding_active_ids: Dict[int, bool] = {}  # Track auto-bidding per item

# ---------------- DATA STRUCTURE ---------------- #
@dataclass
class AuctionItem:
    item_id: int
    name: str
    description: str
    starting_bid: float
    current_bid: float = 0.0
    highest_bidder: Optional[str] = None
    bids: List[Dict[str, float]] = field(default_factory=list)

# ---------------- AUCTION LOGIC ---------------- #
def place_bid(item: AuctionItem, bidder: str, amount: float):
    if amount <= item.current_bid:
        messagebox.showwarning("Invalid Bid", f"Your bid must be higher than current bid (${item.current_bid:.2f})")
        return False
    item.current_bid = round(amount, 2)
    item.highest_bidder = bidder
    item.bids.append({"bidder": bidder, "amount": item.current_bid})
    return True

def simulate_bid_for_item(item: AuctionItem):
    """Simulate auto-bidding for a specific item ID."""
    while bidding_active_ids.get(item.item_id, False):
        time.sleep(BID_REFRESH_INTERVAL)
        bid_increment = round(random.uniform(1, 20), 2)
        bidder = random.choice(["Alice", "Bob", "Charlie", "Dave"])
        new_bid = item.current_bid + bid_increment
        place_bid(item, bidder, new_bid)
        app.after(0, display_page)

def start_all_bidding():
    """Start auto-bidding for all items."""
    for item in all_auctions:
        if not bidding_active_ids[item.item_id]:
            bidding_active_ids[item.item_id] = True
            threading.Thread(target=simulate_bid_for_item, args=(item,), daemon=True).start()

def stop_all_bidding():
    """Stop auto-bidding for all items."""
    for item in all_auctions:
        bidding_active_ids[item.item_id] = False

# ---------------- UI HELPERS ---------------- #
def display_page():
    text.configure(state="normal")
    text.delete("1.0", "end")

    start = (current_page - 1) * RESULTS_PER_PAGE
    end = min(start + RESULTS_PER_PAGE, len(all_auctions))
    page_results = all_auctions[start:end]

    if not page_results:
        text.insert("end", "No auctions available.\n")
        text.configure(state="disabled")
        update_pagination()
        return

    for item in page_results:
        idx = item.item_id  # Global numbering
        text.insert("end", f"{idx}. {item.name}\n", f"title_{idx}")
        text.tag_config(f"title_{idx}", foreground="#1a0dab", font=("Segoe UI", 14, "bold"))

        text.insert("end", f"   Starting Bid: ${item.starting_bid:.2f}\n", f"start_{idx}")
        text.tag_config(f"start_{idx}", foreground="#006621", font=("Segoe UI", 10))

        text.insert("end", f"   Current Bid: ${item.current_bid:.2f}  |  Highest Bidder: {item.highest_bidder or 'None'}\n", f"current_{idx}")
        text.tag_config(f"current_{idx}", foreground="#D2691E", font=("Segoe UI", 10, "italic"))

        text.insert("end", f"   Description: {item.description}\n\n")
    text.configure(state="disabled")
    update_pagination()

def next_page():
    global current_page
    if current_page * RESULTS_PER_PAGE < len(all_auctions):
        current_page += 1
        display_page()

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()

def update_pagination():
    total_pages = max(1, (len(all_auctions) - 1) // RESULTS_PER_PAGE + 1)
    page_label.config(text=f"Page {current_page} of {total_pages}")
    prev_btn.config(state=DISABLED if current_page == 1 else NORMAL)
    next_btn.config(state=DISABLED if current_page == total_pages else NORMAL)

    # Spinbox max = number of items on current page
    start = (current_page - 1) * RESULTS_PER_PAGE
    end = min(start + RESULTS_PER_PAGE, len(all_auctions))
    item_index_spin.config(to=max(1, end - start))

# ---------------- AUCTION SETUP ---------------- #
def add_auction_item():
    name = item_name_entry.get().strip()
    desc = item_desc_entry.get().strip()
    try:
        start_bid = float(item_start_bid_entry.get().strip())
    except ValueError:
        messagebox.showwarning("Invalid Input", "Starting bid must be a number.")
        return
    if not name or name == "Item Name":
        messagebox.showwarning("Input Required", "Enter an item name.")
        return

    item = AuctionItem(
        item_id=len(all_auctions)+1,  # Global numbering
        name=name,
        description=desc,
        starting_bid=start_bid,
        current_bid=start_bid
    )
    all_auctions.append(item)
    bidding_active_ids[item.item_id] = False  # Default no auto-bidding
    display_page()
    # Reset entries
    reset_entry(item_name_entry, "Item Name")
    reset_entry(item_desc_entry, "Item Description")
    reset_entry(item_start_bid_entry, "Starting Bid")

def manual_bid():
    try:
        bid_amount = float(bid_amount_entry.get().strip())
    except ValueError:
        messagebox.showwarning("Invalid Input", "Bid amount must be a number.")
        return

    bidder = bidder_name_entry.get().strip()
    if not bidder or bidder == "Your Name":
        messagebox.showwarning("Input Required", "Enter your name.")
        return

    # Convert page-local index to global index
    try:
        page_local_idx = int(item_index_spin.get()) - 1
        global_idx = (current_page - 1) * RESULTS_PER_PAGE + page_local_idx
    except ValueError:
        messagebox.showwarning("Invalid Input", "Item index must be a number.")
        return

    if global_idx < 0 or global_idx >= len(all_auctions):
        messagebox.showwarning("Invalid Selection", "Select a valid item index.")
        return

    success = place_bid(all_auctions[global_idx], bidder, bid_amount)
    if success:
        display_page()
        reset_entry(bid_amount_entry, "Bid Amount")

# ---------------- AUTO-BIDDING BY ITEM ---------------- #
def start_bidding_for_item():
    try:
        bid_item_id = int(auto_bid_id_entry.get().strip())
    except ValueError:
        messagebox.showwarning("Invalid Input", "Item ID must be a number.")
        return

    # Find the item
    item = next((i for i in all_auctions if i.item_id == bid_item_id), None)
    if not item:
        messagebox.showwarning("Invalid ID", "No item with this ID exists.")
        return

    if not bidding_active_ids[item.item_id]:
        bidding_active_ids[item.item_id] = True
        threading.Thread(target=simulate_bid_for_item, args=(item,), daemon=True).start()

def stop_bidding_for_item():
    try:
        bid_item_id = int(auto_bid_id_entry.get().strip())
    except ValueError:
        messagebox.showwarning("Invalid Input", "Item ID must be a number.")
        return

    if bid_item_id in bidding_active_ids:
        bidding_active_ids[bid_item_id] = False

# ---------------- PLACEHOLDER UTIL ---------------- #
def add_placeholder(entry: tb.Entry, placeholder_text: str):
    entry.insert(0, placeholder_text)
    entry.config(foreground="grey")

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, "end")
            entry.config(foreground="black")

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(foreground="grey")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def reset_entry(entry: tb.Entry, placeholder_text: str):
    entry.delete(0, "end")
    entry.insert(0, placeholder_text)
    entry.config(foreground="grey")

# ---------------- UI SETUP ---------------- #
app = tb.Window(title="Real-Time Bidding System", themename="flatly", size=(1000, 720), resizable=(True, True))

# Top frame - Add auction items
top = tb.Frame(app, padding=15)
top.pack(fill=tk.X)
tb.Label(top, text="Add Auction Item", font=("Segoe UI", 16, "bold")).pack(anchor=tk.W)

item_name_entry = tb.Entry(top, font=("Segoe UI", 12))
item_name_entry.pack(fill=tk.X, pady=2)
add_placeholder(item_name_entry, "Item Name")

item_desc_entry = tb.Entry(top, font=("Segoe UI", 12))
item_desc_entry.pack(fill=tk.X, pady=2)
add_placeholder(item_desc_entry, "Item Description")

item_start_bid_entry = tb.Entry(top, font=("Segoe UI", 12))
item_start_bid_entry.pack(fill=tk.X, pady=2)
add_placeholder(item_start_bid_entry, "Starting Bid")

tb.Button(top, text="Add Item", bootstyle="success", command=add_auction_item).pack(anchor=tk.E, pady=5)

# Results frame
result_frame = tb.Frame(app, padding=(15, 5))
result_frame.pack(fill=tk.BOTH, expand=True)
result_box = ScrolledText(result_frame, autohide=True)
result_box.pack(fill=tk.BOTH, expand=True)
text = result_box.text
text.configure(state="disabled", wrap="word")

# Manual bid frame
bid_frame = tb.Frame(app, padding=10)
bid_frame.pack(fill=tk.X)

tb.Label(bid_frame, text="Bidder Name:").pack(side=tk.LEFT)
bidder_name_entry = tb.Entry(bid_frame, width=12)
bidder_name_entry.pack(side=tk.LEFT, padx=5)
add_placeholder(bidder_name_entry, "Your Name")

tb.Label(bid_frame, text="Item Index:").pack(side=tk.LEFT)
item_index_spin = tb.Spinbox(bid_frame, from_=1, to=RESULTS_PER_PAGE, width=5)
item_index_spin.pack(side=tk.LEFT, padx=5)

tb.Label(bid_frame, text="Bid Amount:").pack(side=tk.LEFT)
bid_amount_entry = tb.Entry(bid_frame, width=10)
bid_amount_entry.pack(side=tk.LEFT, padx=5)
add_placeholder(bid_amount_entry, "Bid Amount")

tb.Button(bid_frame, text="Place Bid", bootstyle="primary", command=manual_bid).pack(side=tk.LEFT, padx=5)

# Auto-bidding control
control_frame = tb.Frame(app, padding=10)
control_frame.pack(fill=tk.X)

tb.Label(control_frame, text="Item ID:").pack(side=tk.LEFT)
auto_bid_id_entry = tb.Entry(control_frame, width=5)
auto_bid_id_entry.pack(side=tk.LEFT, padx=5)
add_placeholder(auto_bid_id_entry, "ID")

tb.Button(control_frame, text="Start Item Bidding", bootstyle="success", command=start_bidding_for_item).pack(side=tk.LEFT, padx=5)
tb.Button(control_frame, text="Stop Item Bidding", bootstyle="danger", command=stop_bidding_for_item).pack(side=tk.LEFT, padx=5)

# Start/Stop All Bidding buttons
tb.Button(control_frame, text="Start All Bidding", bootstyle="success", command=start_all_bidding).pack(side=tk.LEFT, padx=5)
tb.Button(control_frame, text="Stop All Bidding", bootstyle="danger", command=stop_all_bidding).pack(side=tk.LEFT, padx=5)

# Pagination
nav = tb.Frame(app, padding=10)
nav.pack(fill=tk.X)
prev_btn = tb.Button(nav, text="← Prev", bootstyle="secondary", command=prev_page)
prev_btn.pack(side=tk.LEFT)
page_label = tb.Label(nav, text="Page 1", font=("Segoe UI", 10))
page_label.pack(side=tk.LEFT, padx=10)
next_btn = tb.Button(nav, text="Next →", bootstyle="secondary", command=next_page)
next_btn.pack(side=tk.LEFT)

# Start UI
app.mainloop()
