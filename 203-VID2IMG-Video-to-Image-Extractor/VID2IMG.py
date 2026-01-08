import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText
import threading
import os
import cv2  # OpenCV for video processing
import time

# =================== Utility Functions ===================
def resource_path(file_name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# ================= HELPERS =================
def show_error(title, msg):
    messagebox.showerror(title, msg)

def show_info(title, msg):
    messagebox.showinfo(title, msg)

# ================= APP =================
app = tb.Window("VID2IMG - Video to Image Extractor", themename="superhero", size=(1000, 600))
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(1, weight=1)

# ================= TOP LEFT: VIDEO INPUT =================
video_card = tb.Labelframe(app, text="Video Input", padding=15)
video_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

video_path_var = tk.StringVar()
tb.Label(video_card, text="Select Video File").pack(anchor="w")
video_entry = tb.Entry(video_card, textvariable=video_path_var, width=50)
video_entry.pack(side="left", pady=5, padx=(0,5))
tb.Button(video_card, text="Browse", bootstyle="info", command=lambda: select_video()).pack(side="left")

def select_video():
    path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    if path:
        video_path_var.set(path)

# ================= TOP RIGHT: OUTPUT SETTINGS =================
output_card = tb.Labelframe(app, text="Output Settings", padding=15)
output_card.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

tb.Label(output_card, text="Output Folder").grid(row=0, column=0, sticky="w")
output_folder_var = tk.StringVar()
output_entry = tb.Entry(output_card, textvariable=output_folder_var, width=40)
output_entry.grid(row=0, column=1, sticky="w", padx=5)
tb.Button(output_card, text="Browse", bootstyle="info", command=lambda: select_output()).grid(row=0, column=2, sticky="w")

def select_output():
    path = filedialog.askdirectory()
    if path:
        output_folder_var.set(path)

tb.Label(output_card, text="Image Format").grid(row=1, column=0, sticky="w", pady=5)
image_format = tb.Combobox(output_card, values=["JPG", "PNG"], state="readonly", width=8)
image_format.set("JPG")
image_format.grid(row=1, column=1, sticky="w", padx=5)

tb.Label(output_card, text="Frame Interval").grid(row=2, column=0, sticky="w", pady=5)
frame_interval_var = tk.IntVar(value=30)
tb.Entry(output_card, textvariable=frame_interval_var, width=10).grid(row=2, column=1, sticky="w", padx=5)

tb.Label(output_card, text="Image Name Prefix").grid(row=3, column=0, sticky="w", pady=5)
image_prefix_var = tk.StringVar(value="frame")
tb.Entry(output_card, textvariable=image_prefix_var, width=20).grid(row=3, column=1, sticky="w", padx=5)

# ================= BODY: LOG / PROGRESS =================
log_card = tb.Labelframe(app, text="Process Log", padding=15)
log_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
log_card.grid_rowconfigure(0, weight=1)
log_card.grid_columnconfigure(0, weight=1)

log = ScrolledText(log_card, height=20)
log.grid(row=0, column=0, sticky="nsew")
log.text.config(state="disabled")

progress_var = tk.DoubleVar(value=0)
progress = tb.Progressbar(log_card, variable=progress_var, maximum=100)
progress.grid(row=1, column=0, sticky="ew", pady=5)

# ================= FOOTER: ACTION BUTTONS =================
footer_frame = tb.Frame(app)
footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

stop_event = threading.Event()

def log_line(text):
    log.text.config(state="normal")
    log.text.insert("end", text + "\n")
    log.text.see("end")
    log.text.config(state="disabled")

def extract_frames():
    video_path = video_path_var.get()
    output_folder = output_folder_var.get()
    fmt = image_format.get().lower()
    interval = frame_interval_var.get()
    prefix = image_prefix_var.get()

    if not video_path or not os.path.exists(video_path):
        show_error("Input Error", "Please select a valid video file.")
        return
    if not output_folder:
        show_error("Output Error", "Please select an output folder.")
        return

    stop_event.clear()
    log.text.config(state="normal")
    log.text.delete("1.0", "end")
    log.text.config(state="disabled")
    progress_var.set(0)

    def worker():
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        current_frame = 0
        saved_count = 0

        while cap.isOpened():
            if stop_event.is_set():
                log_line("⛔ Extraction stopped by user.")
                break

            ret, frame = cap.read()
            if not ret:
                break

            if current_frame % interval == 0:
                filename = f"{prefix}_{current_frame}.{fmt}"
                filepath = os.path.join(output_folder, filename)
                cv2.imwrite(filepath, frame)
                saved_count += 1
                log_line(f"Saved {filename}")

            current_frame += 1
            progress_var.set(current_frame / total_frames * 100)
            app.update_idletasks()
            time.sleep(0.01)

        cap.release()
        if not stop_event.is_set():
            show_info("Done", f"Extraction completed!\nTotal images: {saved_count}")
            progress_var.set(100)

    threading.Thread(target=worker, daemon=True).start()

def stop_extraction():
    stop_event.set()

tb.Button(footer_frame, text="Start Extraction", bootstyle="success", width=20, command=extract_frames).pack(side="left", padx=5)
tb.Button(footer_frame, text="Stop", bootstyle="danger", width=15, command=stop_extraction).pack(side="left", padx=5)

# ================= HELP =================
def show_help():
    guide_window = tb.Toplevel(app)
    guide_window.title("📘 VID2IMG - Guide")
    guide_window.geometry("600x450")
    guide_window.resizable(False, False)
    guide_window.grab_set()

    frame = tb.Frame(guide_window, padding=10)
    frame.pack(fill="both", expand=True)

    sections = {
        "About VID2IMG": (
            "VID2IMG is a simple software to extract images from video files.\n"
            "Supports editing, anonymization, and photogrammetry workflows."
        ),
        "Key Features": (
            "- Extract frames from videos (MP4, AVI, MOV)\n"
            "- Set frame intervals and output format (JPG/PNG)\n"
            "- Choose output folder and filename prefix\n"
            "- Stop/resume extraction\n"
            "- Progress bar and live logging"
        ),
        "Requirements": (
            "- Windows PC\n"
            "- Python 3.x\n"
            "- OpenCV installed (`pip install opencv-python`)\n"
            "- ttkbootstrap installed (`pip install ttkbootstrap`)"
        ),
    }

    for title, text in sections.items():
        tb.Label(frame, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 0))
        tb.Label(frame, text=text, font=("Segoe UI", 10), wraplength=580, justify="left").pack(anchor="w", pady=(2, 5))

    tb.Button(frame, text="Close", bootstyle="danger-outline", width=15,
              command=guide_window.destroy).pack(pady=10)

tb.Button(footer_frame, text="Help / Guide", bootstyle="info", width=15, command=show_help).pack(side="right", padx=5)

app.mainloop()
