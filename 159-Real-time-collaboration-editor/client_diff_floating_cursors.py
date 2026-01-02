# client_diff_floating_cursors.py
import asyncio
import json
import tkinter as tk
import threading
import time
from tkinter import simpledialog, messagebox
from difflib import SequenceMatcher
import random

import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText
import websockets

# ---------------- CONFIG ---------------- #
SERVER_URI = "ws://127.0.0.1:8765"

# ---------------- GUI ---------------- #
app = tb.Window(title="Collaborative Editor (Floating Cursors)", themename="flatly", size=(900, 600))

top = tb.Frame(app, padding=10)
top.pack(fill=tk.X)
tb.Label(top, text="Collaborative Editor (Floating Cursors)", font=("Segoe UI", 16, "bold")).pack(anchor=tk.W)

editor_frame = tb.Frame(app, padding=10)
editor_frame.pack(fill=tk.BOTH, expand=True)

scrolled = ScrolledText(editor_frame, autohide=True)
scrolled.pack(fill=tk.BOTH, expand=True)
text_widget = scrolled.text
text_widget.configure(wrap="word")

# ---------------- USER SETUP ---------------- #
username = simpledialog.askstring("Username", "Enter your username:", parent=app)
if not username:
    messagebox.showerror("Error", "Username required")
    app.destroy()
    exit()

# ---------------- STATE ---------------- #
ignore_event = False
last_content = ""
cursor_widgets = {}  # username -> (canvas rectangle, label)
user_colors = {}     # username -> color
colors_list = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1",
               "#955251", "#B565A7", "#009B77", "#DD4124", "#45B8AC"]

def get_user_color(user):
    if user not in user_colors:
        color = random.choice(colors_list)
        user_colors[user] = color
    return user_colors[user]

# ---------------- DIFF HELPERS ---------------- #
def generate_diff(old, new):
    seq = SequenceMatcher(None, old, new)
    ops = []
    for tag, i1, i2, j1, j2 in seq.get_opcodes():
        ops.append({
            "tag": tag,
            "i1": i1, "i2": i2,
            "j1": j1, "j2": j2,
            "text": new[j1:j2] if tag in ("replace", "insert") else ""
        })
    return ops

def apply_diff(content, diff_ops):
    new_content = []
    for op in diff_ops:
        tag = op["tag"]
        i1, i2, text = op["i1"], op["i2"], op.get("text", "")
        if tag == "equal":
            new_content.append(content[i1:i2])
        elif tag in ("replace", "insert"):
            new_content.append(text)
        elif tag == "delete":
            pass
    return "".join(new_content)

# ---------------- CURSOR LABEL HELPERS ---------------- #
def update_cursor(user, position):
    """Place a floating colored label at given position for user"""
    if user == username:
        return  # Don't show your own cursor

    color = get_user_color(user)
    # Remove old widgets
    if user in cursor_widgets:
        rect, lbl = cursor_widgets[user]
        text_widget.delete(rect)
        lbl.destroy()

    # Compute bbox of position
    try:
        bbox = text_widget.bbox(f"1.0+{position}c")
        if not bbox:
            return
        x, y, width, height = bbox
        # Create colored rectangle for cursor
        rect = text_widget.create_rectangle(x, y, x+2, y+height, fill=color, width=0)
        # Create floating label
        lbl = tk.Label(text_widget, text=user, bg=color, fg="white", font=("Segoe UI", 8, "bold"))
        text_widget.window_create(f"1.0+{position}c", window=lbl)
        cursor_widgets[user] = (rect, lbl)
    except Exception:
        pass

# ---------------- WEBSOCKET CLIENT ---------------- #
async def connect_to_server():
    global ignore_event, last_content
    async with websockets.connect(SERVER_URI) as ws:
        await ws.send(username)

        async def send_diff(ops):
            await ws.send(json.dumps({"type": "diff", "ops": ops}))

        async def send_cursor(pos):
            await ws.send(json.dumps({"type": "cursor", "position": pos}))

        async def receive_messages():
            global ignore_event, last_content
            async for message in ws:
                data = json.loads(message)
                if data["type"] == "full_update":
                    ignore_event = True
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", data["content"])
                    last_content = data["content"]
                    ignore_event = False
                elif data["type"] == "diff":
                    ignore_event = True
                    last_content = apply_diff(last_content, data["ops"])
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", last_content)
                    ignore_event = False
                elif data["type"] == "cursor":
                    user = data["user"]
                    position = data["position"]
                    update_cursor(user, position)

        # Thread to send cursor updates
        def track_cursor():
            while True:
                try:
                    pos_index = text_widget.index("insert")
                    row, col = map(int, pos_index.split("."))
                    position = int(text_widget.count("1.0", f"{row}.{col}", "chars")[0])
                    asyncio.run_coroutine_threadsafe(send_cursor(position), loop)
                    time.sleep(0.2)
                except Exception:
                    break

        threading.Thread(target=track_cursor, daemon=True).start()

        # Bind text edits
        def on_edit(event=None):
            global last_content
            if ignore_event:
                return
            new_content = text_widget.get("1.0", "end-1c")
            ops = generate_diff(last_content, new_content)
            last_content = new_content
            asyncio.run_coroutine_threadsafe(send_diff(ops), loop)

        text_widget.bind("<<Modified>>", lambda e: on_edit())
        await receive_messages()

# ---------------- START ASYNCIO LOOP ---------------- #
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
threading.Thread(target=lambda: loop.run_until_complete(connect_to_server()), daemon=True).start()

app.mainloop()
