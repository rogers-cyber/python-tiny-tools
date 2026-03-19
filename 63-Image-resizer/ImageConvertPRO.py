import os
import sys
import sqlite3
from threading import Thread
from PIL import Image, ImageTk

try:
    from PIL import ImageResampling
    RESAMPLE = ImageResampling.LANCZOS
except:
    RESAMPLE = Image.LANCZOS

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Listbox, Canvas, Scrollbar
from tkinterdnd2 import TkinterDnD, DND_FILES

# ---------------- APP INFO ----------------
APP_NAME = "ImageConvert PRO"
APP_VERSION = "1.1"

# ---------------- PATH ----------------
BASE_DIR = os.path.dirname(sys.argv[0])
DB_NAME = os.path.join(BASE_DIR, "snapconvert.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "converted")

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY,
        name TEXT,
        original TEXT,
        converted TEXT)""")
    conn.commit()
    conn.close()

def insert_db(name, orig, conv):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO history(name, original, converted) VALUES(?,?,?)",(name,orig,conv))
    conn.commit()
    conn.close()

def fetch_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, original, converted FROM history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def clear_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM history")
    conn.commit()
    conn.close()

# ---------------- ABOUT ----------------
def show_about():
    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME} v{APP_VERSION}\n\n"
        "Professional Image Converter\n\n"
        "© 2026 Mate Technologies\n"
        "https://matetools.gumroad.com"
    )

# ---------------- WORKER ----------------
def worker(images, fmt, out, quality, resize, keep, progress, finish):
    os.makedirs(out, exist_ok=True)
    total = len(images)
    count = 0

    for i, path in enumerate(images):
        try:
            with Image.open(path) as img:
                if resize > 0:
                    img = img.resize((resize, resize), RESAMPLE)

                if fmt == "JPEG" and img.mode in ("RGBA","P"):
                    img = img.convert("RGB")

                name = os.path.splitext(os.path.basename(path))[0]
                if not keep:
                    name += f"_{i+1}"

                out_path = os.path.join(out, f"{name}.{fmt.lower()}")

                c = 1
                while os.path.exists(out_path):
                    out_path = os.path.join(out, f"{name}_{c}.{fmt.lower()}")
                    c += 1

                params = {"quality": quality} if fmt == "JPEG" else {}
                img.save(out_path, fmt, **params)

                insert_db(name, path, out_path)
                count += 1

        except Exception as e:
            print("Error:", e)

        progress(int((i+1)/total*100))

    finish(count)

# ---------------- APP ----------------
class App:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("1200x750")
        self.style = tb.Style("darkly")

        self.images = []
        self.thumbs = []

        self.create_menu()
        self.build_ui()
        self.load_history()

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.drop)

    # MENU
    def create_menu(self):
        menubar = tb.Menu(self.root)
        help_menu = tb.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

    # UI
    def build_ui(self):
        main = tb.Frame(self.root)
        main.pack(fill=BOTH, expand=True)

        # LEFT
        left = tb.Frame(main, width=250, padding=5)
        left.pack(side=LEFT, fill=Y)

        tb.Label(left, text="📂 Files", font=("Arial", 12)).pack(pady=5)

        self.listbox = Listbox(left, bg="#1e1e1e", fg="white")
        self.listbox.pack(fill=BOTH, expand=True, pady=5)

        tb.Button(left, text="Add Images", command=self.add_files, bootstyle=SUCCESS).pack(fill=X, pady=2)
        tb.Button(left, text="Add Folder", command=self.add_folder, bootstyle=INFO).pack(fill=X, pady=2)
        tb.Button(left, text="Remove", command=self.remove_selected, bootstyle=DANGER).pack(fill=X, pady=2)
        tb.Button(left, text="Clear All", command=self.clear_all, bootstyle=SECONDARY).pack(fill=X, pady=2)

        # CENTER
        center = tb.Frame(main, padding=5)
        center.pack(side=LEFT, fill=BOTH, expand=True)

        self.canvas = Canvas(center, bg="#121212")
        self.scroll = Scrollbar(center, command=self.canvas.yview)

        self.inner = tb.Frame(self.canvas)

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scroll.pack(side=RIGHT, fill=Y)

        # RIGHT
        right = tb.Frame(main, width=260, padding=10)
        right.pack(side=RIGHT, fill=Y)

        tb.Label(right, text="⚙ Settings", font=("Arial", 12)).pack(pady=5)

        tb.Label(right, text="Format").pack(anchor="w")
        self.format = tb.Combobox(right, values=["PNG","JPEG","WEBP","BMP","TIFF"])
        self.format.current(0)
        self.format.pack(fill=X, pady=5)

        tb.Label(right, text="JPEG Quality").pack(anchor="w")
        self.quality = tb.Spinbox(right, from_=10, to=100)
        self.quality.set(90)
        self.quality.pack(fill=X, pady=5)

        tb.Label(right, text="Resize (px)").pack(anchor="w")
        self.resize = tb.Spinbox(right, from_=0, to=5000)
        self.resize.set(0)
        self.resize.pack(fill=X, pady=5)

        self.keep = tb.Checkbutton(right, text="Keep original filename")
        self.keep.invoke()
        self.keep.pack(pady=5)

        tb.Separator(right).pack(fill=X, pady=10)

        tb.Button(right, text="🚀 Convert", command=self.convert, bootstyle=WARNING).pack(fill=X, pady=5)

        self.progress = tb.Progressbar(right)
        self.progress.pack(fill=X, pady=5)

        self.status = tb.Label(right, text="Ready")
        self.status.pack(pady=5)

        tb.Separator(right).pack(fill=X, pady=10)

        tb.Button(right, text="🧹 Delete History", command=self.delete_history, bootstyle=DANGER).pack(fill=X, pady=5)

        # HISTORY TABLE
        self.table = tb.Treeview(self.root, columns=("n","o","c"), show="headings")
        self.table.heading("n", text="Name")
        self.table.heading("o", text="Original")
        self.table.heading("c", text="Converted")
        self.table.pack(fill=BOTH, expand=True)

    # FUNCTIONS
    def drop(self, e):
        self.add_images(self.root.tk.splitlist(e.data))

    def add_files(self):
        self.add_images(filedialog.askopenfilenames())

    def add_folder(self):
        folder = filedialog.askdirectory()
        imgs = []
        for r,_,f in os.walk(folder):
            for x in f:
                if x.lower().endswith(("png","jpg","jpeg","bmp","gif")):
                    imgs.append(os.path.join(r,x))
        self.add_images(imgs)

    def add_images(self, paths):
        for p in paths:
            if p not in self.images:
                self.images.append(p)
                self.listbox.insert(END, os.path.basename(p))
        self.render_gallery()

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        sel.reverse()
        for i in sel:
            self.images.pop(i)
            self.listbox.delete(i)
        self.render_gallery()

    def clear_all(self):
        self.images = []
        self.listbox.delete(0, END)
        for w in self.inner.winfo_children():
            w.destroy()

    def render_gallery(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.thumbs.clear()

        cols = 4
        for i, path in enumerate(self.images[:50]):
            try:
                img = Image.open(path)
                img.thumbnail((150,150))
                tkimg = ImageTk.PhotoImage(img)
                self.thumbs.append(tkimg)

                frame = tb.Frame(self.inner)
                frame.grid(row=i//cols, column=i%cols, padx=10, pady=10)

                tb.Label(frame, image=tkimg).pack()
                tb.Label(frame, text=os.path.basename(path), wraplength=140).pack()
            except:
                pass

    def convert(self):
        if not self.images:
            messagebox.showwarning("No images", "Add images first")
            return

        fmt = self.format.get()
        q = int(self.quality.get())
        r = int(self.resize.get())
        keep = self.keep.instate(["selected"])

        def prog(v):
            self.root.after(0, lambda: (
                self.progress.config(value=v),
                self.status.config(text=f"{v}%")
            ))

        def done(c):
            self.root.after(0, lambda: (
                self.status.config(text=f"Done: {c} images"),
                self.progress.config(value=0),
                self.load_history()
            ))

        Thread(target=worker, args=(self.images,fmt,OUTPUT_DIR,q,r,keep,prog,done), daemon=True).start()

    def delete_history(self):
        if messagebox.askyesno("Confirm", "Delete all history?"):
            clear_history()
            self.load_history()

    def load_history(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for row in fetch_db():
            self.table.insert("",END,values=row)

    def run(self):
        self.root.mainloop()

# RUN
if __name__ == "__main__":
    init_db()
    App().run()
