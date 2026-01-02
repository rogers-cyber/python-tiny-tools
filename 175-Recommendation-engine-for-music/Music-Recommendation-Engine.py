import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List, Tuple, Dict
import requests
import io
import json
import os

from PIL import Image, ImageTk
import pygame

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

# ---------------- CONFIG ---------------- #
RESULTS_PER_PAGE = 6
ITUNES_SEARCH_URL = "https://itunes.apple.com/search"

pygame.mixer.init()

# ---------------- GLOBAL STATE ---------------- #
all_ranked_tracks: List[Tuple["Track", float]] = []
current_page = 1
artwork_cache: Dict[str, ImageTk.PhotoImage] = {}

# ---------------- DATA STRUCTURE ---------------- #
@dataclass(frozen=True)
class Track:
    title: str
    artist: str
    album: str
    genre: str
    preview_url: str
    artwork_url: str
    track_url: str

    def text_blob(self, mode: str):
        if mode == "Artist":
            return self.artist
        if mode == "Genre":
            return self.genre
        return f"{self.title} {self.artist} {self.album} {self.genre}"


# ---------------- SEARCH / FETCH ---------------- #
def fetch_tracks(query: str, limit=40) -> List[Track]:
    tracks = []
    params = {"term": query, "entity": "song", "limit": limit}
    resp = requests.get(ITUNES_SEARCH_URL, params=params, timeout=10).json()

    for item in resp.get("results", []):
        tracks.append(
            Track(
                title=item.get("trackName", ""),
                artist=item.get("artistName", ""),
                album=item.get("collectionName", ""),
                genre=item.get("primaryGenreName", ""),
                preview_url=item.get("previewUrl", ""),
                artwork_url=item.get("artworkUrl100", ""),
                track_url=item.get("trackViewUrl", "")
            )
        )
    return tracks

# ---------------- RECOMMENDATION ENGINE ---------------- #
def recommend_tracks(query: str, candidates: List[Track], mode: str) -> List[Tuple[Track, float]]:
    docs = [t.text_blob(mode) for t in candidates]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs + [query])
    scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()

    ranked = list(zip(candidates, scores))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

# ---------------- UI HELPERS ---------------- #
def open_url(url: str):
    webbrowser.open_new_tab(url)

def load_image(url: str, size=(120, 120)):
    if not url:
        return None
    if url in artwork_cache:
        return artwork_cache[url]
    img = Image.open(io.BytesIO(requests.get(url).content)).resize(size)
    photo = ImageTk.PhotoImage(img)
    artwork_cache[url] = photo
    return photo

# ---------------- DISPLAY MAIN ---------------- #

