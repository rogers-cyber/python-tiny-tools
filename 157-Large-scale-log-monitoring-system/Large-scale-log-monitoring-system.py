import socket
import threading
import tkinter as tk
import json
import sqlite3
from datetime import datetime
from typing import Dict

import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText

# ================== CONFIG ================== #
PORT = 6061
BUFFER_SIZE = 8192
DB_FILE = "logs.db"
SERVER_PASSWORD = "LogSecure123"

# ================== UTILITY ================== #
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

HOST = get_local_ip()

# ================== DATABASE ================== #
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            level TEXT,
            message TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_log(source, level, message):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (source, level, message, timestamp) VALUES (?, ?, ?, ?)",
        (source, level, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def load_logs(limit=500):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT source, level, message, timestamp FROM logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return reversed(rows)

# ================== SERVER ================== #
clients: Dict[socket.socket, str] = {}
server_running = True

def start_log_server(log_callback):
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
    except Exception as e:
        log_callback(f"[SERVER] Error binding server: {e}")
        return

    server.listen()
    log_callback(f"[SERVER] Running on {HOST}:{PORT}")

    def broadcast_json(log_entry: dict):
        """Send structured log JSON to all connected clients."""
        payload = json.dumps(log_entry).encode()
        for c in list(clients.keys()):
            try:
                c.send(payload + b"\n")  # newline to separate messages
            except Exception:
                clients.pop(c, None)

    def handle_client(conn, addr):
        try:
            conn.send("Enter server password:".encode())
            pw = conn.recv(BUFFER_SIZE).decode().strip()
            if pw != SERVER_PASSWORD:
                conn.send("❌ Wrong password. Connection closed.".encode())
                conn.close()
                log_callback(f"[SERVER] Rejected connection from {addr}")
                return

            conn.send("Password accepted. Send source name:".encode())
            source = conn.recv(BUFFER_SIZE).decode().strip()
            clients[conn] = source

            # Send recent logs as structured JSON
            for src, level, msg, ts in load_logs():
                log_entry = {
                    "timestamp": ts.split()[1] if " " in ts else ts,
                    "source": src,
                    "level": level,
                    "msg": msg
                }
                try:
                    conn.send(json.dumps(log_entry).encode() + b"\n")
                except Exception:
                    continue

            # Notify server GUI
            log_callback({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": "SERVER",
                "level": "INFO",
                "msg": f"{source} connected from {addr}"
            })
            broadcast_json({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": "SERVER",
                "level": "INFO",
                "msg": f"🟢 {source} connected"
            })

            while server_running:
                raw = conn.recv(BUFFER_SIZE)
                if not raw:
                    break
                try:
                    data = json.loads(raw.decode())
                    level = data.get("level", "INFO")
                    msg = data.get("msg", "")
                    ts = datetime.now().strftime("%H:%M:%S")

                    # Save to DB
                    save_log(source, level, msg)

                    log_entry = {
                        "timestamp": ts,
                        "source": source,
                        "level": level,
                        "msg": msg
                    }

                    # Broadcast structured log to all clients
                    broadcast_json(log_entry)

                    # Show in GUI
                    log_callback(log_entry)
                except json.JSONDecodeError:
                    log_callback({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "source": source,
                        "level": "ERROR",
                        "msg": "Invalid JSON received"
                    })

        except Exception as e:
            log_callback({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": "SERVER",
                "level": "ERROR",
                "msg": f"Client error: {e}"
            })
        finally:
            name = clients.pop(conn, "Unknown")
            conn.close()
            broadcast_json({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": "SERVER",
                "level": "INFO",
                "msg": f"🔴 {name} disconnected"
            })
            log_callback({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": "SERVER",
                "level": "INFO",
                "msg": f"{name} disconnected from {addr}"
            })

    while server_running:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            log_callback({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": "SERVER",
                "level": "ERROR",
                "msg": f"Accept error: {e}"
            })
            break

# ================== CLIENT ================== #
class LogClient:
    def __init__(self, source_name, host, password, log_callback):
        self.source_name = source_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, PORT))
        self.log_callback = log_callback

        # Authentication
        self.sock.recv(BUFFER_SIZE)
        self.sock.send(password.encode())
        self.sock.recv(BUFFER_SIZE)
        self.sock.send(source_name.encode())

        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        buffer = b""
        while True:
            try:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    break
                buffer += data
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        log_entry = json.loads(line.decode())
                        self.log_callback(log_entry)  # directly structured
                    except json.JSONDecodeError:
                        # fallback for raw messages
                        self.log_callback({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "source": "SERVER",
                            "level": "ERROR",
                            "msg": line.decode(errors="ignore")
                        })
            except Exception:
                break

    def send_log(self, level, msg):
        payload = json.dumps({"level": level, "msg": msg})
        self.sock.send(payload.encode())

