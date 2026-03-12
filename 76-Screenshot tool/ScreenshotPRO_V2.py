# ==========================================================
# Screenshot PRO - Advanced Screen Capture Tool
# Professional Desktop Tool
# ==========================================================

import os
import sys
import threading
import time
import traceback
from datetime import datetime
from queue import Queue, Empty

import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from PIL import ImageGrab, Image, ImageTk

import pygetwindow as gw


# =================== APP CONFIG ===================

APP_NAME = "Screenshot PRO"
APP_VERSION = "2.0.0"


# =================== APP ===================

app = tk.Tk()
app.title(f"{APP_NAME} {APP_VERSION}")
app.geometry("1200x700")

tb.Style("darkly")


# =================== UTILITY ===================

def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)


def log_error():
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(traceback.format_exc() + "\n")


def show_about():
    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME} v{APP_VERSION}\n\n"
        "Advanced Screen Capture Tool\n\n"
        "Features:\n"
        "• Full screen capture\n"
        "• Window capture\n"
        "• Smart region selector\n"
        "• Screenshot preview panel\n"
        "• Clipboard copy\n"
        "• Auto file naming\n"
        "• Processing log\n\n"
        "Built with Python + Tkinter + ttkbootstrap\n"
    )


# =================== MENU ===================

menubar = tb.Menu(app)
help_menu = tb.Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)
app.config(menu=menubar)


# =================== FLAGS ===================

ui_queue = Queue()

output_path = tb.StringVar(value=os.getcwd())
file_prefix = tb.StringVar(value="screenshot")

last_image = None


# =================== TITLE ===================

tb.Label(
    app,
    text=APP_NAME,
    font=("Segoe UI", 24, "bold")
).pack(pady=(10, 2))

tb.Label(
    app,
    text="Professional Screen Capture Tool",
    font=("Segoe UI", 10, "italic"),
    foreground="#9ca3af"
).pack(pady=(0, 10))


# =================== FRAME: SETTINGS ===================

frame1 = tb.Labelframe(app, text="Capture Settings", padding=10)
frame1.pack(fill="x", padx=10, pady=6)

tb.Label(frame1, text="File Prefix:").pack(side="left")
tb.Entry(frame1, textvariable=file_prefix, width=20).pack(side="left", padx=6)

tb.Label(frame1, text="Output Folder:", width=13).pack(side="left", padx=(20,0))
tb.Entry(frame1, textvariable=output_path, width=40).pack(side="left", padx=6)


def browse_output():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)

tb.Button(frame1, text="Browse", command=browse_output).pack(side="left", padx=4)


# =================== AUTO FILE NAME ===================

def generate_filename():

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{file_prefix.get()}_{ts}.png"


# =================== SAVE IMAGE ===================

def save_image(img):

    global last_image

    try:

        filename = generate_filename()

        path = os.path.join(output_path.get(), filename)

        img.save(path)

        last_image = img

        ui_queue.put(("preview", img))

        ui_queue.put(("log", f"✔ Saved: {filename}"))

    except:
        log_error()
        ui_queue.put(("log", "❌ Save failed"))


# =================== FULLSCREEN CAPTURE ===================

def capture_fullscreen():

    try:

        img = ImageGrab.grab()

        save_image(img)

    except:
        log_error()

    ui_queue.put(("progress", 100))


# =================== WINDOW CAPTURE ===================

def capture_window():

    try:

        win = gw.getActiveWindow()

        if not win:
            ui_queue.put(("log","❌ No active window"))
            return

        bbox = (win.left, win.top, win.right, win.bottom)

        img = ImageGrab.grab(bbox)

        save_image(img)

    except:
        log_error()

    ui_queue.put(("progress",100))


# =================== REGION SELECTOR ===================

