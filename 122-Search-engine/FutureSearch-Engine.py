import threading
import webbrowser
import tkinter as tk
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from ddgs import DDGS

# ---------------- CONFIG ---------------- #
RESULTS_PER_PAGE = 5

# ---------------- GLOBAL STATE ---------------- #
all_ranked_results: List["SearchResult"] = []
current_page = 1

# ---------------- DATA STRUCTURE ---------------- #
@dataclass
class SearchResult:
    title: str
    url: str
    display_url: str
    snippet: str

# ---------------- HELPERS ---------------- #
def short_display_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").split("/")[:5]
    if path and path[0]:
        return f"{parsed.netloc} › " + " › ".join(path)
    return parsed.netloc

def open_url(url: str):
    webbrowser.open_new_tab(url)

# ---------------- SEARCH LOGIC ---------------- #
def fetch_search_results(query: str) -> List[SearchResult]:
    results = []
    try:
        with DDGS() as ddgs:
            for entry in ddgs.text(query, max_results=25):
                title = entry.get("title") or "Untitled"
                url = entry.get("href") or ""
                snippet = entry.get("body") or "No description available."
                results.append(SearchResult(
                    title=title,
                    url=url,
                    display_url=short_display_url(url),
                    snippet=snippet
                ))
    except Exception as e:
        tb.Messagebox.show_error("Search Error", str(e))
    return results

def rank_results(query: str, results: List[SearchResult]) -> List[tuple]:
    if not results:
        return []
    docs = [f"{r.title} {r.snippet}" for r in results]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(docs + [query])
    tfidf_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    bm25 = BM25Okapi([d.lower().split() for d in docs])
    bm25_scores = bm25.get_scores(query.lower().split())
    ranked = []
    for i, res in enumerate(results):
        score = (tfidf_scores[i] + bm25_scores[i]) / 2
        ranked.append((res, score))
    return sorted(ranked, key=lambda x: x[1], reverse=True)

# ---------------- DISPLAY ---------------- #
def display_page():
    for widget in results_frame.winfo_children():
        widget.destroy()

    start = (current_page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = all_ranked_results[start:end]

    if not page_results:
        tb.Label(
            results_frame,
            text="No results found.",
            font=("Segoe UI", 12),
            foreground="#333333"
        ).pack(pady=10)
        return

    for res, score in page_results:
        # Frame without extra background, inherits parent
        card = tb.Frame(results_frame, padding=15)
        card.pack(fill=X, pady=8, padx=5)

        # Title (clickable with hover effect)
        title_label = tb.Label(
            card,
            text=res.title,
            font=("Segoe UI", 14, "bold"),
            cursor="hand2",
            foreground="#1a0dab"
        )
        title_label.pack(anchor=W)
        title_label.bind("<Button-1>", lambda e, url=res.url: open_url(url))
        title_label.bind("<Enter>", lambda e: title_label.configure(foreground="#0b3d91"))
        title_label.bind("<Leave>", lambda e: title_label.configure(foreground="#1a0dab"))

        # URL / Domain
        tb.Label(
            card,
            text=res.display_url,
            font=("Segoe UI", 10, "italic"),
            foreground="#006400"
        ).pack(anchor=W, pady=(2,5))

        # Snippet with ellipsis
        snippet_text = res.snippet
        if len(snippet_text) > 250:
            snippet_text = snippet_text[:247] + "..."
        tb.Label(
            card,
            text=snippet_text,
            font=("Segoe UI", 12),
            wraplength=900,
            foreground="#333333"
        ).pack(anchor=W)

# ---------------- PAGINATION ---------------- #
def next_page():
    global current_page
    if current_page * RESULTS_PER_PAGE < len(all_ranked_results):
        current_page += 1
        display_page()
        update_pagination()

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()
        update_pagination()

def update_pagination():
    total = max(1, (len(all_ranked_results) - 1) // RESULTS_PER_PAGE + 1)
    page_label.config(text=f"Page {current_page} of {total}")
    prev_btn.config(state=DISABLED if current_page == 1 else NORMAL)
    next_btn.config(state=DISABLED if current_page == total else NORMAL)

# ---------------- SEARCH ---------------- #
def perform_search():
    query = query_entry.get().strip()
    if not query:
        tb.Messagebox.show_warning("Input Required", "Enter a search query.")
        return

    # Disable search button and show "Searching..." text
    search_button.config(state=DISABLED)
    for widget in results_frame.winfo_children():
        widget.destroy()
    tb.Label(results_frame, text="Searching...", font=("Segoe UI", 12)).pack(pady=8, padx=5)
    
    # Start the search in a separate thread
    threading.Thread(target=search_thread, args=(query,), daemon=True).start()


def search_thread(query):
    global all_ranked_results, current_page

    try:
        # Fetch and rank results
        results = fetch_search_results(query)
        all_ranked_results = rank_results(query, results)
        current_page = 1

        # Schedule the UI update on the main thread
        app.after(0, lambda: (
            display_page(),
            update_pagination(),
            search_button.config(state=NORMAL)  # Re-enable search button
        ))

    except Exception as e:
        # Show error on the main thread
        app.after(0, lambda: (
            tb.Messagebox.show_error("Search Error", str(e)),
            search_button.config(state=NORMAL)
        ))

# ---------------- UI ---------------- #
app = tb.Window(title="FutureSearch Engine", themename="flatly", size=(980, 720))

# Top search frame
top_frame = tb.Frame(app, padding=15)
top_frame.pack(fill=X)

tb.Label(top_frame, text="🌟 FutureSearch Engine", font=("Segoe UI", 18, "bold")).pack(anchor=W)
query_entry = tb.Entry(top_frame, font=("Segoe UI", 12))
query_entry.pack(fill=X, pady=8)
query_entry.bind("<Return>", lambda e: perform_search())
# Assign the search button to a variable
search_button = tb.Button(top_frame, text="Search", bootstyle="success", command=perform_search)
search_button.pack(anchor=E)


# Scrollable results
results_container = tb.Frame(app)
results_container.pack(fill=BOTH, expand=True)

canvas = tk.Canvas(results_container, highlightthickness=0)
scrollbar = tb.Scrollbar(results_container, orient="vertical", command=canvas.yview)
results_frame = tb.Frame(canvas)

results_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=results_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Pagination
nav_frame = tb.Frame(app, padding=10)
nav_frame.pack(fill=X)
prev_btn = tb.Button(nav_frame, text="← Prev", bootstyle="secondary", command=prev_page)
prev_btn.pack(side=LEFT)
page_label = tb.Label(nav_frame, text="Page 1", font=("Segoe UI", 10))
page_label.pack(side=LEFT, padx=10)
next_btn = tb.Button(nav_frame, text="Next →", bootstyle="secondary", command=next_page)
next_btn.pack(side=LEFT)

app.mainloop()
