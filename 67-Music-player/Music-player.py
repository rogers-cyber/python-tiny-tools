import os
import threading
import time
import io
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ---------------- VLC / Pygame ---------------- #
VLC_AVAILABLE = True
try:
    import vlc
except ImportError:
    VLC_AVAILABLE = False

if not VLC_AVAILABLE:
    try:
        import pygame
        pygame.mixer.init()
        FALLBACK = True
    except ImportError:
        FALLBACK = False
else:
    FALLBACK = False

if not VLC_AVAILABLE and not FALLBACK:
    raise ImportError("Neither python-vlc nor pygame installed.")

# ---------------- TinyTag for album art ---------------- #
try:
    from tinytag import TinyTag, TinyTagException
except ImportError:
    TinyTag = None

# ---------------- GLOBALS ---------------- #
playlist = []
current_index = -1
is_paused = False
loop_mode = False
album_art_cache = {}

if VLC_AVAILABLE:
    vlc_instance = vlc.Instance("--no-video", "--quiet")
    player = vlc_instance.media_player_new()
else:
    player = None

# ---------------- FUNCTIONS ---------------- #
def add_files():
    global playlist
    files = filedialog.askopenfilenames(
        filetypes=[("Media Files", "*.mp3 *.wav *.mp4 *.m4a *.flac")]
    )
    for f in files:
        playlist.append(f)
        listbox.insert(tk.END, os.path.basename(f))

def extract_album_art(path):
    if not TinyTag:
        return None
    try:
        tag = TinyTag.get(path, image=True)
        if tag.images and tag.images.front_cover:
            img_data = tag.images.front_cover.data
            img = Image.open(io.BytesIO(img_data)).resize((200, 200))
            return ImageTk.PhotoImage(img)
    except:
        return None
    return None

def play_track(index=None):
    global current_index, is_paused
    if index is not None:
        current_index = index
    if current_index < 0 or current_index >= len(playlist):
        return
    file = playlist[current_index]

    now_playing_label.config(text=f"Now Playing: {os.path.basename(file)}")

    # Album art
    if file in album_art_cache:
        art_img = album_art_cache[file]
    else:
        art_img = extract_album_art(file)
        album_art_cache[file] = art_img
    if art_img:
        album_art_label.config(image=art_img)
        album_art_label.image = art_img
    else:
        album_art_label.config(image='')

    # Play
    if VLC_AVAILABLE:
        media = vlc_instance.media_new(file)
        player.set_media(media)
        player.play()
        time.sleep(0.1)
        duration_sec = max(player.get_length()/1000, 1)
        duration_label.config(text=f"Duration: {format_time(0)} / {format_time(duration_sec)}")
        threading.Thread(target=update_progress, daemon=True).start()
        threading.Thread(target=monitor_track_end, daemon=True).start()
    elif FALLBACK:
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            duration_label.config(text="Duration: Unknown")
            threading.Thread(target=monitor_track_end, daemon=True).start()
        except:
            messagebox.showerror("Error", f"Cannot play file: {file}")

    is_paused = False

def pause_track():
    global is_paused
    if VLC_AVAILABLE:
        if player.is_playing():
            player.pause()
            is_paused = True
        elif is_paused:
            player.play()
            is_paused = False
    elif FALLBACK:
        if pygame.mixer.music.get_busy():
            if not is_paused:
                pygame.mixer.music.pause()
                is_paused = True
            else:
                pygame.mixer.music.unpause()
                is_paused = False

def stop_track():
    global is_paused
    if VLC_AVAILABLE:
        player.stop()
    elif FALLBACK:
        pygame.mixer.music.stop()
    is_paused = False
    progress_var.set(0)
    now_playing_label.config(text="Now Playing: ")
    album_art_label.config(image='')
    duration_label.config(text="Duration: 00:00 / 00:00")

def next_track():
    global current_index
    if current_index + 1 < len(playlist):
        current_index += 1
        play_track(current_index)
    elif loop_mode and playlist:
        current_index = 0
        play_track(current_index)

def prev_track():
    global current_index
    if current_index - 1 >= 0:
        current_index -= 1
        play_track(current_index)
    elif loop_mode and playlist:
        current_index = len(playlist) - 1
        play_track(current_index)

def set_volume(val):
    vol = int(float(val))
    if VLC_AVAILABLE:
        player.audio_set_volume(vol)
    elif FALLBACK:
        pygame.mixer.music.set_volume(vol / 100)

