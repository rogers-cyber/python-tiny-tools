"""
LaptopPricePredictor v1.0 - Desktop Edition
Predict laptop prices based on specs in a simple UI
Supports CPU, RAM, GPU, storage, and brand selection
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ---------------------- MOCK MODEL ----------------------
# Replace this with a real ML model later
def predict_price(specs):
    base_price = 300
    cpu_factor = {"i3": 100, "i5": 200, "i7": 350, "Ryzen 3": 90, "Ryzen 5": 180, "Ryzen 7": 320}
    ram_factor = {4: 50, 8: 100, 16: 200, 32: 350}
    storage_factor = {"HDD": 50, "SSD": 150, "Hybrid": 100}
    gpu_factor = {"Integrated": 0, "GTX 1650": 200, "RTX 3050": 350, "RTX 4070": 600}
    brand_factor = {"Dell": 100, "HP": 80, "Lenovo": 70, "Asus": 90, "Apple": 400}

    price = base_price
    price += cpu_factor.get(specs["CPU"], 0)
    price += ram_factor.get(specs["RAM"], 0)
    price += storage_factor.get(specs["Storage"], 0)
    price += gpu_factor.get(specs["GPU"], 0)
    price += brand_factor.get(specs["Brand"], 0)
    return price

# ---------------------- MAIN APP ----------------------
class LaptopPriceApp:
    APP_NAME = "LaptopPricePredictor"
    APP_VERSION = "1.0"

    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.geometry("600x550")

        self._build_ui()
        self._apply_styles()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        main = tb.Frame(self.root, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        tb.Label(main, text="💻 Laptop Price Predictor", font=("Segoe UI", 20, "bold")).pack(pady=(0,10))
        tb.Label(main, text="Enter your laptop specs below:", font=("Segoe UI", 10, "italic"), foreground="#9ca3af").pack(pady=(0,20))

        # Brand
        tb.Label(main, text="Brand").pack(anchor=W)
        self.brand_combo = tb.Combobox(main, values=["Dell","HP","Lenovo","Asus","Apple"])
        self.brand_combo.pack(fill=X, pady=(0,10))
        self.brand_combo.set("Dell")

        # CPU
        tb.Label(main, text="CPU").pack(anchor=W)
        self.cpu_combo = tb.Combobox(main, values=["i3","i5","i7","Ryzen 3","Ryzen 5","Ryzen 7"])
        self.cpu_combo.pack(fill=X, pady=(0,10))
        self.cpu_combo.set("i5")

        # RAM
        tb.Label(main, text="RAM (GB)").pack(anchor=W)
        self.ram_combo = tb.Combobox(main, values=[4,8,16,32])
        self.ram_combo.pack(fill=X, pady=(0,10))
        self.ram_combo.set(8)

        # Storage
        tb.Label(main, text="Storage Type").pack(anchor=W)
        self.storage_combo = tb.Combobox(main, values=["HDD","SSD","Hybrid"])
        self.storage_combo.pack(fill=X, pady=(0,10))
        self.storage_combo.set("SSD")

        # GPU
        tb.Label(main, text="GPU").pack(anchor=W)
        self.gpu_combo = tb.Combobox(main, values=["Integrated","GTX 1650","RTX 3050","RTX 4070"])
        self.gpu_combo.pack(fill=X, pady=(0,20))
        self.gpu_combo.set("Integrated")

        # Predict button
        self.predict_btn = tb.Button(main, text="💰 Predict Price", bootstyle=SUCCESS, command=self.predict)
        self.predict_btn.pack(pady=(0,10))

        # Result label
        self.result_label = tb.Label(main, text="", font=("Segoe UI", 16, "bold"))
        self.result_label.pack(pady=(10,0))

    # ---------------------- Actions ----------------------
    def predict(self):
        specs = {
            "Brand": self.brand_combo.get(),
            "CPU": self.cpu_combo.get(),
            "RAM": int(self.ram_combo.get()),
            "Storage": self.storage_combo.get(),
            "GPU": self.gpu_combo.get()
        }
        price = predict_price(specs)
        self.result_label.config(text=f"Estimated Price: ${price}")

    # ---------------------- Styles ----------------------
    def _apply_styles(self):

        self.root.style.configure("TButton", font=("Segoe UI", 12))

    # ---------------------- Run ----------------------
    def run(self):
        self.root.mainloop()


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app = LaptopPriceApp()
    app.run()
