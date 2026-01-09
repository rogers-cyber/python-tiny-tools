import tkinter as tk
import ttkbootstrap as tb
import numpy as np
import threading
import time
import mss
import cv2
from PIL import Image, ImageTk

# ================= CONFIG =================
APP_TITLE = "Scopes – Screen Capture"
FPS = 30

# ================= GLOBAL STATE =================
running = False
latest_frame = None
roi = None
recording = False
video_writer = None
color_indicators = []

# ================= APP =================
app = tb.Window(title=APP_TITLE, themename="darkly", size=(1280, 720))
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# ================= UI =================
controls = tb.Frame(app, padding=10)
controls.grid(row=0, column=0, sticky="ns")

viewer = tb.Frame(app)
viewer.grid(row=0, column=1, sticky="nsew")
viewer.grid_columnconfigure(0, weight=1)
viewer.grid_rowconfigure(0, weight=1)

canvas = tk.Canvas(viewer, bg="black", highlightthickness=0)
canvas.grid(row=0, column=0, sticky="nsew")

# ================= CONTROLS =================
tb.Label(controls, text="Capture", font=("Segoe UI", 11, "bold")).pack(anchor="w")

def toggle_capture():
    global running
    running = not running
    btn_start.config(text="Stop" if running else "Start")

btn_start = tb.Button(controls, text="Start", bootstyle="success", command=toggle_capture)
btn_start.pack(fill="x", pady=4)

def toggle_record():
    global recording, video_writer
    recording = not recording
    btn_rec.config(text="Stop REC" if recording else "Record")

    if not recording and video_writer:
        video_writer.release()
        video_writer = None

btn_rec = tb.Button(controls, text="Record", bootstyle="danger", command=toggle_record)
btn_rec.pack(fill="x", pady=4)

tb.Label(controls, text="Sampling Step").pack(anchor="w", pady=(10, 0))
sample_slider = tb.Scale(controls, from_=1, to=10, orient="horizontal")
sample_slider.set(4)
sample_slider.pack(fill="x")

tb.Label(controls, text="Gain").pack(anchor="w", pady=(10, 0))
gain_slider = tb.Scale(controls, from_=1, to=10, orient="horizontal")
gain_slider.set(4)
gain_slider.pack(fill="x")

tb.Separator(controls).pack(fill="x", pady=10)

tb.Label(
    controls,
    text="Mouse drag = ROI\nSPACE = sample color\nESC = quit",
    justify="left"
).pack(anchor="w")

# ================= COLOR =================
def rgb_to_yuv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.299*r + 0.587*g + 0.114*b
    u = -0.147*r - 0.289*g + 0.436*b
    v = 0.615*r - 0.515*g - 0.100*b
    return y, u, v

# ================= DRAW =================
def draw_scopes(frame):
    canvas.delete("all")

    h, w, _ = frame.shape
    ch, cw = canvas.winfo_height(), canvas.winfo_width()
    if ch < 50 or cw < 50:
        return

    step = int(sample_slider.get())
    gain = gain_slider.get()

    small = frame[::step, ::step] / 255.0
    Y, U, V = rgb_to_yuv(small)

    # ---- VECTORSCOPE ----
    cx, cy, radius = 200, ch//2, 160
    canvas.create_text(cx, 20, text="VECTORSCOPE", fill="#aaa")
    canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, outline="#444")

    xs = cx + U.flatten() * radius * gain
    ys = cy - V.flatten() * radius * gain

    for x, y in zip(xs, ys):
        canvas.create_line(x, y, x+1, y, fill="lime")

    for r, g, b in color_indicators:
        _, u, v = rgb_to_yuv(np.array([[r, g, b]]))
        ix = cx + u[0] * radius * gain
        iy = cy - v[0] * radius * gain
        canvas.create_oval(ix-6, iy-6, ix+6, iy+6, outline="yellow", width=2)

    # ---- HISTOGRAM ----
    hist_x = 420
    hist_w = cw - hist_x - 20
    hist_h = 150
    hist_y = 60

    canvas.create_text(hist_x, 20, text="HISTOGRAM", fill="#aaa", anchor="w")

    for i, col in enumerate(("red", "green", "blue")):
        hist, _ = np.histogram(frame[..., i], bins=256, range=(0, 255))
        hist = hist / hist.max() if hist.max() > 0 else hist
        for x in range(256):
            y0 = hist_y + hist_h
            y1 = hist_y + hist_h - hist[x] * hist_h
            canvas.create_line(
                hist_x + x * hist_w / 256, y0,
                hist_x + x * hist_w / 256, y1,
                fill=col
            )

    # ---- LUMA ----
    canvas.create_text(hist_x, hist_y + hist_h + 30, text="LUMA", fill="#aaa", anchor="w")
    hist, _ = np.histogram((Y * 255).astype(np.uint8), bins=256, range=(0, 255))
    hist = hist / hist.max() if hist.max() > 0 else hist

    for x in range(256):
        y0 = hist_y + hist_h + 180
        y1 = y0 - hist[x] * hist_h
        canvas.create_line(
            hist_x + x * hist_w / 256, y0,
            hist_x + x * hist_w / 256, y1,
            fill="white"
        )

# ================= CAPTURE THREAD =================
def capture_thread():
    global latest_frame, video_writer
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            if running:
                img = np.array(sct.grab(monitor))[:, :, :3]

                # Apply ROI safely
                if roi:
                    x1, y1, x2, y2 = roi
                    # Convert to relative coordinates
                    x1_rel = max(0, min(x1 - monitor["left"], img.shape[1]-1))
                    y1_rel = max(0, min(y1 - monitor["top"], img.shape[0]-1))
                    x2_rel = max(0, min(x2 - monitor["left"], img.shape[1]))
                    y2_rel = max(0, min(y2 - monitor["top"], img.shape[0]))

                    if x2_rel > x1_rel and y2_rel > y1_rel:
                        img = img[y1_rel:y2_rel, x1_rel:x2_rel]
                    else:
                        img = None  # Invalid ROI

                if img is not None:
                    latest_frame = img

                    if recording:
                        h, w = img.shape[:2]
                        if h > 0 and w > 0:  # Make sure dimensions are valid
                            if video_writer is None:
                                video_writer = cv2.VideoWriter(
                                    "recording.mp4",
                                    cv2.VideoWriter_fourcc(*"mp4v"),
                                    FPS,
                                    (w, h)
                                )
                            if video_writer.isOpened():
                                video_writer.write(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

            time.sleep(1 / FPS)

threading.Thread(target=capture_thread, daemon=True).start()

# ================= UI LOOP =================
def update_ui():
    if running and latest_frame is not None:
        draw_scopes(latest_frame)
    app.after(33, update_ui)

update_ui()

# ================= ROI =================
start_pt = None

def on_mouse_down(e):
    global start_pt
    start_pt = (e.x_root, e.y_root)

def on_mouse_up(e):
    global roi, start_pt
    if not start_pt:
        return
    x1, y1 = start_pt
    x2, y2 = e.x_root, e.y_root
    roi = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
    start_pt = None

canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# ================= INPUT =================
def on_key(e):
    global roi
    if e.keysym == "Escape":
        app.destroy()
    if e.keysym == "space":
        x, y = app.winfo_pointerxy()
        with mss.mss() as sct:
            img = sct.grab(sct.monitors[1])
            r, g, b = img.pixel(x, y)
            color_indicators.append((r/255, g/255, b/255))
    if e.keysym == "r":
        roi = None

app.bind("<Key>", on_key)

# ================= RUN =================
app.mainloop()
