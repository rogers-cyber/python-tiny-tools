import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, asdict
from typing import List
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

# ---------------- CONFIG ---------------- #
CHAIN_FILE = "blockchain.json"
DIFFICULTY = 4
MINING_REWARD = 50

# ---------------- DATA STRUCTURES ---------------- #
@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    timestamp: float

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def compute_hash(self):
        data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [asdict(tx) for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

# ---------------- BLOCKCHAIN ---------------- #
class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending: List[Transaction] = []
        self.load()

    def create_genesis(self):
        block = Block(0, time.time(), [], "0")
        block.hash = block.compute_hash()
        self.chain.append(block)
        self.save()

    def load(self):
        if not os.path.exists(CHAIN_FILE):
            self.create_genesis()
            return
        with open(CHAIN_FILE, "r") as f:
            data = json.load(f)
            self.chain = [self.dict_to_block(b) for b in data]

    def save(self):
        with open(CHAIN_FILE, "w") as f:
            json.dump([self.block_to_dict(b) for b in self.chain], f, indent=2)

    def add_transaction(self, sender, recipient, amount):
        self.pending.append(Transaction(sender, recipient, amount, time.time()))

    def mine(self, miner):
        if not self.pending:
            return None

        self.pending.append(Transaction("SYSTEM", miner, MINING_REWARD, time.time()))

        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending.copy(),
            previous_hash=self.chain[-1].hash,
        )

        while True:
            block.hash = block.compute_hash()
            if block.hash.startswith("0" * DIFFICULTY):
                break
            block.nonce += 1

        self.chain.append(block)
        self.pending.clear()
        self.save()
        return block

    def is_valid(self):
        for i in range(1, len(self.chain)):
            c, p = self.chain[i], self.chain[i - 1]
            if c.hash != c.compute_hash():
                return False
            if c.previous_hash != p.hash:
                return False
        return True

    def balance(self, addr):
        bal = 0
        for b in self.chain:
            for t in b.transactions:
                if t.sender == addr:
                    bal -= t.amount
                if t.recipient == addr:
                    bal += t.amount
        return bal

    def block_to_dict(self, b):
        return {
            "index": b.index,
            "timestamp": b.timestamp,
            "transactions": [asdict(t) for t in b.transactions],
            "previous_hash": b.previous_hash,
            "nonce": b.nonce,
            "hash": b.hash,
        }

    def dict_to_block(self, d):
        txs = [Transaction(**t) for t in d["transactions"]]
        return Block(d["index"], d["timestamp"], txs, d["previous_hash"], d["nonce"], d["hash"])

# ---------------- GUI ---------------- #
class BlockchainGUI:
    def __init__(self, app):
        self.app = app
        self.chain = Blockchain()
        self.wallet = uuid.uuid4().hex

        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.app.title("🔗 Blockchain GUI")
        self.app.geometry("1000x700")

        top = tb.Frame(self.app, padding=15)
        top.pack(fill=X)

        tb.Label(top, text="🔗 Blockchain Explorer", font=("Segoe UI", 18, "bold")).pack(anchor=W)
        self.balance_lbl = tb.Label(top, text="")
        self.balance_lbl.pack(anchor=W, pady=5)
        tb.Label(top, text=f"👛 Wallet: {self.wallet}", font=("Segoe UI", 9)).pack(anchor=W)

        form = tb.Labelframe(self.app, text="Create Transaction", padding=10)
        form.pack(fill=X, padx=15, pady=10)

        self.to_var = tk.StringVar()
        self.amount_var = tk.DoubleVar()

        tb.Entry(form, textvariable=self.to_var).pack(fill=X, pady=5)
        tb.Entry(form, textvariable=self.amount_var).pack(fill=X, pady=5)

        tb.Button(form, text="Send Transaction", bootstyle=SUCCESS, command=self.send_tx).pack()

        actions = tb.Frame(self.app, padding=10)
        actions.pack(fill=X)

        tb.Button(actions, text="⛏ Mine Block", bootstyle=WARNING, command=self.mine).pack(side=LEFT, padx=5)
        tb.Button(actions, text="✔ Validate Chain", bootstyle=INFO, command=self.validate).pack(side=LEFT)

        view = tb.Labelframe(self.app, text="Blockchain", padding=10)
        view.pack(fill=BOTH, expand=True, padx=15, pady=10)

        self.text = ScrolledText(view)
        self.text.pack(fill=BOTH, expand=True)
        self.text.text.configure(state="disabled")

    def refresh(self):
        self.balance_lbl.config(text=f"💰 Balance: {self.chain.balance(self.wallet)}")
        self.text.text.configure(state="normal")
        self.text.text.delete("1.0", END)
        for block in self.chain.chain:
            self.text.text.insert(END, json.dumps(self.chain.block_to_dict(block), indent=2))
            self.text.text.insert(END, "\n\n")
        self.text.text.configure(state="disabled")

    def send_tx(self):
        if not self.to_var.get() or self.amount_var.get() <= 0:
            messagebox.showerror("Error", "Invalid transaction")
            return
        self.chain.add_transaction(self.wallet, self.to_var.get(), self.amount_var.get())
        messagebox.showinfo("Success", "Transaction added")

    def mine(self):
        block = self.chain.mine(self.wallet)
        if not block:
            messagebox.showwarning("Mine", "No transactions")
        else:
            messagebox.showinfo("Mine", f"Block #{block.index} mined!")
            self.refresh()

    def validate(self):
        ok = self.chain.is_valid()
        messagebox.showinfo("Validation", "Blockchain is valid ✔" if ok else "Blockchain corrupted ❌")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app = tb.Window(themename="darkly")
    BlockchainGUI(app)
    app.mainloop()
