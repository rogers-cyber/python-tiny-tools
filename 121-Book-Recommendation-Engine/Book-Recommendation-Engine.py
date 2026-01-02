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

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

# ---------------- CONFIG ---------------- #
RESULTS_PER_PAGE = 6
OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"

# ---------------- GLOBAL STATE ---------------- #
all_ranked_books: List[Tuple["Book", float]] = []
current_page = 1
cover_cache: Dict[str, ImageTk.PhotoImage] = {}

# ---------------- DATA STRUCTURE ---------------- #
@dataclass(frozen=True)
class Book:
    title: str
    authors: List[str]
    description: str
    url: str
    cover_url: str = ""
    publish_year: int = 0

    def text_blob(self, mode: str):
        if mode == "Author":
            return " ".join(self.authors)
        return f"{self.title} {' '.join(self.authors)} {self.description}"


# ---------------- SEARCH / FETCH ---------------- #
def fetch_books(query: str, limit=40) -> List[Book]:
    books = []
    params = {"q": query, "limit": limit}
    resp = requests.get(OPENLIBRARY_SEARCH_URL, params=params, timeout=10).json()
    for item in resp.get("docs", []):
        title = item.get("title", "")
        authors = item.get("author_name", [])
        key = item.get("key", "")
        url = f"https://openlibrary.org{key}" if key else ""
        cover_id = item.get("cover_i", None)
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
        description = item.get("first_sentence", {}).get("value", "") if item.get("first_sentence") else ""
        publish_year = item.get("first_publish_year", 0)
        books.append(Book(title=title, authors=authors, description=description, url=url, cover_url=cover_url, publish_year=publish_year))
    return books

# ---------------- RECOMMENDATION ENGINE ---------------- #
def recommend_books(query: str, candidates: List[Book], mode: str) -> List[Tuple[Book, float]]:
    docs = [b.text_blob(mode) for b in candidates]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs + [query])
    scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
    ranked = list(zip(candidates, scores))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

# ---------------- UI HELPERS ---------------- #
def open_url(url: str):
    webbrowser.open_new_tab(url)

def load_cover(url: str, size=(120, 180)):
    if not url:
        return None
    if url in cover_cache:
        return cover_cache[url]
    try:
        img = Image.open(io.BytesIO(requests.get(url).content)).resize(size)
        photo = ImageTk.PhotoImage(img)
        cover_cache[url] = photo
        return photo
    except:
        return None

# ---------------- DISPLAY MAIN ---------------- #
def insert_book(container_widget, book: Book):
    frame = tk.Frame(container_widget)
    art_label = tk.Label(frame)
    art_label.pack(side=tk.LEFT)

    info_frame = tk.Frame(frame)
    info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    tb.Label(info_frame, text=f"{book.title}", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
    tb.Label(info_frame, text=f"By {', '.join(book.authors)} | Year: {book.publish_year}", font=("Segoe UI", 9)).pack(anchor=tk.W)
    btn_frame = tk.Frame(info_frame)
    btn_frame.pack(anchor=tk.W, pady=2)
    tb.Button(btn_frame, text="↗ Open", bootstyle="info", command=lambda u=book.url: open_url(u)).pack(side=tk.LEFT, padx=2)

    container_widget.configure(state="normal")
    container_widget.window_create("end", window=frame)
    container_widget.insert("end", "\n\n")
    container_widget.configure(state="disabled")

    def async_load():
        img = load_cover(book.cover_url)
        if img:
            def set_img():
                if art_label.winfo_exists():
                    art_label.configure(image=img)
                    art_label.image = img
            container_widget.after(0, set_img)
    threading.Thread(target=async_load, daemon=True).start()

def display_page():
    text.configure(state="normal")
    text.delete("1.0", "end")
    start = (current_page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    for book, score in all_ranked_books[start:end]:
        insert_book(text, book)
    text.configure(state="disabled")
    update_pagination()

# ---------------- PAGINATION ---------------- #
def next_page():
    global current_page
    if current_page * RESULTS_PER_PAGE < len(all_ranked_books):
        current_page += 1
        display_page()

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()

def update_pagination():
    total = max(1, (len(all_ranked_books) - 1) // RESULTS_PER_PAGE + 1)
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
    books = fetch_books(query)
    ranked_list = []
    for mode in selected_modes:
        ranked = recommend_books(query, books, mode)
        ranked_list.extend(ranked)
    ranked_list.sort(key=lambda x: x[1], reverse=True)
    seen = set()
    final_list = []
    for book, score in ranked_list:
        key = book.title + "".join(book.authors)
        if key not in seen:
            seen.add(key)
            final_list.append((book, score))
    def update_ui():
        global all_ranked_books, current_page
        current_page = 1
        all_ranked_books = final_list
        display_page()
    app.after(0, update_ui)

# ---------------- UI SETUP ---------------- #
app = tb.Window(title="Book Recommendation Engine", themename="darkly", size=(1000, 680), resizable=(True, True))

top = tb.Frame(app, padding=15)
top.pack(fill=tk.X)

tb.Label(top, text="📚 Book Recommendation Engine", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)

query_entry = tb.Entry(top, font=("Segoe UI", 13))
query_entry.pack(fill=tk.X, pady=6)
query_entry.bind("<Return>", lambda e: perform_search())

# Mode selection
mode_vars = {"All": tk.IntVar(value=1), "Author": tk.IntVar(value=0)}
def update_modes(changed):
    if changed == "All" and mode_vars["All"].get() == 1:
        mode_vars["Author"].set(0)
    elif changed == "Author" and mode_vars["Author"].get() == 1:
        mode_vars["All"].set(0)
    elif all(var.get() == 0 for var in mode_vars.values()):
        mode_vars["All"].set(1)
mode_button_frame = tb.Frame(top)
mode_button_frame.pack(fill=tk.X, pady=5)
for name, var in mode_vars.items():
    tb.Checkbutton(mode_button_frame, text=name, variable=var, bootstyle="info", command=lambda n=name: update_modes(n)).pack(side=tk.LEFT, padx=5)
tb.Label(mode_button_frame, text=" " * 5).pack(side=tk.LEFT)
tb.Button(mode_button_frame, text="Search", bootstyle="primary", command=perform_search).pack(side=tk.LEFT, padx=5)

# Results
result_frame = tb.Frame(app)
result_frame.pack(fill=tk.BOTH, expand=True)
result_box = ScrolledText(result_frame)
result_box.pack(fill=tk.BOTH, expand=True)
text = result_box.text
text.configure(state="disabled", wrap="word")

# Pagination
nav = tb.Frame(app, padding=10)
nav.pack()
tb.Button(nav, text="← Prev", command=prev_page).pack(side=tk.LEFT)
page_label = tb.Label(nav, text="Page 1")
page_label.pack(side=tk.LEFT, padx=10)
tb.Button(nav, text="Next →", command=next_page).pack(side=tk.LEFT)

app.mainloop()
