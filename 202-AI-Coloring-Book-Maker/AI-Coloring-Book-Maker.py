import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledFrame
import threading
import os
import sys
from PIL import Image, ImageDraw, ImageTk
import random

# Optional for PDF export
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Optional for Stable Diffusion API
import requests
import base64
from io import BytesIO

# =================== APP INFO ===================
APP_NAME = "AI Coloring Book Maker"
VERSION = "1.0"

# =================== UTIL ===================
def resource_path(file_name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def show_error(title, msg):
    messagebox.showerror(title, msg)

def show_info(title, msg):
    messagebox.showinfo(title, msg)

# =================== APP ===================
app = tb.Window(f"{APP_NAME} v{VERSION}", themename="superhero", size=(1300, 720))
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=2)
app.grid_rowconfigure(1, weight=1)

try:
    app.iconbitmap(resource_path("icon.ico"))
except Exception:
    pass

generated_images = []
selected_images = set()
thumbnail_labels = []

# ================= LEFT PANEL =================
left_panel = tb.Labelframe(app, text="AI Prompt Settings", padding=15)
left_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

tb.Label(left_panel, text="Prompt / Theme").pack(anchor="w")
prompt_entry = tb.Entry(left_panel)
prompt_entry.pack(fill="x", pady=5)

tb.Label(left_panel, text="Art Style").pack(anchor="w")
style_combo = tb.Combobox(
    left_panel,
    values=[
        "Cartoon Coloring Page",
        "Cute Kawaii Line Art",
        "Kids Coloring Book",
        "Mandala Line Art",
        "Simple Thick Outline"
    ],
    state="readonly"
)
style_combo.set("Cartoon Coloring Page")
style_combo.pack(fill="x", pady=5)

tb.Label(left_panel, text="Image Size").pack(anchor="w")
size_combo = tb.Combobox(
    left_panel,
    values=["256x256", "512x512", "768x768", "1024x1024"],
    state="readonly"
)
size_combo.set("512x512")
size_combo.pack(fill="x", pady=5)

tb.Label(left_panel, text="Batch Count (1–10)").pack(anchor="w")
batch_spin = tb.Spinbox(left_panel, from_=1, to=10, width=5)
batch_spin.set(4)
batch_spin.pack(anchor="w", pady=5)

generate_btn = tb.Button(
    left_panel,
    text="Generate Images",
    bootstyle="success",
    width=25
)
generate_btn.pack(pady=15)

save_btn = tb.Button(
    left_panel,
    text="Save Selected Images",
    bootstyle="primary",
    width=25
)
save_btn.pack(pady=5)

export_pdf_btn = tb.Button(
    left_panel,
    text="Export Coloring Book (PDF)",
    bootstyle="warning",
    width=25
)
export_pdf_btn.pack(pady=5)

# ================= RIGHT PANEL =================
preview_panel = tb.Labelframe(app, text="Thumbnail Preview", padding=10)
preview_panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
preview_panel.grid_rowconfigure(0, weight=1)
preview_panel.grid_columnconfigure(0, weight=1)

scroll = ScrolledFrame(preview_panel, autohide=True)
scroll.pack(fill="both", expand=True)

# ================= AI PLACEHOLDER =================
def fake_ai_generate(size):
    img = Image.new("RGB", size, "white")
    d = ImageDraw.Draw(img)
    for _ in range(15):
        x1 = random.randint(0, size[0])
        y1 = random.randint(0, size[1])
        x2 = random.randint(0, size[0])
        y2 = random.randint(0, size[1])
        d.line((x1, y1, x2, y2), fill="black", width=3)
    return img