def update_progress():
    while True:
        if VLC_AVAILABLE and player.is_playing():
            length = max(player.get_length()/1000, 1)
            pos = player.get_time()/1000
            progress_bar.config(to=length)
            progress_var.set(pos)
            duration_label.config(text=f"Duration: {format_time(pos)} / {format_time(length)}")
        elif FALLBACK and pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos()/1000
            progress_var.set(pos)
        else:
            break
        time.sleep(0.5)

def seek(event):
    if VLC_AVAILABLE and player.get_media():
        player.set_time(int(progress_var.get()*1000))
    elif FALLBACK:
        pygame.mixer.music.play(start=progress_var.get())

def format_time(seconds):
    seconds = int(seconds)
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

def monitor_track_end():
    """Automatically play next track when current track ends"""
    global current_index
    while True:
        if VLC_AVAILABLE and player.get_media():
            if not player.is_playing() and not is_paused:
                time.sleep(0.2)
                next_track()
                break
        elif FALLBACK:
            if not pygame.mixer.music.get_busy() and not is_paused:
                time.sleep(0.2)
                next_track()
                break
        else:
            break
        time.sleep(0.5)

# Drag & Drop playlist
drag_data = None
def on_drag_start(event):
    global drag_data
    drag_data = {"widget": event.widget, "index": event.widget.nearest(event.y)}

def on_drag_release(event):
    global drag_data
    if not drag_data:
        return
    widget = drag_data.get("widget")
    start_index = drag_data.get("index")
    if widget is None or start_index is None:
        drag_data = None
        return
    end_index = widget.nearest(event.y)
    if start_index != end_index:
        playlist[start_index], playlist[end_index] = playlist[end_index], playlist[start_index]
        listbox.delete(0, tk.END)
        for f in playlist:
            listbox.insert(tk.END, os.path.basename(f))
    drag_data = None

# ---------------- GUI ---------------- #
app = tb.Window(themename="darkly", title="VLC-Style Music Player", size=(900, 550))

# Playlist
left_frame = tb.Frame(app)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
listbox = tk.Listbox(left_frame)
listbox.pack(fill=tk.BOTH, expand=True)
listbox.bind("<Double-1>", lambda e: (
    play_track(listbox.curselection()[0]) if listbox.curselection() else None
))
listbox.bind("<Button-1>", on_drag_start)
listbox.bind("<ButtonRelease-1>", on_drag_release)
tb.Button(left_frame, text="Add Files", bootstyle="primary", command=add_files).pack(pady=5)

# Controls + Album Art
right_frame = tb.Frame(app)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

album_art_label = tk.Label(right_frame)
album_art_label.pack(pady=10)

now_playing_label = tb.Label(right_frame, text="Now Playing: ", font=("Segoe UI", 10, "bold"))
now_playing_label.pack()

duration_label = tb.Label(right_frame, text="Duration: 00:00 / 00:00", font=("Segoe UI", 9))
duration_label.pack()

progress_var = tk.DoubleVar()
progress_bar = tb.Scale(right_frame, variable=progress_var, from_=0, to=100, orient=tk.HORIZONTAL)
progress_bar.pack(fill=tk.X, padx=5)
progress_bar.bind("<ButtonRelease-1>", seek)

control_frame = tb.Frame(right_frame)
control_frame.pack(pady=10)
tb.Button(control_frame, text="⏮ Prev", bootstyle="secondary", command=prev_track).pack(side=tk.LEFT, padx=5)
tb.Button(control_frame, text="▶ Play", bootstyle="success", command=lambda: (
    play_track(listbox.curselection()[0] if listbox.curselection() else None)
)).pack(side=tk.LEFT, padx=5)
tb.Button(control_frame, text="⏸ Pause", bootstyle="warning", command=pause_track).pack(side=tk.LEFT, padx=5)
tb.Button(control_frame, text="⏹ Stop", bootstyle="danger", command=stop_track).pack(side=tk.LEFT, padx=5)
tb.Button(control_frame, text="⏭ Next", bootstyle="secondary", command=next_track).pack(side=tk.LEFT, padx=5)

loop_var = tk.IntVar()
tb.Checkbutton(right_frame, text="Loop Playlist", variable=loop_var, bootstyle="info",
               command=lambda: set_loop()).pack(pady=5)

volume_frame = tb.Frame(right_frame)
volume_frame.pack(pady=5)
tb.Label(volume_frame, text="Volume").pack(side=tk.LEFT, padx=5)
volume_slider = tb.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=set_volume)
volume_slider.set(50)
volume_slider.pack(side=tk.LEFT)

def set_loop():
    global loop_mode
    loop_mode = bool(loop_var.get())

app.mainloop()
