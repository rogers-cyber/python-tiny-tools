import os
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ---------------- HELPERS ---------------- #
def format_size(bytes_size):
    if not bytes_size:
        return "N/A"
    try:
        bytes_size = int(bytes_size)
    except:
        return "N/A"
    for unit in ['B','KB','MB','GB','TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} PB"

def run_command(command):
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output_lines = []
        for line in proc.stdout:
            output_lines.append(line.strip())
        proc.wait()
        return output_lines
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []

def download_with_progress(video_url, fmt_code, progress_var):
    """Download selected format and update progress bar"""
    downloads_folder = "downloads"
    os.makedirs(downloads_folder, exist_ok=True)
    output_template = os.path.join(downloads_folder, "%(title)s.%(ext)s")
    command = [
        "yt-dlp", "-f", fmt_code, "-o", output_template, "--newline", video_url
    ]
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if "%" in line:
                # Extract progress %
                try:
                    percent = float(line.split("%")[0].split()[-1])
                    progress_var.set(percent)
                except:
                    pass
        proc.wait()
        progress_var.set(100)
        messagebox.showinfo("Downloaded", f"Video saved to {downloads_folder}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def parse_formats(output_lines):
    """Return video/audio formats sorted high->low"""
    formats = []
    for line in output_lines:
        if not line or line.startswith("format code"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        fmt_code = parts[0]
        res = parts[1]
        type_ = parts[2]
        if "video" not in type_.lower() and "audio" not in type_.lower():
            continue
        size = "-"
        if len(parts) > 3 and parts[-1].endswith(("KiB","MiB","GiB")):
            size = parts[-1]
        sort_key = 0
        if "video" in type_.lower() and res != "audio":
            try: sort_key = int(res.replace("p",""))
            except: sort_key=0
        formats.append({"fmt_code": fmt_code, "res": res, "type": type_, "size": size, "sort_key": sort_key})
    formats.sort(key=lambda x: x["sort_key"], reverse=True)
    return formats

def fetch_thumbnail(video_url):
    """Fetch video thumbnail"""
    try:
        cmd = ["yt-dlp", "--get-thumbnail", video_url]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        url = result.stdout.strip()
        if not url:
            return None
        resp = requests.get(url)
        img = Image.open(io.BytesIO(resp.content))
        img.thumbnail((320, 180))
        return ImageTk.PhotoImage(img)
    except:
        return None

# ---------------- GUI FUNCTIONS ---------------- #
def fetch_formats_gui():
    video_url = url_entry.get().strip()
    if not video_url:
        messagebox.showwarning("Input Needed", "Please enter a YouTube URL.")
        return
    fetching_label.config(text="Fetching formats...")

    def worker():
        # Clear previous
        for widget in list_frame.winfo_children():
            widget.destroy()
        # Fetch thumbnail
        thumb = fetch_thumbnail(video_url)
        if thumb:
            thumb_label.config(image=thumb)
            thumb_label.image = thumb

        output_lines = run_command(["yt-dlp", "-F", video_url])
        if not output_lines:
            fetching_label.config(text="")
            messagebox.showerror("Error", "Failed to fetch formats.")
            return
        formats = parse_formats(output_lines)

        # Headers
        headers = ["Format", "Resolution", "Type", "Size", "Download"]
        for c,h in enumerate(headers):
            tb.Label(list_frame, text=h, font=("Segoe UI",10,"bold")).grid(row=0,column=c,padx=5,pady=2)
        # Add rows
        for r_idx, fmt in enumerate(formats,start=1):
            bg_color = "#2c2f33" if r_idx % 2==0 else "#23272a"
            tb.Label(list_frame, text=fmt["fmt_code"], background=bg_color).grid(row=r_idx,column=0,padx=2,sticky="w")
            tb.Label(list_frame, text=fmt["res"], background=bg_color).grid(row=r_idx,column=1,padx=2,sticky="w")
            tb.Label(list_frame, text=fmt["type"], background=bg_color).grid(row=r_idx,column=2,padx=2,sticky="w")
            tb.Label(list_frame, text=fmt["size"], background=bg_color).grid(row=r_idx,column=3,padx=2,sticky="w")
            progress_var = tk.DoubleVar()
            progress = tb.Progressbar(list_frame, variable=progress_var, bootstyle="info-striped", length=120)
            progress.grid(row=r_idx,column=4,padx=2)
            btn = tb.Button(list_frame, text="⬇ Download", bootstyle="success",
                            command=lambda f=fmt["fmt_code"], pv=progress_var: threading.Thread(target=download_with_progress,args=(video_url,f,pv),daemon=True).start())
            btn.grid(row=r_idx,column=5,padx=5)
        fetching_label.config(text="")

    threading.Thread(target=worker, daemon=True).start()

# ---------------- GUI ---------------- #
app = tb.Window(title="Professional YouTube Downloader", themename="darkly", size=(1000,650))

# URL entry
top_frame = tb.Frame(app,padding=10)
top_frame.pack(fill=tk.X)
tb.Label(top_frame,text="YouTube URL:", font=("Segoe UI",12)).pack(side=tk.LEFT)
url_entry = tb.Entry(top_frame,font=("Segoe UI",12))
url_entry.pack(side=tk.LEFT,fill=tk.X,expand=True,padx=5)
tb.Button(top_frame,text="Fetch Formats",bootstyle="primary", command=fetch_formats_gui).pack(side=tk.LEFT)

fetching_label = tb.Label(app,text="",font=("Segoe UI",10),foreground="yellow")
fetching_label.pack(pady=2)

# Thumbnail
thumb_label = tb.Label(app)
thumb_label.pack(pady=5)

# List Frame with Scroll
canvas_frame = tb.Frame(app)
canvas_frame.pack(fill=tk.BOTH,expand=True,pady=10)
canvas = tk.Canvas(canvas_frame)
scrollbar = tk.Scrollbar(canvas_frame,orient="vertical",command=canvas.yview)
scrollable_frame = tb.Frame(canvas)
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0,0),window=scrollable_frame,anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left",fill="both",expand=True)
scrollbar.pack(side="right",fill="y")
list_frame = scrollable_frame

app.mainloop()
