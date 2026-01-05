import threading
import webbrowser
import tkinter as tk
from dataclasses import dataclass
from typing import List
import time
import random

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ---------------- CONFIG ---------------- #
UPDATE_INTERVAL = 2  # seconds between auto transactions
PROCESSING_DELAY = 1  # seconds to simulate network processing

# Payment methods with success probabilities
PAYMENT_METHODS = {
    "Credit Card": 0.85,
    "UPI": 0.95,
    "Wallet": 0.9
}

FAILURE_REASONS = [
    "Insufficient Funds",
    "Network Error",
    "Card Expired",
    "Payment Gateway Timeout",
    "Invalid Credentials"
]

# ---------------- GLOBAL STATE ---------------- #
payment_active = False
transaction_history: List["Transaction"] = []

# ---------------- DATA STRUCTURE ---------------- #
@dataclass(frozen=True)
class Transaction:
    timestamp: str
    method: str
    amount: float
    status: str
    reference_id: str
    failure_reason: str = ""  # Optional

# ---------------- PAYMENT SIMULATION ---------------- #
def generate_transaction(method=None, amount=None) -> Transaction:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if method is None:
        method = random.choice(list(PAYMENT_METHODS.keys()))
    if amount is None:
        amount = round(random.uniform(5, 500), 2)
    status = "⏳ Pending"
    reference_id = f"{method[:2].upper()}{random.randint(100000,999999)}"
    return Transaction(timestamp, method, amount, status, reference_id)

def finalize_transaction(txn: Transaction):
    success_prob = PAYMENT_METHODS[txn.method]
    if random.random() < success_prob:
        return Transaction(txn.timestamp, txn.method, txn.amount, "✅ Success", txn.reference_id)
    else:
        reason = random.choice(FAILURE_REASONS)
        return Transaction(txn.timestamp, txn.method, txn.amount, "❌ Failed", txn.reference_id, failure_reason=reason)

# ---------------- PROCESSING THREAD ---------------- #
def processing_loop():
    global payment_active
    while payment_active:
        txn = generate_transaction()
        transaction_history.append(txn)
        app.after(0, lambda t=txn: display_transaction(t))
        time.sleep(PROCESSING_DELAY)

        # Finalize the pending transaction
        finalized_txn = finalize_transaction(txn)
        transaction_history[-1] = finalized_txn
        app.after(0, lambda t=finalized_txn: update_transaction_display(t))
        time.sleep(UPDATE_INTERVAL - PROCESSING_DELAY)

# ---------------- UI HELPERS ---------------- #
def format_transaction_text(txn: Transaction) -> str:
    base = f"💰 {txn.timestamp}\nMethod: {txn.method}\nAmount: ${txn.amount}\nStatus: {txn.status}\nRef: {txn.reference_id}"
    if txn.status == "❌ Failed" and txn.failure_reason:
        base += f"\nReason: {txn.failure_reason}"
    return base + "\n\n"

def display_transaction(txn: Transaction):
    text.configure(state="normal")
    text.insert("end", format_transaction_text(txn))
    text.see("end")
    text.configure(state="disabled")
    update_stats()

def update_transaction_display(txn: Transaction):
    # Update last transaction to finalized status
    text.configure(state="normal")
    text.delete("end-8l", "end")
    text.insert("end", format_transaction_text(txn))
    text.see("end")
    text.configure(state="disabled")
    update_stats()

def open_gateway_docs():
    webbrowser.open_new_tab("https://www.example-payment-gateway.com/docs")

# ---------------- STATS & CHART ---------------- #
def update_stats():
    success = sum(1 for t in transaction_history if t.status == "✅ Success")
    failed = sum(1 for t in transaction_history if t.status == "❌ Failed")
    pending = sum(1 for t in transaction_history if t.status == "⏳ Pending")
    stats_label.config(text=f"✅ {success}  ❌ {failed}  ⏳ {pending}")

    # Update pie chart safely
    ax.clear()
    labels = ["Success", "Failed", "Pending"]
    sizes = [success, failed, pending]
    colors = ["green", "red", "orange"]

    if sum(sizes) == 0:
        # Draw a blank circle instead of pie chart
        ax.text(0.5, 0.5, "No Transactions", ha="center", va="center", fontsize=12)
        ax.axis("off")
    else:
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

    canvas.draw()

# ---------------- CONTROL FUNCTIONS ---------------- #
def start_processing():
    global payment_active
    if payment_active:
        return
    payment_active = True
    status_label.config(text="🟢 Payment Processing Active", bootstyle="success")
    threading.Thread(target=processing_loop, daemon=True).start()

def stop_processing():
    global payment_active
    payment_active = False
    status_label.config(text="🔴 Payment Processing Stopped", bootstyle="danger")

def clear_history():
    transaction_history.clear()
    text.configure(state="normal")
    text.delete("1.0", "end")
    text.configure(state="disabled")
    update_stats()

