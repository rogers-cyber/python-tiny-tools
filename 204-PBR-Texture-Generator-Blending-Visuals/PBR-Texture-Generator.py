import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText
import threading
import cv2
import os
import sys
import numpy as np

# =================== Utility ===================
def resource_path(file_name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =================== APP ===================
app = tb.Window(
    title="PBR Texture Generator — Blending Visuals",
    themename="superhero",
    size=(1150, 650)
)

app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=2)
app.grid_rowconfigure(0, weight=1)

# =================== HELPERS ===================
def ui(func, *args):
    app.after(0, lambda: func(*args))

def log_line(text):
    def _log():
        log.text.config(state="normal")
        log.text.insert("end", text + "\n")
        log.text.see("end")
        log.text.config(state="disabled")
    ui(_log)

# =================== PANELS ===================
left_panel = tb.Frame(app)
left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
left_panel.grid_columnconfigure(0, weight=1)

right_panel = tb.Frame(app)
right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
right_panel.grid_rowconfigure(0, weight=1)

# =================== INPUT ===================
input_card = tb.Labelframe(left_panel, text="Base Image", padding=15)
input_card.grid(row=0, column=0, sticky="ew", pady=5)

image_path = tk.StringVar()
output_dir = tk.StringVar()

tb.Entry(input_card, textvariable=image_path).grid(row=0, column=0, sticky="ew", padx=5)
tb.Button(
    input_card, text="Browse", bootstyle="info",
    command=lambda: image_path.set(
        filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    )
).grid(row=0, column=1, padx=5)

input_card.grid_columnconfigure(0, weight=1)

# =================== OUTPUT ===================
out_card = tb.Labelframe(left_panel, text="Output Folder", padding=15)
out_card.grid(row=1, column=0, sticky="ew", pady=5)

tb.Entry(out_card, textvariable=output_dir).grid(row=0, column=0, sticky="ew", padx=5)
tb.Button(
    out_card, text="Browse", bootstyle="info",
    command=lambda: output_dir.set(filedialog.askdirectory())
).grid(row=0, column=1, padx=5)

out_card.grid_columnconfigure(0, weight=1)

# =================== MAP OPTIONS ===================
map_card = tb.Labelframe(left_panel, text="Maps to Generate", padding=15)
map_card.grid(row=2, column=0, sticky="ew", pady=5)

gen_normal = tk.BooleanVar(value=True)
gen_rough = tk.BooleanVar(value=True)
gen_height = tk.BooleanVar(value=True)
gen_ao = tk.BooleanVar(value=True)
gen_metal = tk.BooleanVar(value=True)

for text, var in [
    ("Normal Map", gen_normal),
    ("Roughness Map", gen_rough),
    ("Height Map", gen_height),
    ("Ambient Occlusion", gen_ao),
    ("Metallic Map", gen_metal),
]:
    tb.Checkbutton(map_card, text=text, variable=var, bootstyle="success").pack(anchor="w")

# =================== LOG ===================
log_card = tb.Labelframe(right_panel, text="Live Output", padding=15)
log_card.grid(row=0, column=0, sticky="nsew")
log_card.grid_rowconfigure(0, weight=1)

log = ScrolledText(log_card)
log.grid(row=0, column=0, sticky="nsew")
log.text.config(state="disabled")

# =================== PROGRESS ===================
bottom = tb.Frame(app)
bottom.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

progress = tb.Progressbar(bottom)
progress.grid(row=0, column=0, sticky="ew")
bottom.grid_columnconfigure(0, weight=1)

# =================== PBR GENERATION ===================
def generate_pbr():
    if not image_path.get() or not output_dir.get():
        messagebox.showerror("Missing Input", "Select image and output folder.")
        return

    img = cv2.imread(image_path.get())
    base = os.path.splitext(os.path.basename(image_path.get()))[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    os.makedirs(output_dir.get(), exist_ok=True)
    progress.configure(value=0)

    steps = sum([
        gen_normal.get(), gen_rough.get(),
        gen_height.get(), gen_ao.get(),
        gen_metal.get()
    ])
    done = 0

    # ===== HEIGHT =====
    if gen_height.get():
        height = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(f"{output_dir.get()}/{base}_height.png", height)
        log_line("Height map generated")
        done += 1

    # ===== NORMAL =====
    if gen_normal.get():
        sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
        sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
        normal = np.dstack((-sobelx, -sobely, np.ones_like(gray)))
        normal /= np.linalg.norm(normal, axis=2, keepdims=True)
        normal = ((normal + 1) * 127.5).astype(np.uint8)
        cv2.imwrite(f"{output_dir.get()}/{base}_normal.png", normal)
        log_line("Normal map generated")
        done += 1

    # ===== AO =====
    if gen_ao.get():
        ao = cv2.GaussianBlur(255 - gray, (15, 15), 0)
        cv2.imwrite(f"{output_dir.get()}/{base}_ao.png", ao)
        log_line("Ambient Occlusion map generated")
        done += 1

    # ===== ROUGHNESS =====
    if gen_rough.get():
        edges = cv2.Canny(gray, 50, 150)
        rough = cv2.GaussianBlur(255 - edges, (7, 7), 0)
        cv2.imwrite(f"{output_dir.get()}/{base}_roughness.png", rough)
        log_line("Roughness map generated")
        done += 1

    # ===== METALLIC =====
    if gen_metal.get():
        _, metal = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        cv2.imwrite(f"{output_dir.get()}/{base}_metallic.png", metal)
        log_line("Metallic map generated")
        done += 1

    progress.configure(value=100)
    messagebox.showinfo("Done", "PBR textures generated successfully.")

# =================== BUTTONS ===================
tb.Button(
    bottom,
    text="Generate PBR Maps",
    bootstyle="success",
    width=25,
    command=lambda: threading.Thread(target=generate_pbr, daemon=True).start()
).grid(row=1, column=0, pady=5)

app.mainloop()
