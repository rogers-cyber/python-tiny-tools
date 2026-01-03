import os
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import json

# ---------------- CONFIG ---------------- #
CONFIG_FILE = "resizer_config.json"

def load_last_folder():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_folder", "")
        except:
            return ""
    return ""

def save_last_folder(folder):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"last_folder": folder}, f)
    except:
        pass

# ---------------- GLOBALS ---------------- #
image_list = []
pending_images = []
stop_flag = False
current_percent = 100  # Live adjustable percentage

# ---------------- FUNCTIONS ---------------- #
def select_folder():
    folder = filedialog.askdirectory(title="Select source folder")
    if folder:
        folder_var.set(folder)
        save_last_folder(folder)
        load_images(folder)

def load_images(folder):
    global image_list
    image_list.clear()
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"):
        image_list.extend(Path(folder).glob(ext))
    count_var.set(f"{len(image_list)} images loaded")

def on_percent_change(val):
    """Update the live percentage from the slider"""
    global current_percent
    try:
        current_percent = int(float(val))  # <-- convert float string to int safely
    except ValueError:
        current_percent = 100  # fallback default

def process_image(img_path, output_folder, overwrite):
    """Process a single image using live current_percent"""
    save_path = os.path.join(output_folder, img_path.name)
    if os.path.exists(save_path) and not overwrite:
        return "skipped"
    try:
        img = Image.open(img_path)
        w = max(1, img.width * current_percent // 100)
        h = max(1, img.height * current_percent // 100)
        resized = img.resize((w, h), Image.Resampling.LANCZOS)
        resized.save(save_path)
        return "processed"
    except Exception as e:
        return f"error: {img_path.name}"

def resize_images_advanced(overwrite=False):
    """Multi-threaded resizing with cancel/resume and live percentage adjustment"""
    global pending_images, stop_flag
    if not image_list:
        messagebox.showwarning("Warning", "No images loaded.")
        return

    source_folder = folder_var.get()
    output_folder = os.path.join(source_folder, "Resized")
    os.makedirs(output_folder, exist_ok=True)

    if not pending_images:
        pending_images = list(image_list)

    processed_count = 0
    skipped_count = 0
    error_list = []

    total_images = len(pending_images)
    progress_var.set(0)
    app.update_idletasks()

    max_workers = min(8, os.cpu_count() or 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for img_path in pending_images:
            if stop_flag:
                break
            future = executor.submit(process_image, img_path, output_folder, overwrite)
            futures[future] = img_path

        for i, (future, img_path) in enumerate(futures.items(), 1):
            if stop_flag:
                break
            result = future.result()
            if result == "processed":
                processed_count += 1
            elif result == "skipped":
                skipped_count += 1
            else:
                error_list.append(result)
            progress_var.set(i / total_images * 100)
            status_var.set(f"Processing: {i}/{total_images} ({current_percent}%)")
            app.update_idletasks()

        # Remove processed images from pending list
        pending_images = pending_images[i:] if not stop_flag else pending_images[i-1:]

    if not stop_flag:
        status_var.set("Done")
        message = f"Processed {processed_count} images.\nSkipped {skipped_count} images."
        if error_list:
            message += f"\nErrors: {len(error_list)} (see console)"
            print("Errors during processing:")
            for err in error_list:
                print(err)
        message += f"\nSaved in:\n{output_folder}"
        messagebox.showinfo("Batch Resize Complete", message)
        pending_images = []
        progress_var.set(0)
    else:
        status_var.set("Paused/Cancelled")
        messagebox.showinfo("Paused", f"Batch paused. {len(pending_images)} images remaining.")

def start_advanced_resize():
    global stop_flag
    stop_flag = False
    threading.Thread(target=resize_images_advanced, args=(bool(overwrite_var.get()),), daemon=True).start()

def cancel_resize():
    global stop_flag
    stop_flag = True

def resume_resize():
    global stop_flag
    if pending_images:
        stop_flag = False
        threading.Thread(target=resize_images_advanced, args=(bool(overwrite_var.get()),), daemon=True).start()
    else:
        messagebox.showinfo("Info", "No pending images to resume.")

# ---------------- GUI ---------------- #
app = tb.Window(themename="darkly", title="Professional Live Batch Resizer", size=(600, 450))

folder_var = tk.StringVar(value=load_last_folder())
count_var = tk.StringVar(value="0 images loaded")
percent_var = tk.IntVar(value=current_percent)
overwrite_var = tk.IntVar(value=0)
progress_var = tk.DoubleVar(value=0)
status_var = tk.StringVar(value="Idle")

# Folder selection
tb.Label(app, text="Source Folder:").pack(pady=5)
folder_frame = tb.Frame(app)
folder_frame.pack(fill=tk.X, padx=10)
tb.Entry(folder_frame, textvariable=folder_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
tb.Button(folder_frame, text="Browse", bootstyle="primary", command=select_folder).pack(side=tk.LEFT)
tb.Button(folder_frame, text="Load Images", bootstyle="secondary", command=lambda: load_images(folder_var.get())).pack(side=tk.LEFT, padx=5)

# Image count
tb.Label(app, textvariable=count_var, font=("Segoe UI", 10, "bold")).pack(pady=5)

# Resize percentage (live)
tb.Label(app, text="Resize Percentage (30% - 300%)").pack(pady=5)
tb.Scale(app, from_=30, to=300, orient=tk.HORIZONTAL, variable=percent_var, command=on_percent_change).pack(fill=tk.X, padx=20)

# Overwrite checkbox
tb.Checkbutton(app, text="Overwrite existing resized images", variable=overwrite_var, bootstyle="info").pack(pady=5)

# Progress bar and status
tb.Label(app, text="Progress:").pack(pady=5)
tb.Progressbar(app, variable=progress_var, maximum=100).pack(fill=tk.X, padx=20, pady=5)
tb.Label(app, textvariable=status_var).pack(pady=5)

# Buttons
button_frame = tb.Frame(app)
button_frame.pack(pady=10, fill=tk.X, padx=20)
tb.Button(button_frame, text="🚀 Start", bootstyle="success", command=start_advanced_resize).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
tb.Button(button_frame, text="⏸ Cancel", bootstyle="warning", command=cancel_resize).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
tb.Button(button_frame, text="▶ Resume", bootstyle="info", command=resume_resize).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

app.mainloop()