# ================== GUI ================== #
app = tb.Window(title="Centralized Log Monitoring", themename="darkly", size=(1000, 700))

# ---------- SERVER CONTROL PANEL ---------- #
control_frame = tb.Frame(app, padding=10)
control_frame.pack(fill=tk.X)

server_status_var = tk.StringVar(value="Running")
tb.Label(control_frame, text="Server Status:").pack(side=tk.LEFT)
server_status_label = tb.Label(control_frame, textvariable=server_status_var, bootstyle="success")
server_status_label.pack(side=tk.LEFT, padx=5)

connected_clients_var = tk.StringVar(value="Connected Clients: 0")
tb.Label(control_frame, textvariable=connected_clients_var).pack(side=tk.LEFT, padx=20)

# ---------- LOGIN FRAME ---------- #
login_frame = tb.Frame(app, padding=20)
login_frame.pack(fill=tk.BOTH, expand=True)

tb.Label(login_frame, text="Source Name").pack()
source_entry = tb.Entry(login_frame)
source_entry.pack(fill=tk.X, pady=5)

tb.Label(login_frame, text="Server IP (LAN)").pack()
ip_entry = tb.Entry(login_frame)
ip_entry.insert(0, HOST)
ip_entry.pack(fill=tk.X, pady=5)

tb.Label(login_frame, text="Server Password").pack()
pw_entry = tb.Entry(login_frame, show="*")
pw_entry.pack(fill=tk.X, pady=5)

client = None

def start_client():
    global client
    source = source_entry.get().strip()
    ip = ip_entry.get().strip()
    pw = pw_entry.get().strip()
    if source and ip and pw:
        try:
            login_frame.pack_forget()
            main_frame.pack(fill=tk.BOTH, expand=True)
            client = LogClient(source, ip, pw, add_log)
            display_logs()
            add_log(f"[SYSTEM] Connected as {source}")
        except Exception as e:
            tk.messagebox.showerror("Connection Failed", f"Cannot connect to server:\n{e}")

tb.Button(login_frame, text="Connect to Server", bootstyle="success", command=start_client).pack(pady=15)

# ---------- MAIN FRAME ---------- #
main_frame = tb.Frame(app)

# Filters
filter_frame = tb.Frame(main_frame)
filter_frame.pack(fill=tk.X, padx=10, pady=5)

tb.Label(filter_frame, text="Filter by Source:").pack(side=tk.LEFT)
source_filter = tk.StringVar(value="All")
source_menu = tb.OptionMenu(filter_frame, source_filter, "All")
source_menu.pack(side=tk.LEFT, padx=5)

tb.Label(filter_frame, text="Filter by Level:").pack(side=tk.LEFT, padx=(20,0))
level_filter = tk.StringVar(value="All")
level_menu = tb.OptionMenu(filter_frame, level_filter, "All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
level_menu.pack(side=tk.LEFT, padx=(20,0))

tb.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(20,0))
search_var = tk.StringVar()
search_entry = tb.Entry(filter_frame, textvariable=search_var)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

def apply_filters(*args):
    display_logs()

source_filter.trace_add("write", apply_filters)
level_filter.trace_add("write", apply_filters)
search_var.trace_add("write", apply_filters)

