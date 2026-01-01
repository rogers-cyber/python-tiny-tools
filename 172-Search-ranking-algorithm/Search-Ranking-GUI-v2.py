import threading
import webbrowser
import requests

import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

from urllib.parse import urlparse, parse_qs, unquote


# ---------------- CONFIG ---------------- #

RESULTS_PER_PAGE = 6


# ---------------- GLOBAL STATE ---------------- #

all_ranked_results = []
current_page = 1
favorites = set()


# ---------------- URL CLEANING ---------------- #

def clean_duckduckgo_url(url):
    if "duckduckgo.com/l/?" in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if "uddg" in params:
            return unquote(params["uddg"][0])
    return url


def short_display_url(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/").split("/")[:5]
    if path and path[0]:
        return f"{parsed.netloc} › " + " › ".join(path)
    return parsed.netloc


# ---------------- SEARCH LOGIC ---------------- #

def fetch_search_results(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(
        f"https://duckduckgo.com/html/?q={query}",
        headers=headers,
        timeout=10
    )

    results = []
    if response.status_code != 200:
        return results

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", class_="result__a")

    for link in links[:25]:
        raw_url = link.get("href")
        clean_url = clean_duckduckgo_url(raw_url)

        snippet_tag = link.find_parent("div", class_="result").find(
            "a", class_="result__snippet"
        )
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        results.append({
            "title": link.get_text(strip=True),
            "url": clean_url,
            "display_url": short_display_url(clean_url),
            "snippet": snippet or "No description available."
        })

    return results


def rank_results(query, results):
    docs = [r["title"] + " " + r["snippet"] for r in results]

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(docs + [query])
    tfidf_scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()

    bm25 = BM25Okapi([d.split() for d in docs])
    bm25_scores = bm25.get_scores(query.split())

    ranked = []
    for i, res in enumerate(results):
        score = (tfidf_scores[i] + bm25_scores[i]) / 2
        ranked.append((res, score))

    return sorted(ranked, key=lambda x: x[1], reverse=True)


# ---------------- UI HELPERS ---------------- #

def open_url(url):
    webbrowser.open_new_tab(url)


def toggle_favorite(url, btn):
    if url in favorites:
        favorites.remove(url)
        btn.config(text="☆")
    else:
        favorites.add(url)
        btn.config(text="★")


# ---------------- DISPLAY ---------------- #

def display_page():
    text.configure(state="normal")
    text.delete("1.0", "end")

    start = (current_page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = all_ranked_results[start:end]

    for idx, (res, _) in enumerate(page_results):
        title_tag = f"title_{idx}"

        text.insert("end", res["title"] + "\n", (title_tag,))
        text.insert("end", res["display_url"] + "\n", "url")
        text.insert("end", res["snippet"] + "\n\n", "snippet")

        # --- CLICK OPENS CORRECT URL ---
        text.tag_bind(
            title_tag,
            "<Button-1>",
            lambda e, url=res["url"]: open_url(url)
        )

        # --- HOVER CURSOR ---
        text.tag_bind(
            title_tag,
            "<Enter>",
            lambda e: text.config(cursor="hand2")
        )
        text.tag_bind(
            title_tag,
            "<Leave>",
            lambda e: text.config(cursor="")
        )

    text.configure(state="disabled")
    update_pagination_label()


def update_pagination_label():
    total_pages = max(1, (len(all_ranked_results) - 1) // RESULTS_PER_PAGE + 1)
    page_label.config(text=f"Page {current_page} of {total_pages}")


# ---------------- PAGINATION ---------------- #

def next_page():
    global current_page
    if current_page * RESULTS_PER_PAGE < len(all_ranked_results):
        current_page += 1
        display_page()


def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()


# ---------------- SEARCH ---------------- #

def perform_search():
    query = query_entry.get().strip()
    if not query:
        messagebox.showwarning("Input Required", "Enter a search query.")
        return

    threading.Thread(target=search_thread, args=(query,), daemon=True).start()


def search_thread(query):
    global all_ranked_results, current_page
    current_page = 1

    text.configure(state="normal")
    text.delete("1.0", "end")
    text.insert("end", "Searching...\n")
    text.configure(state="disabled")

    results = fetch_search_results(query)
    all_ranked_results = rank_results(query, results)

    display_page()


# ---------------- UI SETUP ---------------- #

app = tb.Window(
    title="Search Ranking App",
    themename="flatly",
    size=(980, 700),
    resizable=(True, True)
)

top = tb.Frame(app, padding=15)
top.pack(fill=X)

tb.Label(
    top,
    text="Search",
    font=("Segoe UI", 16, "bold")
).pack(anchor=W)

query_entry = tb.Entry(top, font=("Segoe UI", 12))
query_entry.pack(fill=X, pady=8)
query_entry.bind("<Return>", lambda e: perform_search())

tb.Button(
    top,
    text="Search",
    bootstyle="primary",
    command=perform_search
).pack(anchor=E)

# Results
result_frame = tb.Frame(app, padding=(15, 5))
result_frame.pack(fill=BOTH, expand=True)

result_box = ScrolledText(result_frame, autohide=True)
result_box.pack(fill=BOTH, expand=True)

text = result_box.text
text.configure(state="disabled", wrap="word")

# Styles
text.tag_config(
    "url",
    foreground="#188038",
    font=("Segoe UI", 10)
)

text.tag_config(
    "snippet",
    foreground="#4d5156",
    font=("Segoe UI", 11),
    spacing3=18
)

# Pagination
nav = tb.Frame(app, padding=10)
nav.pack(fill=X)

tb.Button(nav, text="← Prev", bootstyle="secondary", command=prev_page).pack(side=LEFT)
page_label = tb.Label(nav, text="Page 1", font=("Segoe UI", 10))
page_label.pack(side=LEFT, padx=10)
tb.Button(nav, text="Next →", bootstyle="secondary", command=next_page).pack(side=LEFT)

# Run
app.mainloop()
