import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import requests
import io
from PIL import Image, ImageTk  # pip install pillow

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

# ---------------- CONFIG ---------------- #
RESULTS_PER_PAGE = 6
OMDB_API_KEY = "YOUR_OMDB_API_KEY"  # ← replace with your OMDb API key
OMDB_SEARCH_URL = "http://www.omdbapi.com/"

# ---------------- GLOBAL STATE ---------------- #
all_ranked_movies: List[Tuple["Movie", float]] = []
current_page = 1
poster_cache: Dict[str, ImageTk.PhotoImage] = {}

# ---------------- DATA STRUCTURE ---------------- #
@dataclass
class Movie:
    title: str
    imdb_id: str
    url: str
    description: str
    poster_url: str
    genres: List[str] = None
    director: str = ""
    actors: List[str] = None
    rating: float = 0.0

# ---------------- SEARCH / FETCH ---------------- #
def fetch_movies(query: str) -> List[Movie]:
    """Fetch movies from OMDb API matching the query."""
    movies: List[Movie] = []
    try:
        params = {"apikey": OMDB_API_KEY, "s": query, "type": "movie"}
        resp = requests.get(OMDB_SEARCH_URL, params=params, timeout=10)
        data = resp.json()

        if data.get("Response") != "True":
            return []

        for item in data.get("Search", []):
            imdb_id = item.get("imdbID")
            detail_resp = requests.get(
                OMDB_SEARCH_URL,
                params={"apikey": OMDB_API_KEY, "i": imdb_id, "plot": "short"},
                timeout=10
            ).json()

            genres = detail_resp.get("Genre", "")
            actors = detail_resp.get("Actors", "")
            movies.append(
                Movie(
                    title=detail_resp.get("Title", "Unknown"),
                    imdb_id=imdb_id,
                    url=f"https://www.imdb.com/title/{imdb_id}/",
                    description=detail_resp.get("Plot", ""),
                    poster_url=detail_resp.get("Poster", ""),
                    genres=[g.strip() for g in genres.split(",")] if genres else [],
                    director=detail_resp.get("Director", ""),
                    actors=[a.strip() for a in actors.split(",")] if actors else [],
                    rating=float(detail_resp.get("imdbRating", 0.0)) if detail_resp.get("imdbRating") != "N/A" else 0.0
                )
            )
    except requests.RequestException as e:
        messagebox.showerror("API Error", f"Network error: {e}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    return movies

# ---------------- RECOMMENDATION ENGINE ---------------- #
def recommend_movies(query: str, candidates: List[Movie], top_n=RESULTS_PER_PAGE) -> List[Tuple[Movie, float]]:
    """
    Simple content-based recommendation:
    Scores movies by overlap with query in title, description, and genres
    """
    query_tokens = set(query.lower().split())
    recommendations: List[Tuple[Movie, float]] = []

    for movie in candidates:
        text_to_match = " ".join([
            movie.title.lower(),
            movie.description.lower(),
            " ".join(movie.genres or [])
        ])
        score = sum(1 for token in query_tokens if token in text_to_match)
        recommendations.append((movie, score))

    # Sort descending by score
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:top_n]

# ---------------- UI HELPERS ---------------- #
def open_url(url: str):
    webbrowser.open_new_tab(url)

def load_image(url: str, size=(100, 150)) -> Optional[ImageTk.PhotoImage]:
    """Load poster image from URL, with caching."""
    if not url or url == "N/A":
        return None
    if url in poster_cache:
        return poster_cache[url]
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(io.BytesIO(resp.content))
        img = img.resize(size, Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        poster_cache[url] = photo
        return photo
    except Exception:
        return None

def display_page():
    text.configure(state="normal")
    text.delete("1.0", "end")

    start = (current_page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = all_ranked_movies[start:end]

    if not page_results:
        text.insert("end", "No results found.\n")
        text.configure(state="disabled")
        update_pagination()
        return

    for idx, (movie, score) in enumerate(page_results):
        # Title
        text.insert("end", f"{movie.title}\n", f"title_{idx}")
        text.tag_config(f"title_{idx}", foreground="#1a0dab", font=("Segoe UI", 14, "bold"))
        text.tag_bind(f"title_{idx}", "<Double-Button-1>", lambda e, url=movie.url: open_url(url))

        # Display URL and IMDB rating
        text.insert("end", f"{movie.url}  |  Rating: {movie.rating}\n", f"url_{idx}")
        text.tag_config(f"url_{idx}", foreground="#006621", font=("Segoe UI", 10))

        # Poster
        poster = load_image(movie.poster_url)
        if poster:
            text.image_create("end", image=poster)
            text.insert("end", "\n")

        # Description & genres
        genres = ", ".join(movie.genres or [])
        text.insert("end", f"{movie.description}\nGenres: {genres}\n\n")

    text.configure(state="disabled")
    update_pagination()

# ---------------- PAGINATION ---------------- #
def next_page():
    global current_page
    if current_page * RESULTS_PER_PAGE < len(all_ranked_movies):
        current_page += 1
        display_page()

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()

def update_pagination():
    total_pages = max(1, (len(all_ranked_movies) - 1) // RESULTS_PER_PAGE + 1)
    page_label.config(text=f"Page {current_page} of {total_pages}")
    prev_btn.config(state=DISABLED if current_page == 1 else NORMAL)
    next_btn.config(state=DISABLED if current_page == total_pages else NORMAL)

# ---------------- SEARCH ---------------- #
def perform_search():
    query = query_entry.get().strip()
    if not query:
        messagebox.showwarning("Input Required", "Enter a movie title or keywords.")
        return
    threading.Thread(target=search_thread, args=(query,), daemon=True).start()

def search_thread(query: str):
    global all_ranked_movies, current_page
    current_page = 1
    candidates = fetch_movies(query)
    all_ranked_movies = recommend_movies(query, candidates, top_n=50)  # get top 50 recommendations
    display_page()

# ---------------- UI SETUP ---------------- #
app = tb.Window(title="Movie Recommendation Engine", themename="flatly", size=(980, 720), resizable=(True, True))

# Top frame
top = tb.Frame(app, padding=15)
top.pack(fill=tk.X)
tb.Label(top, text="Movie Recommendation Engine", font=("Segoe UI", 16, "bold")).pack(anchor=tk.W)

query_entry = tb.Entry(top, font=("Segoe UI", 12))
query_entry.pack(fill=tk.X, pady=8)
query_entry.bind("<Return>", lambda e: perform_search())

tb.Button(top, text="Search", bootstyle="primary", command=perform_search).pack(anchor=tk.E)

# Results frame
result_frame = tb.Frame(app, padding=(15, 5))
result_frame.pack(fill=tk.BOTH, expand=True)

result_box = ScrolledText(result_frame, autohide=True)
result_box.pack(fill=tk.BOTH, expand=True)
text = result_box.text
text.configure(state="disabled", wrap="word")

# Navigation
nav = tb.Frame(app, padding=10)
nav.pack(fill=tk.X)

prev_btn = tb.Button(nav, text="← Prev", bootstyle="secondary", command=prev_page)
prev_btn.pack(side=tk.LEFT)

page_label = tb.Label(nav, text="Page 1", font=("Segoe UI", 10))
page_label.pack(side=tk.LEFT, padx=10)

next_btn = tb.Button(nav, text="Next →", bootstyle="secondary", command=next_page)
next_btn.pack(side=tk.LEFT)

app.mainloop()
