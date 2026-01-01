import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from ddgs import DDGS

# ---------------- CONFIG ---------------- #
RESULTS_PER_PAGE = 6  # Can be changed via UI

# ---------------- GLOBAL STATE ---------------- #
all_ranked_results: List["SearchResult"] = []
current_page = 1
recent_queries: List[str] = []

# ---------------- DATA STRUCTURE ---------------- #
@dataclass
class SearchResult:
    title: str
    url: str
    display_url: str
    snippet: str

# ---------------- URL HELPERS ---------------- #
def short_display_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").split("/")[:5]
    if path and path[0]:
        return f"{parsed.netloc} › " + " › ".join(path)
    return parsed.netloc

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
        messagebox.showerror("Search Error", f"An error occurred: {str(e)}")
        return []
    return results

def rank_results(query: str, results: List[SearchResult]) -> List[tuple]:
    if not results:
        return []
    
    docs = [f"{r.title} {r.snippet}" for r in results]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(docs + [query])
    
    if tfidf_matrix.shape[0] <= 1:
        return [(res, 0) for res in results]
    
    tfidf_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    bm25 = BM25Okapi([d.lower().split() for d in docs])
    bm25_scores = bm25.get_scores(query.lower().split())
    
    ranked = []
    for i, res in enumerate(results):
        score = (tfidf_scores[i] + bm25_scores[i]) / 2
        ranked.append((res, score))
    
    return sorted(ranked, key=lambda x: x[1], reverse=True)

# ---------------- UI HELPERS ---------------- #
def open_url(url: str):
    if url:
        webbrowser.open_new_tab(url)

def highlight_query_words(text_widget, query):
    for word in query.split():
        start = "1.0"
        while True:
            pos = text_widget.search(word, start, stopindex="end", nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(word)}c"
            text_widget.tag_add("highlight", pos, end_pos)
            start = end_pos
    text_widget.tag_config("highlight", background="#fff59d")  # yellow

# ---------------- DISPLAY ---------------- #
def display_page():
    text.configure(state="normal")
    text.delete("1.0", "end")
    
    start = (current_page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = all_ranked_results[start:end]
    
    if not page_results:
        text.insert("end", "No results found.\n")
        text.configure(state="disabled")
        update_pagination()
        return
    
    for idx, (res, _) in enumerate(page_results):
        # Title
        title_tag = f"title_{idx}"
        text.tag_config(title_tag, foreground="#1a0dab", font=("Segoe UI", 14, "bold"), spacing1=5)
        text.insert("end", res.title + "\n", title_tag)
        text.tag_bind(title_tag, "<Double-Button-1>", lambda e, url=res.url: open_url(url))
        text.tag_bind(title_tag, "<Enter>", lambda e: text.config(cursor="hand2"))
        text.tag_bind(title_tag, "<Leave>", lambda e: text.config(cursor=""))
        
        # URL
        url_tag = f"url_{idx}"
        text.tag_config(url_tag, foreground="#188038", font=("Segoe UI", 11, "italic"))
        text.insert("end", res.display_url + "\n", url_tag)
        
        # Snippet
        snippet_tag = f"snippet_{idx}"
        text.tag_config(snippet_tag, foreground="#4d5156", font=("Segoe UI", 12), spacing3=10)
        text.insert("end", res.snippet + "\n\n", snippet_tag)
    
    # Highlight query words
    highlight_query_words(text, query_entry.get())
    
    text.configure(state="disabled")
    text.yview_moveto(0)
    update_pagination()

# ---------------- PAGINATION ---------------- #
def next_page():
    global current_page
    total_pages = max(1, (len(all_ranked_results) - 1) // RESULTS_PER_PAGE + 1)
    if current_page < total_pages:
        current_page += 1
        display_page()

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()

def update_pagination():
    total_pages = max(1, (len(all_ranked_results) - 1) // RESULTS_PER_PAGE + 1)
    page_label.config(text=f"Page {current_page} of {total_pages}")
    prev_btn.config(state=DISABLED if current_page == 1 else NORMAL)
    next_btn.config(state=DISABLED if current_page >= total_pages else NORMAL)

# ---------------- SEARCH ---------------- #
def perform_search():
    query = query_entry.get().strip()
    if not query:
        messagebox.showwarning("Input Required", "Enter a search query.")
        return
    if query not in recent_queries:
        recent_queries.append(query)
    threading.Thread(target=search_thread, args=(query,), daemon=True).start()

def search_thread(query):
    global all_ranked_results, current_page
    current_page = 1
    update_text(lambda: text.insert("end", "Searching...\n"))
    
    results = fetch_search_results(query)
    all_ranked_results = rank_results(query, results)
    display_page()

def update_text(callback):
    text.configure(state="normal")
    callback()
    text.configure(state="disabled")

# ---------------- UI SETUP ---------------- #
app = tb.Window(title="Search Ranking App", themename="flatly", size=(980,700), resizable=(True,True))

top = tb.Frame(app, padding=15)
top.pack(fill=X)

tb.Label(top, text="Search", font=("Segoe UI", 16, "bold")).pack(anchor=W)

query_entry = tb.Entry(top, font=("Segoe UI",12))
query_entry.pack(fill=X, pady=8)
query_entry.bind("<Return>", lambda e: perform_search())

tb.Button(top, text="Search", bootstyle="primary", command=perform_search).pack(anchor=E)

# Results
result_frame = tb.Frame(app, padding=(15,5))
result_frame.pack(fill=BOTH, expand=True)

result_box = ScrolledText(result_frame, autohide=True)
result_box.pack(fill=BOTH, expand=True)

text = result_box.text
text.configure(state="disabled", wrap="word")

# Pagination
nav = tb.Frame(app, padding=10)
nav.pack(fill=X)

prev_btn = tb.Button(nav, text="← Prev", bootstyle="secondary", command=prev_page)
prev_btn.pack(side=LEFT)

page_label = tb.Label(nav, text="Page 1", font=("Segoe UI",10))
page_label.pack(side=LEFT, padx=10)

next_btn = tb.Button(nav, text="Next →", bootstyle="secondary", command=next_page)
next_btn.pack(side=LEFT)

# ---------------- RUN ---------------- #
app.mainloop()
