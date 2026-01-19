import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from tkinter import ttk  # For Combobox
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import numpy as np
import random
import time 

# =========================
# UTILITY FUNCTIONS
# =========================
def add_noise(img, intensity=10):
    """Add random noise to an image."""
    arr = np.array(img)
    noise = np.random.randint(-intensity, intensity + 1, arr.shape, "int16")
    noisy = np.clip(arr + noise, 0, 255).astype("uint8")
    return Image.fromarray(noisy)

def generate_gradient(size):
    """Generate a simple vertical gradient with optional noise."""
    w, h = size
    top_color = (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255)
    )
    bottom_color = (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255)
    )
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line((0, y, w, y), fill=(r, g, b))
    return add_noise(img, intensity=5)

def generate_texture(size):
    """Generate a random texture overlay."""
    img = Image.new("RGBA", size)
    draw = ImageDraw.Draw(img)
    for _ in range(size[0] * size[1] // 50):
        x = random.randint(0, size[0] - 1)
        y = random.randint(0, size[1] - 1)
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(20, 50)
        )
        draw.point((x, y), fill=color)
    return img

def generate_background(size):
    """Combine gradient and texture to produce the final background."""
    base = generate_gradient(size)
    texture = generate_texture(size)
    base.paste(texture, (0, 0), texture)
    return base

# =========================
# MAIN APP CLASS
# =========================
class BackgroundGenerator:
    def __init__(self, root):
        self.root = root
        root.title("Background Generator Tool")
        root.geometry("1200x700")
        root.resizable(True, True)

        self.resolutions = {
            "HD (1280x720)": (1280, 720),
            "Full HD (1920x1080)": (1920, 1080),
            "2K (2560x1440)": (2560, 1440),
            "4K (3840x2160)": (3840, 2160),
            "Ultra HD (6000x3375)": (6000, 3375)
        }

        self.state = {
            "size": (1920, 1080),
            "bg": generate_background((1920, 1080))
        }

        # LEFT PANEL
        left = tb.Frame(root, width=300, bootstyle="secondary")
        left.pack(side="left", fill="y", padx=10, pady=10)

        # Orientation Selector
        tb.Label(left, text="Orientation:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 2))
        self.orient_combo = ttk.Combobox(left, values=["Landscape", "Portrait"], state="readonly")
        self.orient_combo.current(0)  # Default to Landscape
        self.orient_combo.pack(fill=X, pady=(0, 10))

        # Resolution Selector
        tb.Label(left, text="Export Resolution:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 2))
        self.res_var = tb.StringVar(value="Full HD (1920x1080)")
        tb.OptionMenu(left, self.res_var, *self.resolutions.keys(), bootstyle="secondary").pack(fill=X, pady=(0, 10))

        # Buttons
        tb.Button(left, text="🔄 Generate Background", bootstyle=INFO, command=self.generate_bg).pack(fill=X, pady=5)
        tb.Button(left, text="💾 Export", bootstyle=SUCCESS, command=self.save_bg).pack(fill=X, pady=5)

        # RIGHT PANEL - Canvas Preview
        self.canvas_frame = tb.Frame(root)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.canvas = tb.Canvas(self.canvas_frame, bg="black", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas_frame.bind("<Configure>", self.on_resize)

        self.update_preview()

    # =========================
    # EVENT METHODS
    # =========================
    def on_resize(self, event):
        self.update_preview()

    # =========================
    # STATE HANDLERS
    # =========================
    def generate_bg(self):
        w, h = self.resolutions.get(self.res_var.get(), (1920, 1080))
        orientation = self.orient_combo.get()
        if orientation == "Portrait":
            w, h = h, w
        self.state["size"] = (w, h)
        self.state["bg"] = generate_background((w, h))
        self.update_preview()

    def update_preview(self):
        img = self.state["bg"].copy()
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w > 0 and canvas_h > 0:
            img_w, img_h = img.size
            ratio = min(canvas_w / img_w, canvas_h / img_h)
            new_w = max(1, int(img_w * ratio))
            new_h = max(1, int(img_h * ratio))
            preview = img.resize((new_w, new_h))
            self.tk_img = ImageTk.PhotoImage(preview)
            self.canvas.delete("all")
            self.canvas.create_image(canvas_w // 2, canvas_h // 2, image=self.tk_img)

    def save_bg(self):
        # Get current background info
        w, h = self.state["size"]
        orientation = self.orient_combo.get()
        
        # Generate automatic filename
        timestamp = int(time.time())  # simple timestamp
        filename = f"background_{w}x{h}_{orientation}_{timestamp}.png"

        # Ask user where to save, default filename pre-filled
        f = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")]
        )

        if f:
            ext = f.split('.')[-1].lower()
            if ext in ["jpg", "jpeg"]:
                self.state["bg"].save(f, quality=85)
            else:
                self.state["bg"].save(f, optimize=True)
            messagebox.showinfo("Success", f"Background saved as {f}!")

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = BackgroundGenerator(root)
    root.mainloop()