# Optional: Stable Diffusion generator
def stable_diffusion_generate(prompt, size):
    # Replace URL with your SD WebUI API endpoint
    try:
        payload = {
            "prompt": f"{prompt}, black and white coloring page, line art, no shading",
            "negative_prompt": "color, gray, shadows, text",
            "steps": 25,
            "width": size[0],
            "height": size[1],
            "cfg_scale": 7,
            "sampler_name": "Euler a"
        }
        r = requests.post("http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
        r.raise_for_status()
        img_data = base64.b64decode(r.json()["images"][0])
        return Image.open(BytesIO(img_data)).convert("RGB")
    except Exception as e:
        show_error("Stable Diffusion Error", str(e))
        return fake_ai_generate(size)

# ================= GENERATION =================
def get_column_count():
    width = scroll.winfo_width()
    return max(1, width // 210)

def refresh_thumbnail_grid(event=None):
    cols = get_column_count()
    for idx, lbl in enumerate(thumbnail_labels):
        lbl.grid(row=idx // cols, column=idx % cols, padx=5, pady=5)

def generate_images():
    prompt = prompt_entry.get().strip()
    if not prompt:
        show_error("Input Error", "Please enter a prompt or theme.")
        return

    for widget in scroll.winfo_children():
        widget.destroy()

    generated_images.clear()
    selected_images.clear()
    thumbnail_labels.clear()

    size = tuple(map(int, size_combo.get().split("x")))
    batch = int(batch_spin.get())

    for i in range(batch):
        # Replace fake_ai_generate with stable_diffusion_generate if SD is available
        img = fake_ai_generate(size)
        # img = stable_diffusion_generate(prompt, size)

        generated_images.append(img)

        thumb = img.copy()
        thumb.thumbnail((200, 200))
        tk_img = ImageTk.PhotoImage(thumb)

        lbl = tk.Label(scroll, image=tk_img, borderwidth=2, relief="ridge")
        lbl.image = tk_img
        thumbnail_labels.append(lbl)

        def toggle_select(event, index=i, label=lbl):
            if index in selected_images:
                selected_images.remove(index)
                label.config(relief="ridge", borderwidth=2)
            else:
                selected_images.add(index)
                label.config(relief="solid", borderwidth=4)

        lbl.bind("<Button-1>", toggle_select)

    refresh_thumbnail_grid()

scroll.bind("<Configure>", refresh_thumbnail_grid)

# ================= SAVE =================
def save_selected():
    if not selected_images:
        show_error("Save Error", "No images selected.")
        return

    folder = filedialog.askdirectory(title="Select Save Folder")
    if not folder:
        return

    for i in selected_images:
        path = os.path.join(folder, f"coloring_page_{i+1}.png")
        img_300 = generated_images[i].resize((2480, 3508), Image.LANCZOS)
        img_300.save(path, dpi=(300, 300))

    show_info("Saved", f"{len(selected_images)} images saved successfully.")

# ================= PDF EXPORT =================
def export_pdf():
    if not selected_images:
        show_error("Export Error", "No images selected.")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not path:
        return

    c = canvas.Canvas(path, pagesize=A4)
    page_width, page_height = A4

    for idx in selected_images:
        img = generated_images[idx]
        img_300 = img.resize((2480, 3508), Image.LANCZOS)
        img_reader = ImageReader(img_300)
        c.drawImage(
            img_reader,
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=True,
            anchor='c'
        )
        c.showPage()

    c.save()
    show_info("PDF Exported", "Coloring book PDF created successfully.")

generate_btn.config(command=lambda: threading.Thread(target=generate_images, daemon=True).start())
save_btn.config(command=save_selected)
export_pdf_btn.config(command=export_pdf)

# ================= ABOUT =================
def show_about():
    win = tb.Toplevel(app)
    win.title("About")
    win.geometry("500x400")
    win.resizable(False, False)
    frame = tb.Frame(win, padding=15)
    frame.pack(fill="both", expand=True)

    tb.Label(frame, text=APP_NAME, font=("Segoe UI", 14, "bold")).pack(pady=5)
    tb.Label(frame, text=f"Version {VERSION}").pack()

    tb.Label(
        frame,
        text=(
            "AI Coloring Book Maker is a standalone desktop application\n"
            "that generates printable black-and-white coloring pages\n"
            "using AI-powered image generation.\n\n"
            "Key Features:\n"
            "- Custom prompts\n"
            "- Batch image generation\n"
            "- Thumbnail selection\n"
            "- Print-ready line art\n"
            "- 300 DPI PDF export\n"
            "- Fully offline executable\n"
        ),
        justify="left",
        wraplength=460
    ).pack(pady=10)

    tb.Button(frame, text="Close", bootstyle="danger", command=win.destroy).pack(pady=10)

menu = tk.Menu(app)
app.config(menu=menu)
help_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=show_about)

app.mainloop()
