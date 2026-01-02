import socket
import threading
import tkinter as tk
import json
import sqlite3
from datetime import datetime
from typing import Dict

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

# ================== CONFIG ================== #
HOST = "0.0.0.0"          # LAN / WAN support
PORT = 5050
BUFFER_SIZE = 4096
DB_FILE = "chat.db"

# ================== DATABASE ================== #
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            content TEXT,
            reply_to TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_message(sender, content, reply_to=None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (sender, content, reply_to, timestamp) VALUES (?, ?, ?, ?)",
        (sender, content, reply_to, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def load_history(limit=50):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT sender, content, reply_to, timestamp FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return reversed(rows)

# ================== SERVER ================== #
clients: Dict[socket.socket, str] = {}
server_running = True


def start_server(log_callback):
    init_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    log_callback(f"Server running on {HOST}:{PORT}")

    def broadcast(message):
        for c in list(clients.keys()):
            try:
                c.send(message.encode())
            except:
                clients.pop(c, None)

    def handle_client(conn, addr):
        try:
            username = conn.recv(BUFFER_SIZE).decode()
            clients[conn] = username

            # Send chat history
            for sender, content, reply_to, ts in load_history():
                prefix = f"[{ts}] {sender}:"
                if reply_to:
                    conn.send(f"{prefix} ↪ {reply_to}\n{content}".encode())
                else:
                    conn.send(f"{prefix} {content}".encode())

            broadcast(f"[SERVER] 🟢 {username} joined the chat")
            log_callback(f"{username} connected from {addr}")

            while server_running:
                raw = conn.recv(BUFFER_SIZE).decode()
                if not raw:
                    break

                data = json.loads(raw)
                msg = data.get("msg", "")
                reply_to = data.get("reply_to")
                ts = datetime.now().strftime("%H:%M")

                save_message(username, msg, reply_to)

                if reply_to:
                    broadcast(f"[{ts}] {username}: ↪ {reply_to}\n{msg}")
                else:
                    broadcast(f"[{ts}] {username}: {msg}")

        except Exception as e:
            log_callback(f"Client error: {e}")
        finally:
            name = clients.pop(conn, "Unknown")
            conn.close()
            broadcast(f"[SERVER] 🔴 {name} left the chat")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# ================== CLIENT ================== #
class ChatClient:
    def __init__(self, username, host, message_callback):
        self.username = username
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, PORT))
        self.sock.send(username.encode())
        self.message_callback = message_callback
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                msg = self.sock.recv(BUFFER_SIZE).decode()
                if msg:
                    self.message_callback(msg)
            except:
                break

    def send(self, msg, reply_to=None):
        payload = json.dumps({"msg": msg, "reply_to": reply_to})
        self.sock.send(payload.encode())

# ================== UI ================== #
app = tb.Window(
    title="Distributed Chat Application",
    themename="darkly",
    size=(900, 650)
)

username = ""
server_ip = ""
client = None
reply_target = None

# ---------- LOGIN ---------- #
login = tb.Frame(app, padding=30)
login.pack(fill=tk.BOTH, expand=True)

tb.Label(login, text="Username").pack()
user_entry = tb.Entry(login)
user_entry.pack(fill=tk.X, pady=5)

tb.Label(login, text="Server IP (LAN / WAN)").pack()
ip_entry = tb.Entry(login)
ip_entry.insert(0, "127.0.0.1")
ip_entry.pack(fill=tk.X, pady=5)


def join_chat():
    global username, server_ip, client
    username = user_entry.get().strip()
    server_ip = ip_entry.get().strip()
    if username and server_ip:
        login.pack_forget()
        chat.pack(fill=tk.BOTH, expand=True)
        client = ChatClient(username, server_ip, display_message)
        display_message(f"[SYSTEM] Connected as {username}")


tb.Button(login, text="Join Chat", bootstyle="success", command=join_chat).pack(pady=15)

# ---------- CHAT ---------- #
chat = tb.Frame(app)

chat_box = ScrolledText(chat)
chat_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
chat_box.text.configure(state="disabled")

reply_label = tb.Label(chat, text="", bootstyle="warning")
reply_label.pack(anchor=tk.W, padx=10)

entry_frame = tb.Frame(chat)
entry_frame.pack(fill=tk.X, padx=10, pady=5)

msg_entry = tb.Entry(entry_frame)
msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)


def send_message():
    global reply_target
    text = msg_entry.get().strip()
    if text:
        client.send(text, reply_target)
        reply_target = None
        reply_label.config(text="")
        msg_entry.delete(0, tk.END)


msg_entry.bind("<Return>", lambda e: send_message())


def on_click(event):
    global reply_target
    idx = chat_box.text.index("@%s,%s linestart" % (event.x, event.y))
    line = chat_box.text.get(idx, idx + " lineend").strip()
    reply_target = line
    reply_label.config(text=f"Replying to: {line[:50]}...")


def display_message(msg):
    chat_box.text.configure(state="normal")
    chat_box.text.insert("end", msg + "\n")
    chat_box.text.see("end")
    chat_box.text.configure(state="disabled")


chat_box.text.bind("<Button-1>", on_click)

tb.Button(entry_frame, text="Send", bootstyle="primary", command=send_message).pack(side=tk.RIGHT)

# ---------- START SERVER THREAD ---------- #
threading.Thread(target=start_server, args=(display_message,), daemon=True).start()

app.mainloop()
