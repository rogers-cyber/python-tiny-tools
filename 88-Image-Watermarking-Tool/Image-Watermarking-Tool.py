import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

# Optional: Drag-and-drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("tkinterdnd2 not installed. Drag-and-drop disabled (install via pip install tkinterdnd2)")

# ================= HELPERS =================
def show_error(title, msg):
    messagebox.showerror(title, msg)

def show_info(title, msg):
    messagebox.showinfo(title, msg)

def add_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(foreground="grey")
    def clear(_):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.config(foreground="black")
    def restore(_):
        if not entry.get():
            entry.insert(0, text)
            entry.config(foreground="grey")
    entry.bind("<FocusIn>", clear)
    entry.bind("<FocusOut>", restore)

# ================= ROOT WINDOW =================
if DND_AVAILABLE:
    app = TkinterDnD.Tk()
    app.title("Per-Thumbnail Watermark Tool")
    app.geometry("1200x600")
else:
    app = tb.Window("Per-Thumbnail Watermark Tool", themename="flatly", size=(1200, 600))

# ================= DATA =================
image_data = []  # List of dicts: {"path":..., "position":..., "thumbnail":..., "preview":..., "selected":...}

# ================= SPLIT PANEL =================
left_panel = tb.Labelframe(app, text="Image Preview (Drag & Drop / Browse)", padding=10)
left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

right_panel = tb.Labelframe(app, text="Global Watermark Settings", padding=10)
right_panel.pack(side="right", fill="y", padx=10, pady=10)

# ================= SCROLLABLE GALLERY =================
canvas = tk.Canvas(left_panel)
scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ================= IMAGE MANAGEMENT =================
def add_images(paths):
    for path in paths:
        if os.path.isfile(path) and path not in [d["path"] for d in image_data]:
            ext = os.path.splitext(path)[1].lower()
            if ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
                image_data.append({
                    "path": path,
                    "position": "Bottom-Right",
                    "thumbnail": None,
                    "preview": None,
                    "selected": False
                })
    update_gallery()

def browse_images():
    paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    add_images(paths)

# ================= DRAG & DROP =================
def drop_files(event):
    if DND_AVAILABLE:
        # Handle Windows-style paths with braces and spaces
        data = event.data
        if data.startswith("{") and data.endswith("}"):
            files = [f.strip("{}") for f in data.split("} {")]
        else:
            files = data.split()
        add_images(files)

def remove_selected():
    global image_data
    image_data = [d for d in image_data if not d["selected"]]
    update_gallery()

# ================= GLOBAL WATERMARK SETTINGS =================
tb.Label(right_panel, text="Watermark Text").pack(anchor="w", pady=(0,2))
watermark_text = tb.Entry(right_panel, width=40)
watermark_text.pack(anchor="w", pady=(0,5))
add_placeholder(watermark_text, "Enter watermark text")

tb.Label(right_panel, text="Font Size").pack(anchor="w", pady=(5,2))
font_size = tb.Entry(right_panel, width=20)
font_size.pack(anchor="w", pady=(0,5))
add_placeholder(font_size, "36")

tb.Label(right_panel, text="Opacity (0-255)").pack(anchor="w", pady=(5,2))
opacity = tb.Entry(right_panel, width=20)
opacity.pack(anchor="w", pady=(0,5))
add_placeholder(opacity, "128")

tb.Label(right_panel, text="Output Folder").pack(anchor="w", pady=(5,2))
output_path_var = tk.StringVar()
tb.Entry(right_panel, textvariable=output_path_var, width=40).pack(anchor="w", pady=(0,5))
select_btn = tb.Button(right_panel, text="Select Folder", bootstyle="success", command=lambda: output_path_var.set(filedialog.askdirectory()))
select_btn.pack(anchor="w", pady=(0,5))

# ================= THUMBNAIL PREVIEW =================
def generate_preview(image_dict):
    try:
        img = Image.open(image_dict["path"]).convert("RGBA")
        img.thumbnail((150,150))
        preview = img.copy()
        text = watermark_text.get().strip()
        if text and text.lower() != "enter watermark text":
            try:
                size = int(font_size.get())
            except:
                size = 36
            try:
                alpha = int(opacity.get())
                if not (0 <= alpha <= 255):
                    alpha = 128
            except:
                alpha = 128
            watermark_layer = Image.new("RGBA", preview.size, (255,255,255,0))
            draw = ImageDraw.Draw(watermark_layer)
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0,0), text, font=font)
            text_width = bbox[2]-bbox[0]
            text_height = bbox[3]-bbox[1]
            pos = image_dict.get("position","Bottom-Right")
            x = y = 0
            if pos=="Top-Left": x,y=10,10
            elif pos=="Top-Right": x,y=preview.width-text_width-10,10
            elif pos=="Bottom-Left": x,y=10,preview.height-text_height-10
            elif pos=="Bottom-Right": x,y=preview.width-text_width-10,preview.height-text_height-10
            elif pos=="Center": x,y=(preview.width-text_width)//2,(preview.height-text_height)//2
            draw.text((x,y), text, fill=(255,255,255,alpha), font=font)
            preview = Image.alpha_composite(preview, watermark_layer)
        image_dict["preview"] = ImageTk.PhotoImage(preview)
    except Exception as e:
        print(f"Preview error: {e}")

