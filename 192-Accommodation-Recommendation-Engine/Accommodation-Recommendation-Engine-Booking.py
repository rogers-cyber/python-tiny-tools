import threading
import requests
import webbrowser
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List, Dict
import io
import json
import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText
from PIL import Image, ImageTk

# ---------------- CONFIG ---------------- #
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
AFFILIATE_ID = "YOUR_AFFILIATE_ID"
API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://demandapi.booking.com/3.1"
RESULTS_PER_PAGE = 6
FAVORITES_FILE = "accommodation_favorites.json"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}",
    "X-Affiliate-Id": str(AFFILIATE_ID)
}

# ---------------- IMAGE CACHE ---------------- #
cover_cache: Dict[str, ImageTk.PhotoImage] = {}

def load_cover(url: str, size=(120, 80)):
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

# ---------------- DATA STRUCTURE ---------------- #
@dataclass
class Accommodation:
    name: str
    city: str
    price: float
    rating: float
    url: str
    image_url: str = ""  # for preview images

# ---------------- ENGINE ---------------- #
class AccommodationEngine:
    def __init__(self):
        self.results: List[Accommodation] = []
        self.current_page = 1
        self.favorites: List[Accommodation] = []
        self.selected_latlng = (None, None)
        self.load_favorites()
        self.build_ui()

    # ---------------- FAVORITES ---------------- #
    def load_favorites(self):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                self.favorites = [Accommodation(**a) for a in json.load(f)]
        except FileNotFoundError:
            self.favorites = []

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump([a.__dict__ for a in self.favorites], f, indent=2)

    def add_to_favorites(self, acc: Accommodation):
        if acc not in self.favorites:
            self.favorites.append(acc)
            self.save_favorites()
            messagebox.showinfo("Saved", f"Added {acc.name} to Favorites")

    # ---------------- GOOGLE PLACES AUTOCOMPLETE ---------------- #
    def autocomplete_city(self, query: str):
        url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {"input": query, "types": "(cities)", "key": GOOGLE_API_KEY}
        r = requests.get(url, params=params)
        return r.json().get("predictions", [])

    def get_city_location(self, place_id: str):
        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {"place_id": place_id, "fields": "geometry", "key": GOOGLE_API_KEY}
        r = requests.get(url, params=params)
        geom = r.json().get("result", {}).get("geometry", {})
        loc = geom.get("location", {})
        return loc.get("lat"), loc.get("lng")

    # ---------------- BOOKING.COM SEARCH ---------------- #
    def fetch_accommodations(self, lat, lng, radius, min_price, max_price, min_rating, amenities, room_types):
        body = {
            "geo": {"lat": lat, "lng": lng, "radius": radius},
            "currency": "USD",
            "guests": {"number_of_adults": 2, "number_of_rooms": 1},
            "price": {"minimum": min_price, "maximum": max_price},
            "rating": {"minimum_review_score": min_rating},
            "accommodation_types": room_types,
            "room_facilities": amenities,
            "rows": 100,
            "extras": ["extra_charges", "products"]
        }
        r = requests.post(f"{BASE_URL}/accommodations/search", headers=HEADERS, json=body)
        data = r.json().get("data", [])
        results = []
        for item in data:
            try:
                name = item.get("name")
                city = item.get("address", {}).get("city_name", "")
                price = float(item.get("price", {}).get("total", 0))
                rating = float(item.get("review_score", 0))
                url = item.get("url")
                image_url = item.get("photo_main", "")
                results.append(Accommodation(name, city, price, rating, url, image_url))
            except:
                continue
        return results

    # ---------------- UI ---------------- #
    def build_ui(self):
        self.app = tb.Window(title="Accommodation Engine", themename="darkly", size=(1000, 700))

        top = tb.Frame(self.app, padding=15)
        top.pack(fill=tk.X)

        tb.Label(top, text="🏨 Accommodation Finder", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)

        # City search with autocomplete
        self.city_var = tk.StringVar()
        city_entry = tb.Entry(top, textvariable=self.city_var, font=("Segoe UI", 13))
        city_entry.pack(fill=tk.X, pady=4)
        city_entry.bind("<KeyRelease>", self.on_city_key)

        self.city_suggestions = tk.Listbox(top, height=5)
        self.city_suggestions.pack(fill=tk.X)
        self.city_suggestions.bind("<<ListboxSelect>>", self.on_city_select)

        # Distance radius slider
        tb.Label(top, text="Distance Radius (km)").pack(anchor=tk.W)
        self.radius_var = tk.DoubleVar(value=5)
        tb.Scale(top, from_=1, to=50, variable=self.radius_var, orient="horizontal").pack(fill=tk.X, pady=2)

        # Filters
        filter_frame = tb.Frame(top)
        filter_frame.pack(fill=tk.X)
        self.min_price = tk.StringVar(value="0")
        self.max_price = tk.StringVar(value="1000")
        self.min_rating = tk.StringVar(value="0")
        tb.Entry(filter_frame, textvariable=self.min_price, width=8).pack(side=tk.LEFT, padx=2)
        tb.Entry(filter_frame, textvariable=self.max_price, width=8).pack(side=tk.LEFT, padx=2)
        tb.Entry(filter_frame, textvariable=self.min_rating, width=8).pack(side=tk.LEFT, padx=2)
        tb.Label(filter_frame, text="MinPrice  MaxPrice  MinRating").pack(side=tk.LEFT, padx=5)

        # Amenity checkboxes
        amenity_frame = tb.LabelFrame(top, text="Amenities")
        amenity_frame.pack(fill=tk.X, pady=2)
        self.amenity_vars = {}
        amenities = ["Pool", "Wifi", "Parking", "Gym"]
        for a in amenities:
            var = tk.IntVar()
            self.amenity_vars[a] = var
            tb.Checkbutton(amenity_frame, text=a, variable=var).pack(side=tk.LEFT, padx=5)

        # Room type checkboxes
        room_frame = tb.LabelFrame(top, text="Room Types")
        room_frame.pack(fill=tk.X, pady=2)
        self.room_vars = {}
        room_types = ["Hotel", "Apartment", "Villa", "B&B"]
        for r in room_types:
            var = tk.IntVar()
            self.room_vars[r] = var
            tb.Checkbutton(room_frame, text=r, variable=var).pack(side=tk.LEFT, padx=5)

        tb.Button(top, text="Search", bootstyle="primary", command=self.perform_search).pack(pady=6)

        # Results
        result_frame = tb.Frame(self.app)
        result_frame.pack(fill=tk.BOTH, expand=True)
        self.result_box = ScrolledText(result_frame)
        self.result_box.pack(fill=tk.BOTH, expand=True)
        self.text = self.result_box.text
        self.text.configure(state="disabled", wrap="word")

        # Pagination & favorites
        nav = tb.Frame(self.app)
        nav.pack(fill=tk.X)
        tb.Button(nav, text="← Prev", command=self.prev_page).pack(side=tk.LEFT)
        self.page_label = tb.Label(nav, text="Page 1"); self.page_label.pack(side=tk.LEFT, padx=10)
        tb.Button(nav, text="Next →", command=self.next_page).pack(side=tk.LEFT)
        tb.Button(nav, text="Favorites", bootstyle="success", command=self.show_favorites).pack(side=tk.RIGHT)

        self.app.mainloop()

    # ---------------- CITY AUTOCOMPLETE EVENTS ---------------- #
    def on_city_key(self, event):
        query = self.city_var.get()
        if len(query) < 2:
            return
        suggestions = self.autocomplete_city(query)
        self.city_suggestions.delete(0, tk.END)
        for s in suggestions:
            self.city_suggestions.insert(tk.END, f"{s['description']}||{s['place_id']}")

    def on_city_select(self, event):
        sel = self.city_suggestions.curselection()
        if sel:
            val = self.city_suggestions.get(sel[0])
            desc, pid = val.split("||")
            self.city_var.set(desc)
            lat, lng = self.get_city_location(pid)
            self.selected_latlng = (lat, lng)
            self.city_suggestions.delete(0, tk.END)

    # ---------------- SEARCH ---------------- #
    def perform_search(self):
        if not self.selected_latlng[0]:
            messagebox.showerror("Error", "Select a city from suggestions")
            return
        lat, lng = self.selected_latlng
        radius = self.radius_var.get()
        min_p = float(self.min_price.get())
        max_p = float(self.max_price.get())
        min_r = float(self.min_rating.get())
        amenities = [i for i, v in self.amenity_vars.items() if v.get() == 1]
        room_types = [i for i, v in self.room_vars.items() if v.get() == 1]

        threading.Thread(target=self.search_thread,
                         args=(lat, lng, radius, min_p, max_p, min_r, amenities, room_types), daemon=True).start()

    def search_thread(self, lat, lng, radius, min_p, max_p, min_r, amenities, room_types):
        self.results = self.fetch_accommodations(lat, lng, radius, min_p, max_p, min_r, amenities, room_types)
        self.current_page = 1
        self.display_page()

    # ---------------- DISPLAY WITH IMAGE ---------------- #
    def display_page(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        start = (self.current_page - 1) * RESULTS_PER_PAGE
        end = start + RESULTS_PER_PAGE
        for acc in self.results[start:end]:
            self.insert_accommodation(self.text, acc)
        self.text.configure(state="disabled")
        self.page_label.config(text=f"Page {self.current_page}")

    def insert_accommodation(self, container_widget, acc: Accommodation):
        frame = tk.Frame(container_widget)
        art_label = tk.Label(frame)
        art_label.pack(side=tk.LEFT, padx=5, pady=5)

        info_frame = tk.Frame(frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tb.Label(info_frame, text=f"{acc.name}", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        tb.Label(info_frame, text=f"{acc.city} | ${acc.price} ⭐ {acc.rating}", font=("Segoe UI", 9)).pack(anchor=tk.W)
        
        btn_frame = tk.Frame(info_frame)
        btn_frame.pack(anchor=tk.W, pady=2)
        tb.Button(btn_frame, text="★ Favorite", bootstyle="warning", command=lambda a=acc: self.add_to_favorites(a)).pack(side=tk.LEFT, padx=2)
        tb.Button(btn_frame, text="↗ Open", bootstyle="info", command=lambda u=acc.url: webbrowser.open_new_tab(u)).pack(side=tk.LEFT, padx=2)

        container_widget.configure(state="normal")
        container_widget.window_create("end", window=frame)
        container_widget.insert("end", "\n\n")
        container_widget.configure(state="disabled")

        # Async image loading
        def load_cover_async():
            img = load_cover(acc.image_url)
            if img:
                def set_img():
                    if art_label.winfo_exists():
                        art_label.configure(image=img)
                        art_label.image = img
                container_widget.after(0, set_img)
        threading.Thread(target=load_cover_async, daemon=True).start()

    # ---------------- PAGINATION ---------------- #
    def next_page(self):
        if self.current_page * RESULTS_PER_PAGE < len(self.results):
            self.current_page += 1
            self.display_page()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()

    # ---------------- FAVORITES ---------------- #
    def show_favorites(self):
        fav_win = tb.Toplevel(self.app)
        fav_win.title("Favorites")
        fav_win.geometry("700x500")
        fav_text = ScrolledText(fav_win)
        fav_text.pack(fill=tk.BOTH, expand=True)
        for a in self.favorites:
            self.insert_accommodation(fav_text.text, a)
        fav_text.text.configure(state="disabled")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    AccommodationEngine()