# Log display
log_box = ScrolledText(main_frame)
log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
log_box.text.configure(state="disabled")

# Message entry
entry_frame = tb.Frame(main_frame)
entry_frame.pack(fill=tk.X, padx=10, pady=5)

level_var = tk.StringVar(value="INFO")
level_send_menu = tb.OptionMenu(entry_frame, level_var, "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
level_send_menu.pack(side=tk.LEFT, padx=5)

msg_entry = tb.Entry(entry_frame)
msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

def send_log():
    if client:
        msg = msg_entry.get().strip()
        if msg:
            client.send_log(level_var.get(), msg)
            msg_entry.delete(0, tk.END)

msg_entry.bind("<Return>", lambda e: send_log())
tb.Button(entry_frame, text="Send Log", bootstyle="primary", command=send_log).pack(side=tk.RIGHT)

# ================= LOG MANAGEMENT ================= #
log_storage: list[dict] = []  # List of structured logs
seen_logs = set()  # Track unique logs if needed

LEVEL_COLORS = {
    "DEBUG": "gray",
    "INFO": "white",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red4"
}

# Thread-safe log addition
def add_log(log: dict | str):
    """
    Add a log entry to storage and refresh GUI safely.
    Accepts either:
      - a structured dict: {"timestamp", "source", "level", "msg"}
      - a raw string (for system messages)
    """
    def _add():
        # If it's a string, wrap it as a system log
        if isinstance(log, str):
            entry = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": "SYSTEM",
                "level": "INFO",
                "msg": log
            }
        else:
            entry = log

        # Optional: prevent exact duplicates
        key = (entry["timestamp"], entry["source"], entry["level"], entry["msg"])
        if key not in seen_logs:
            seen_logs.add(key)
            log_storage.append(entry)
            display_logs()

    app.after(0, _add)  # Schedule GUI update in main thread

# Display logs in ScrolledText with filters
def display_logs():
    log_box.text.configure(state="normal")
    log_box.text.delete("1.0", tk.END)

    f_source = source_filter.get()
    f_level = level_filter.get()
    f_search = search_var.get().lower()

    for entry in log_storage:
        # Apply filters
        if f_source != "All" and entry["source"] != f_source:
            continue
        if f_level != "All" and entry["level"] != f_level:
            continue
        if f_search and f_search not in entry["msg"].lower() and f_search not in entry["source"].lower():
            continue

        ts = entry["timestamp"]
        src = entry["source"]
        level = entry["level"]
        msg = entry["msg"]

        log_line = f"[{ts}] {src} [{level}]: {msg}"

        color_tag = LEVEL_COLORS.get(level, "white")
        if level == "CRITICAL":
            log_box.text.insert("end", log_line + "\n", ("critical",))
        else:
            log_box.text.insert("end", log_line + "\n", (color_tag,))

    # Configure tags
    for level_name, color in LEVEL_COLORS.items():
        log_box.text.tag_configure(color, foreground=color)
    log_box.text.tag_configure("critical", foreground="red4", font=("TkDefaultFont", 10, "bold"))

    log_box.text.see("end")
    log_box.text.configure(state="disabled")
    update_sources()  # Update source filter options dynamically

# Update source filter dropdown safely
def update_sources():
    current_selection = source_filter.get()
    sources = {entry["source"] for entry in log_storage}

    menu = source_menu["menu"]
    menu.delete(0, "end")
    menu.add_command(label="All", command=lambda: source_filter.set("All"))
    for s in sorted(sources):
        menu.add_command(label=s, command=lambda x=s: source_filter.set(x))

    # Restore previous selection if still valid
    if current_selection in sources or current_selection == "All":
        source_filter.set(current_selection)
    else:
        source_filter.set("All")

def periodic_update():
    update_sources()
    # Update connected clients count dynamically
    connected_clients_var.set(f"Connected Clients: {len(clients)}")
    app.after(2000, periodic_update)

app.after(2000, periodic_update)

# ---------- START SERVER THREAD ---------- #
threading.Thread(target=start_log_server, args=(add_log,), daemon=True).start()

app.mainloop()