def insert_track_main(track: Track):
    container = tk.Frame(text)

    art_label = tk.Label(container)
    art_label.pack(side=tk.LEFT)

    info_frame = tk.Frame(container)
    info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    tb.Label(info_frame, text=f"{track.title} — {track.artist}", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
    tb.Label(info_frame, text=f"Album: {track.album} | Genre: {track.genre}", font=("Segoe UI", 9)).pack(anchor=tk.W)

    btn_frame = tk.Frame(info_frame)
    btn_frame.pack(anchor=tk.W, pady=2)
    tb.Button(btn_frame, text="↗ Open", bootstyle="info",
              command=lambda u=track.track_url: open_url(u)).pack(side=tk.LEFT, padx=2)

    # Insert container into Text widget
    text.configure(state="normal")
    text.window_create("end", window=container)
    text.insert("end", "\n\n")
    text.configure(state="disabled")

    # ---------------- ASYNC IMAGE LOAD ---------------- #
    def async_load():
        photo = load_image(track.artwork_url)
        if photo:
            def safe_update():
                # Check if the widget still exists
                if art_label.winfo_exists():
                    art_label.configure(image=photo)
                    art_label.image = photo
            text.after(0, safe_update)

    threading.Thread(target=async_load, daemon=True).start()

def display_page():
    text.configure(state="normal")
    text.delete("1.0", "end")

    start = (current_page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE

    for track, score in all_ranked_tracks[start:end]:
        insert_track_main(track)

    text.configure(state="disabled")
    update_pagination()

# ---------------- PAGINATION ---------------- #
def next_page():
    global current_page
    if current_page * RESULTS_PER_PAGE < len(all_ranked_tracks):
        current_page += 1
        display_page()

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()

def update_pagination():
    total = max(1, (len(all_ranked_tracks) - 1) // RESULTS_PER_PAGE + 1)
    page_label.config(text=f"Page {current_page} of {total}")

# ---------------- SEARCH ---------------- #
def get_selected_modes():
    selected = [name for name, var in mode_vars.items() if var.get() == 1]
    if not selected:
        return ["All"]
    return selected

def perform_search():
    query = query_entry.get().strip()
    if not query:
        return
    threading.Thread(target=search_thread, args=(query,), daemon=True).start()

def search_thread(query: str):
    selected_modes = get_selected_modes()
    tracks = fetch_tracks(query)

    # If multiple modes selected, we can rank separately
    ranked_list = []

    for mode in selected_modes:
        ranked = recommend_tracks(query, tracks, mode)
        ranked_list.extend(ranked)

    # Sort by score descending
    ranked_list.sort(key=lambda x: x[1], reverse=True)

    # Remove duplicates
    seen = set()
    final_list = []
    for track, score in ranked_list:
        if track.title + track.artist not in seen:  # unique by title + artist
            seen.add(track.title + track.artist)
            final_list.append((track, score))

    # Update global list on main thread
    def update_ui():
        global all_ranked_tracks, current_page
        current_page = 1
        all_ranked_tracks = final_list
        display_page()

    app.after(0, update_ui)  # safe UI update

# ---------------- UI SETUP ---------------- #
app = tb.Window(
    title="Music Recommendation Engine",
    themename="darkly",
    size=(1000, 680),
    resizable=(True, True)
)


top = tb.Frame(app, padding=15)
top.pack(fill=tk.X)

tb.Label(top, text="🎵 Music Recommendation Engine", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)

query_entry = tb.Entry(top, font=("Segoe UI", 13))
query_entry.pack(fill=tk.X, pady=6)

# Bind Enter key to trigger search
query_entry.bind("<Return>", lambda event: perform_search())

# --- Mode Selection and Buttons in a single row ---
mode_vars = {
    "All": tk.IntVar(value=1),
    "Artist": tk.IntVar(value=0),
    "Genre": tk.IntVar(value=0)
}

def update_modes(changed):
    if changed == "All" and mode_vars["All"].get() == 1:
        mode_vars["Artist"].set(0)
        mode_vars["Genre"].set(0)
    elif changed in ["Artist", "Genre"] and mode_vars[changed].get() == 1:
        mode_vars["All"].set(0)
    elif all(var.get() == 0 for var in mode_vars.values()):
        mode_vars["All"].set(1)

# --- Frame for row ---
mode_button_frame = tb.Frame(top)
mode_button_frame.pack(fill=tk.X, pady=5)

# --- Checkboxes ---
for mode_name, var in mode_vars.items():
    cb = tb.Checkbutton(
        mode_button_frame, text=mode_name, variable=var, bootstyle="info",
        command=lambda m=mode_name: update_modes(m)
    )
    cb.pack(side=tk.LEFT, padx=5)

# --- Spacer ---
tb.Label(mode_button_frame, text=" " * 5).pack(side=tk.LEFT)  # optional spacing

# --- Buttons on the same row ---
tb.Button(mode_button_frame, text="Search", bootstyle="primary",
          command=perform_search).pack(side=tk.LEFT, padx=5)

# --- Results Display ---
result_frame = tb.Frame(app)
result_frame.pack(fill=tk.BOTH, expand=True)

result_box = ScrolledText(result_frame)
result_box.pack(fill=tk.BOTH, expand=True)
text = result_box.text
text.configure(state="disabled", wrap="word")

# --- Pagination ---
nav = tb.Frame(app, padding=10)
nav.pack()

tb.Button(nav, text="← Prev", command=prev_page).pack(side=tk.LEFT)
page_label = tb.Label(nav, text="Page 1")
page_label.pack(side=tk.LEFT, padx=10)
tb.Button(nav, text="Next →", command=next_page).pack(side=tk.LEFT)

app.mainloop()
