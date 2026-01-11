import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from PIL import Image, ImageTk
import subprocess
import os
import threading
import time
import re

# ================= APP =================
app = tb.Window(
    title="Relax Video Builder – Images + MP3 to MP4",
    themename="superhero",
    size=(950, 650),
    resizable=(False, False)
)

# ================= VARIABLES =================
image_files = []
mp3_path = tk.StringVar()
output_path = tk.StringVar()
hours_var = tk.IntVar(value=10)

process = None
rendering = False
total_seconds = 0

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # CHANGE THIS

# ================= FUNCTIONS =================
def select_images():
    files = filedialog.askopenfilenames(
        filetypes=[("Images", "*.jpg *.png")]
    )
    if files:
        image_files.extend(files)
        refresh_images()

def refresh_images():
    image_listbox.delete(0, tk.END)
    for img in image_files:
        image_listbox.insert(tk.END, os.path.basename(img))
    image_count_label.config(text=f"{len(image_files)} image(s) selected")

def remove_selected_images():
    sel = image_listbox.curselection()
    for i in reversed(sel):
        del image_files[i]
    refresh_images()

def remove_all_images():
    image_files.clear()
    refresh_images()
    preview_label.config(image="")

def on_image_select(event):
    sel = image_listbox.curselection()
    if not sel:
        return
    img = Image.open(image_files[sel[0]])
    img.thumbnail((350, 250))
    tk_img = ImageTk.PhotoImage(img)
    preview_label.config(image=tk_img)
    preview_label.image = tk_img

def select_mp3():
    mp3 = filedialog.askopenfilename(filetypes=[("MP3", "*.mp3")])
    if mp3:
        mp3_path.set(mp3)

def remove_mp3():
    mp3_path.set("")

def select_output():
    out = filedialog.asksaveasfilename(
        defaultextension=".mp4",
        filetypes=[("MP4", "*.mp4")]
    )
    if out:
        output_path.set(out)

def build_video():
    if rendering:
        return
    if not image_files or not mp3_path.get() or not output_path.get():
        messagebox.showerror("Error", "Missing images, MP3, or output file.")
        return

    threading.Thread(target=run_ffmpeg, daemon=True).start()

def stop_video():
    global process, rendering
    if process:
        process.terminate()
        process = None
        rendering = False
        status_label.config(text="Rendering stopped.")
        resume_btn.config(state="normal")

def run_ffmpeg():
    global process, rendering, total_seconds
    rendering = True
    resume_btn.config(state="disabled")
    progress_bar['value'] = 0

    total_seconds = hours_var.get() * 3600
    seconds_per_image = total_seconds / len(image_files)

    list_file = "images.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for img in image_files:
            f.write(f"file '{img}'\n")
            f.write(f"duration {seconds_per_image}\n")
        f.write(f"file '{image_files[-1]}'\n")

    cmd = [
        FFMPEG_PATH, "-y",
        "-stream_loop", "-1",
        "-i", mp3_path.get(),
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-t", str(total_seconds),
        "-vf", "scale=1920:1080",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path.get()
    ]

    process = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+)")

    for line in process.stderr:
        match = time_pattern.search(line)
        if match:
            h, m, s = map(int, match.groups())
            current = h * 3600 + m * 60 + s
            percent = (current / total_seconds) * 100
            progress_bar['value'] = percent
            status_label.config(
                text=f"Rendering... {int(percent)}%"
            )

    process.wait()
    rendering = False
    os.remove(list_file)

    if process.returncode == 0:
        status_label.config(text="Rendering complete!")
        messagebox.showinfo("Done", "Relax video created successfully.")
    else:
        status_label.config(text="Rendering stopped.")

# ================= UI =================
main = tb.Frame(app, padding=15)
main.pack(fill="both", expand=True)

tb.Label(main, text="Relax Video Builder", font=("Segoe UI", 18, "bold")).pack()

content = tb.Frame(main)
content.pack(fill="both", expand=True, pady=10)

# LEFT
left = tb.Labelframe(content, text="Images", padding=10)
left.pack(side="left", fill="y")

tb.Button(left, text="Add Images", command=select_images).pack(fill="x")
image_listbox = tk.Listbox(left, height=15)
image_listbox.pack(pady=5)
image_listbox.bind("<<ListboxSelect>>", on_image_select)
image_count_label = tb.Label(left, text="0 image(s)")
image_count_label.pack()
tb.Button(left, text="Remove Selected", command=remove_selected_images).pack(fill="x")
tb.Button(left, text="Remove All", command=remove_all_images).pack(fill="x")

# CENTER
center = tb.Labelframe(content, text="Preview", padding=10)
center.pack(side="left", fill="both", expand=True)
preview_label = tb.Label(center)
preview_label.pack(expand=True)

# RIGHT
right = tb.Labelframe(content, text="Audio & Settings", padding=10)
right.pack(side="right", fill="y")

tb.Button(right, text="Select MP3", command=select_mp3).pack(fill="x")
tb.Entry(right, textvariable=mp3_path, width=30).pack()
tb.Button(right, text="Remove MP3", command=remove_mp3).pack(fill="x", pady=5)

tb.Label(right, text="Duration (Hours)").pack()
tb.Spinbox(right, from_=1, to=10, textvariable=hours_var, width=8).pack()

tb.Button(right, text="Output MP4", command=select_output).pack(fill="x", pady=10)
tb.Entry(right, textvariable=output_path, width=30).pack()

tb.Button(right, text="▶ Start", bootstyle="success", command=build_video).pack(fill="x", pady=5)
tb.Button(right, text="⛔ Stop", bootstyle="danger", command=stop_video).pack(fill="x", pady=5)
resume_btn = tb.Button(right, text="🔁 Resume (Restart)", bootstyle="warning", command=build_video)
resume_btn.pack(fill="x")

# BOTTOM
progress_bar = tb.Progressbar(main, length=600)
progress_bar.pack(pady=10)

status_label = tb.Label(main, text="Idle")
status_label.pack()

app.mainloop()