# ================= GALLERY UPDATE (grid version) =================
def update_gallery():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    columns = 5
    for idx, d in enumerate(image_data):
        generate_preview(d)
        lbl_frame = tk.Frame(scrollable_frame, bd=2, relief="groove")
        lbl_frame.grid(row=idx//columns, column=idx%columns, padx=5, pady=5)
        lbl = tk.Label(lbl_frame, image=d["preview"])
        lbl.image = d["preview"]
        lbl.pack()
        # Position combobox per thumbnail
        pos_cb = tb.Combobox(lbl_frame, values=["Top-Left","Top-Right","Bottom-Left","Bottom-Right","Center"],
                             state="readonly", width=12)
        pos_cb.set(d.get("position","Bottom-Right"))
        pos_cb.pack(pady=5)
        def cb_callback(event, img_dict=d, label=lbl):
            img_dict["position"] = pos_cb.get()
            generate_preview(img_dict)
            label.configure(image=img_dict["preview"])
            label.image = img_dict["preview"]
        pos_cb.bind("<<ComboboxSelected>>", cb_callback)
        # Selection toggle
        def toggle_select(e, img_dict=d, frame=lbl_frame):
            img_dict["selected"] = not img_dict["selected"]
            frame.config(bd=4, relief="sunken" if img_dict["selected"] else "groove")
        lbl_frame.bind("<Button-1>", toggle_select)
        lbl.bind("<Button-1>", toggle_select)

def process_image(d, text, size, alpha, out_dir):
    try:
        img = Image.open(d["path"]).convert("RGBA")
        watermark_layer = Image.new("RGBA", img.size, (255,255,255,0))
        draw = ImageDraw.Draw(watermark_layer)

        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0,0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        pos = d.get("position","Bottom-Right")
        if pos=="Top-Left": x,y=10,10
        elif pos=="Top-Right": x,y=img.width-text_width-10,10
        elif pos=="Bottom-Left": x,y=10,img.height-text_height-10
        elif pos=="Bottom-Right": x,y=img.width-text_width-10,img.height-text_height-10
        else: x,y=(img.width-text_width)//2,(img.height-text_height)//2

        draw.text((x,y), text, fill=(255,255,255,alpha), font=font)

        watermarked = Image.alpha_composite(img, watermark_layer)
        base_name = os.path.basename(d["path"])
        watermarked.convert("RGB").save(os.path.join(out_dir, base_name))

        progress_var.set(progress_var.get() + 1)
        app.update_idletasks()

    except Exception as e:
        print(f"Failed: {d['path']} -> {e}")

def reset_progress_ui():
    apply_btn.config(state="normal")
    progress_bar.pack_forget()
    progress_var.set(0)

# ================= APPLY WATERMARK =================
def apply_watermark():
    progress_bar.pack(fill="x", pady=(0, 5))
    progress_bar["maximum"] = len(image_data)
    progress_var.set(0)
    select_btn.config(state="disabled")
    browse_btn.config(state="disabled")
    remove_btn.config(state="disabled")
    apply_btn.config(state="disabled")
    app.update_idletasks()

    out_dir = output_path_var.get().strip()
    if not out_dir or not os.path.isdir(out_dir):
        show_error("Error", "Please select a valid output folder.")
        reset_progress_ui()
        return
    text = watermark_text.get().strip()
    if not text or text.lower()=="enter watermark text":
        show_error("Error", "Please enter watermark text.")
        return
    try:
        size = int(font_size.get())
    except:
        size = 36
    try:
        alpha = int(opacity.get())
        if not (0<=alpha<=255): alpha=128
    except:
        alpha=128
    count=0
    for d in image_data:
        process_image(d, text, size, alpha, out_dir)
        count += 1
    show_info("Done", f"Watermarked {count} image(s) successfully.")
    select_btn.config(state="normal")
    browse_btn.config(state="normal")
    remove_btn.config(state="normal")
    apply_btn.config(state="normal")
    progress_bar.pack_forget()
    progress_var.set(0)

# ================= BUTTONS =================
browse_btn= tb.Button(
    right_panel,
    text="Browse Images",
    bootstyle="info",
    command=browse_images
)
browse_btn.pack(pady=5, fill="x")

remove_btn = tb.Button(
    right_panel,
    text="Remove Selected",
    bootstyle="danger",
    command=remove_selected
)
remove_btn.pack(pady=5, fill="x")

apply_btn = tb.Button(
    right_panel,
    text="Apply Watermark to All",
    bootstyle="success",
    command=apply_watermark
)
apply_btn.pack(pady=(10, 5), fill="x")

# Progress bar (hidden initially)
progress_var = tk.IntVar(value=0)
progress_bar = tb.Progressbar(
    right_panel,
    variable=progress_var,
    maximum=100,
    mode="determinate"
)
progress_bar.pack(fill="x", pady=(0, 5))
progress_bar.pack_forget()  # hide until needed

# ================= DRAG & DROP =================
if DND_AVAILABLE:
    left_panel.drop_target_register(DND_FILES)
    left_panel.dnd_bind("<<Drop>>", drop_files)

update_gallery()
app.mainloop()