def capture_region():

    selector = tk.Toplevel()
    selector.attributes("-fullscreen", True)
    selector.attributes("-alpha", 0.25)
    selector.configure(bg="black")

    canvas = tk.Canvas(selector, cursor="cross")
    canvas.pack(fill="both", expand=True)

    start_x = start_y = 0
    rect = None

    def press(e):
        nonlocal start_x, start_y, rect
        start_x = e.x
        start_y = e.y
        rect = canvas.create_rectangle(start_x,start_y,start_x,start_y,outline="red",width=2)

    def drag(e):
        canvas.coords(rect,start_x,start_y,e.x,e.y)

    def release(e):

        x1 = min(start_x,e.x)
        y1 = min(start_y,e.y)
        x2 = max(start_x,e.x)
        y2 = max(start_y,e.y)

        selector.destroy()

        try:

            img = ImageGrab.grab(bbox=(x1,y1,x2,y2))

            save_image(img)

        except:
            log_error()

        ui_queue.put(("progress",100))

    canvas.bind("<ButtonPress-1>",press)
    canvas.bind("<B1-Motion>",drag)
    canvas.bind("<ButtonRelease-1>",release)


# =================== CLIPBOARD COPY ===================

def copy_clipboard():

    global last_image

    if not last_image:
        messagebox.showerror("Error","No screenshot yet")
        return

    try:

        import win32clipboard
        from io import BytesIO

        output = BytesIO()
        last_image.convert("RGB").save(output,"BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB,data)
        win32clipboard.CloseClipboard()

        ui_queue.put(("log","📋 Copied to clipboard"))

    except:
        ui_queue.put(("log","❌ Clipboard copy failed"))


# =================== BUTTONS ===================

frame_buttons = tb.Frame(app)
frame_buttons.pack(fill="x", padx=10, pady=6)

tb.Button(frame_buttons,text="📸 Full Screen",bootstyle="success",
command=lambda: threading.Thread(target=capture_fullscreen,daemon=True).start()
).pack(side="left",padx=4)

tb.Button(frame_buttons,text="🖥 Window Capture",bootstyle="info",
command=lambda: threading.Thread(target=capture_window,daemon=True).start()
).pack(side="left",padx=4)

tb.Button(frame_buttons,text="🎯 Region Capture",bootstyle="warning",
command=capture_region
).pack(side="left",padx=4)

tb.Button(frame_buttons,text="📋 Copy Clipboard",bootstyle="secondary",
command=copy_clipboard
).pack(side="left",padx=4)


# =================== PROGRESS ===================

frame2 = tb.Labelframe(app, text="Progress", padding=8)
frame2.pack(fill="x", padx=10)

progress_var = tb.IntVar()

tb.Progressbar(frame2,variable=progress_var,maximum=100,length=400).pack(side="left", padx=10)

status_lbl = tb.Label(frame2,text="Status: Ready")
status_lbl.pack(side="left",padx=10)


# =================== MAIN LAYOUT ===================

main_frame = tb.Frame(app)
main_frame.pack(fill="both",expand=True,padx=10,pady=6)

# preview panel
preview_frame = tb.Labelframe(main_frame,text="Preview",padding=8)
preview_frame.pack(side="left",fill="both",expand=True,padx=6)

preview_label = tk.Label(preview_frame)
preview_label.pack(expand=True)

# log panel
log_frame = tb.Labelframe(main_frame,text="Processing Log",padding=8)
log_frame.pack(side="right",fill="both",expand=True,padx=6)

log_text = tk.Text(log_frame,height=10)
log_text.pack(side="left",fill="both",expand=True)

scroll = tk.Scrollbar(log_frame,command=log_text.yview)
scroll.pack(side="right",fill="y")

log_text.config(yscrollcommand=scroll.set,state="disabled")


# =================== UI QUEUE ===================

def process_ui_queue():

    try:

        while True:

            cmd,data = ui_queue.get_nowait()

            if cmd=="progress":
                progress_var.set(data)

            elif cmd=="log":

                log_text.config(state="normal")
                log_text.insert("end",data+"\n")
                log_text.see("end")
                log_text.config(state="disabled")

            elif cmd=="preview":

                img = data.copy()
                img.thumbnail((550,400))

                tk_img = ImageTk.PhotoImage(img)

                preview_label.config(image=tk_img)
                preview_label.image = tk_img

    except Empty:
        pass

    app.after(100,process_ui_queue)


# =================== START UI ===================

app.after(100,process_ui_queue)

app.mainloop()
