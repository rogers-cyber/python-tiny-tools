import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List, Tuple, Dict
import io
import json
import os
import requests

from PIL import Image, ImageTk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

# ---------------- CONFIG ---------------- #
RESULTS_PER_PAGE = 6
FAVORITES_FILE = "product_favorites.json"
PRODUCTS_FILE = "products.json"

# ---------------- GLOBAL STATE ---------------- #
all_ranked_products: List[Tuple["Product", float]] = []
current_page = 1
image_cache: Dict[str, ImageTk.PhotoImage] = {}
favorites: List["Product"] = []

# ---------------- DATA STRUCTURE ---------------- #
@dataclass(frozen=True)
class Product:
    name: str
    brand: str
    category: str
    description: str
    price: float
    url: str
    image_url: str = ""

    def text_blob(self, mode: str):
        if mode == "Brand":
            return self.brand
        if mode == "Category":
            return self.category
        return f"{self.name} {self.brand} {self.category} {self.description}"

# ---------------- SAMPLE DATA ---------------- #
def load_products() -> List[Product]:
    if not os.path.exists(PRODUCTS_FILE):
        sample = [
            Product(
                name="Wireless Headphones",
                brand="SoundMax",
                category="Electronics",
                description="Noise cancelling over-ear headphones with deep bass",
                price=129.99,
                url="https://example.com/headphones",
                image_url="https://via.placeholder.com/120x180.png?text=Headphones"
            ),
            Product(
                name="Running Shoes",
                brand="FastStep",
                category="Footwear",
                description="Lightweight running shoes with breathable mesh",
                price=89.99,
                url="https://example.com/shoes",
                image_url="https://via.placeholder.com/120x180.png?text=Shoes"
            ),
            Product(
                name="Smart Watch",
                brand="TimeTech",
                category="Electronics",
                description="Fitness tracking smartwatch with heart rate monitor",
                price=199.99,
                url="https://example.com/watch",
                image_url="https://via.placeholder.com/120x180.png?text=Watch"
            ),
        ]
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump([p.__dict__ for p in sample], f, indent=2)

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return [Product(**p) for p in json.load(f)]

products = load_products()

# ---------------- FAVORITES ---------------- #
def load_favorites():
    global favorites
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            favorites = [Product(**p) for p in json.load(f)]

def save_favorites():
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump([p.__dict__ for p in favorites], f, indent=2)

# ---------------- RECOMMENDATION ENGINE ---------------- #
def recommend_products(query: str, candidates: List[Product], mode: str):
    docs = [p.text_blob(mode) for p in candidates]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs + [query])
    scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
    ranked = list(zip(candidates, scores))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

# ---------------- UI HELPERS ---------------- #
def open_url(url: str):
    webbrowser.open_new_tab(url)

def load_image(url: str, size=(120, 180)):
    if url in image_cache:
        return image_cache[url]
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content)).resize(size)
        photo = ImageTk.PhotoImage(img)
        image_cache[url] = photo
        return photo
    except:
        return None

def add_to_favorites(product: Product):
    if product not in favorites:
        favorites.append(product)
        save_favorites()
        messagebox.showinfo("Saved", "Added to Favorites")

# ---------------- DISPLAY ---------------- #
def insert_product(container, product: Product):
    frame = tk.Frame(container)
    img_label = tk.Label(frame)
    img_label.pack(side=tk.LEFT)

    info = tk.Frame(frame)
    info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    tb.Label(info, text=product.name, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
    tb.Label(info, text=f"{product.brand} | {product.category}", font=("Segoe UI", 9)).pack(anchor=tk.W)
    tb.Label(info, text=f"${product.price:.2f}", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)

    btns = tk.Frame(info)
    btns.pack(anchor=tk.W, pady=3)
    tb.Button(btns, text="★ Favorite", bootstyle="warning",
              command=lambda p=product: add_to_favorites(p)).pack(side=tk.LEFT, padx=2)
    tb.Button(btns, text="↗ View", bootstyle="info",
              command=lambda u=product.url: open_url(u)).pack(side=tk.LEFT, padx=2)

    container.configure(state="normal")
    container.window_create("end", window=frame)
    container.insert("end", "\n\n")
    container.configure(state="disabled")

    # -------------------- Download image in background -------------------- #
    def download_image():
        img = load_image(product.image_url)
        if img:
            # Update widget safely in main thread
            app.after(0, lambda: setattr(img_label, 'image', img) or img_label.configure(image=img))

    threading.Thread(target=download_image, daemon=True).start()

# ---------------- PAGINATION ---------------- #
def display_page():
    text.configure(state="normal")
    text.delete("1.0", "end")
    start = (current_page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    for product, _ in all_ranked_products[start:end]:
        insert_product(text, product)
    text.configure(state="disabled")
    update_pagination()

def next_page():
    global current_page
    if current_page * RESULTS_PER_PAGE < len(all_ranked_products):
        current_page += 1
        display_page()

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        display_page()

def update_pagination():
    total = max(1, (len(all_ranked_products) - 1) // RESULTS_PER_PAGE + 1)
    page_label.config(text=f"Page {current_page} of {total}")

# ---------------- SEARCH ---------------- #
def get_selected_modes():
    selected = [name for name, var in mode_vars.items() if var.get() == 1]
    return selected or ["All"]

def perform_search():
    query = query_entry.get().strip()
    if not query:
        return
    threading.Thread(target=search_thread, args=(query,), daemon=True).start()

def search_thread(query: str):
    modes = get_selected_modes()
    ranked = []
    for mode in modes:
        ranked.extend(recommend_products(query, products, mode))

    ranked.sort(key=lambda x: x[1], reverse=True)
    seen = set()
    final = []
    for p, s in ranked:
        if p.name not in seen:
            seen.add(p.name)
            final.append((p, s))

    def update():
        global all_ranked_products, current_page
        current_page = 1
        all_ranked_products = final
        display_page()

    app.after(0, update)

# ---------------- UI SETUP ---------------- #
app = tb.Window(title="E-Commerce Recommendation System",
                themename="darkly",
                size=(1000, 680))

load_favorites()

top = tb.Frame(app, padding=15)
top.pack(fill=tk.X)

tb.Label(top, text="🛒 Product Recommendation Engine",
         font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)

query_entry = tb.Entry(top, font=("Segoe UI", 13))
query_entry.pack(fill=tk.X, pady=6)
query_entry.bind("<Return>", lambda e: perform_search())

mode_vars = {
    "All": tk.IntVar(value=1),
    "Category": tk.IntVar(value=0),
    "Brand": tk.IntVar(value=0)
}

mode_frame = tb.Frame(top)
mode_frame.pack(fill=tk.X, pady=5)

for name, var in mode_vars.items():
    tb.Checkbutton(mode_frame, text=name, variable=var,
                   bootstyle="info").pack(side=tk.LEFT, padx=5)

tb.Button(mode_frame, text="Search",
          bootstyle="primary",
          command=perform_search).pack(side=tk.LEFT, padx=10)

result_frame = tb.Frame(app)
result_frame.pack(fill=tk.BOTH, expand=True)

result_box = ScrolledText(result_frame)
result_box.pack(fill=tk.BOTH, expand=True)
text = result_box.text
text.configure(state="disabled", wrap="word")

nav = tb.Frame(app, padding=10)
nav.pack()

tb.Button(nav, text="← Prev", command=prev_page).pack(side=tk.LEFT)
page_label = tb.Label(nav, text="Page 1")
page_label.pack(side=tk.LEFT, padx=10)
tb.Button(nav, text="Next →", command=next_page).pack(side=tk.LEFT)

app.mainloop()