# ---------------- MANUAL PAYMENT SUBMISSION ---------------- #
def submit_payment():
    method = method_var.get()
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            raise ValueError
    except ValueError:
        tb.messagebox.showerror("Invalid Amount", "Please enter a valid positive number for amount.")
        return

    txn = generate_transaction(method, amount)
    transaction_history.append(txn)
    display_transaction(txn)

    # Simulate processing delay in background
    def finalize():
        time.sleep(PROCESSING_DELAY)
        finalized_txn = finalize_transaction(txn)
        transaction_history[-1] = finalized_txn
        app.after(0, lambda t=finalized_txn: update_transaction_display(t))
    threading.Thread(target=finalize, daemon=True).start()

# ---------------- TRANSACTION SEARCH/FILTER ---------------- #
def filter_transactions():
    query_method = filter_method_var.get()
    query_status = filter_status_var.get().lower()
    query_ref = filter_ref_entry.get().strip().lower()

    text.configure(state="normal")
    text.delete("1.0", "end")
    for txn in transaction_history:
        if query_method != "All" and txn.method != query_method:
            continue
        if query_status != "all" and txn.status.lower() != query_status:
            continue
        if query_ref and query_ref not in txn.reference_id.lower():
            continue
        text.insert("end", format_transaction_text(txn))
    text.configure(state="disabled")

# ---------------- UI SETUP ---------------- #
app = tb.Window(
    title="Online Payment Gateway Simulator",
    themename="darkly",
    size=(1000, 700),
    resizable=(True, True),
)

# Top section
top = tb.Frame(app, padding=15)
top.pack(fill=tk.X)
tb.Label(top, text="💳 Online Payment Gateway Simulator", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)
status_label = tb.Label(top, text="🔴 Payment Processing Stopped", bootstyle="danger")
status_label.pack(anchor=tk.W, pady=5)

# Auto transaction buttons
btn_frame = tb.Frame(app)
btn_frame.pack(fill=tk.X, pady=5)
tb.Button(btn_frame, text="▶ Start Auto Transactions", bootstyle="success", command=start_processing).pack(side=tk.LEFT, padx=5)
tb.Button(btn_frame, text="⏹ Stop Auto Transactions", bootstyle="danger", command=stop_processing).pack(side=tk.LEFT, padx=5)
tb.Button(btn_frame, text="📄 Docs", bootstyle="info", command=open_gateway_docs).pack(side=tk.LEFT, padx=5)
tb.Button(btn_frame, text="🧹 Clear", bootstyle="warning", command=clear_history).pack(side=tk.LEFT, padx=5)

# Manual payment section
manual_frame = tb.Labelframe(app, text="Manual Payment Submission", padding=10)
manual_frame.pack(fill=tk.X, pady=10)
method_var = tk.StringVar(value="Credit Card")
tb.Label(manual_frame, text="Payment Method:").pack(side=tk.LEFT, padx=5)
tb.OptionMenu(manual_frame, method_var, *PAYMENT_METHODS.keys()).pack(side=tk.LEFT, padx=5)
tb.Label(manual_frame, text="Amount:").pack(side=tk.LEFT, padx=5)
amount_entry = tb.Entry(manual_frame, width=10)
amount_entry.pack(side=tk.LEFT, padx=5)
amount_entry.insert(0, "100")
tb.Button(manual_frame, text="💳 Submit Payment", bootstyle="primary", command=submit_payment).pack(side=tk.LEFT, padx=10)

# Transaction filter/search section
filter_frame = tb.Labelframe(app, text="Search / Filter Transactions", padding=10)
filter_frame.pack(fill=tk.X, pady=10)
filter_method_var = tk.StringVar(value="All")
tb.Label(filter_frame, text="Method:").pack(side=tk.LEFT, padx=5)
tb.OptionMenu(filter_frame, filter_method_var, "All", *PAYMENT_METHODS.keys()).pack(side=tk.LEFT, padx=5)
filter_status_var = tk.StringVar(value="All")
tb.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
tb.OptionMenu(filter_frame, filter_status_var, "All", "✅ Success", "❌ Failed", "⏳ Pending").pack(side=tk.LEFT, padx=5)
tb.Label(filter_frame, text="Reference ID:").pack(side=tk.LEFT, padx=5)
filter_ref_entry = tb.Entry(filter_frame, width=15)
filter_ref_entry.pack(side=tk.LEFT, padx=5)
tb.Button(filter_frame, text="🔍 Filter", bootstyle="info", command=filter_transactions).pack(side=tk.LEFT, padx=10)

# Transaction log
result_frame = tb.Frame(app)
result_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
result_box = ScrolledText(result_frame)
result_box.pack(fill=tk.BOTH, expand=True)
text = result_box.text
text.configure(state="disabled", wrap="word")

# Stats & Pie Chart
stats_frame = tb.Frame(app, padding=10)
stats_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=False)
stats_label = tb.Label(stats_frame, text="✅ 0  ❌ 0  ⏳ 0", font=("Segoe UI", 12, "bold"))
stats_label.pack(pady=10)
fig, ax = plt.subplots(figsize=(4,4))
canvas = FigureCanvasTkAgg(fig, master=stats_frame)
canvas.get_tk_widget().pack()
ax.text(0.5, 0.5, "No Transactions", ha="center", va="center", fontsize=12)
ax.axis("off")

canvas.draw()

# Run app
app.mainloop()
