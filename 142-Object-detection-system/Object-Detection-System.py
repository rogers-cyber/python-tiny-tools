import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Initialize YOLO model
model = YOLO("yolov8n.pt")  # YOLOv8 Nano model

class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Object Detection System")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # ttkbootstrap style
        self.style = tb.Style("superhero")

        # Frame for buttons
        self.frame = tb.Frame(root)
        self.frame.pack(side=TOP, pady=10)

        self.load_btn = tb.Button(self.frame, text="Load Image", bootstyle=PRIMARY, command=self.load_image)
        self.load_btn.grid(row=0, column=0, padx=10)

        self.detect_btn = tb.Button(self.frame, text="Detect Objects", bootstyle=SUCCESS, command=self.detect_objects)
        self.detect_btn.grid(row=0, column=1, padx=10)

        # Label to display images
        self.image_label = tb.Label(root)
        self.image_label.pack(pady=10)

        self.img_path = None
        self.display_img = None

    def load_image(self):
        self.img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.img_path:
            img = Image.open(self.img_path)
            # Pillow 10+ compatible resize
            img = img.resize((800, 500), Image.Resampling.LANCZOS)
            self.display_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.display_img)

    def detect_objects(self):
        if not self.img_path:
            messagebox.showwarning("Warning", "Please load an image first!")
            return

        # Run YOLO detection
        results = model(self.img_path)[0]

        # Load image with OpenCV
        img_cv = cv2.imread(self.img_path)

        # Draw bounding boxes
        for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
            x1, y1, x2, y2 = map(int, box)
            label = f"{model.names[int(cls)]} {conf:.2f}"
            cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_cv, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert BGR to RGB for Tkinter
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil = img_pil.resize((800, 500), Image.Resampling.LANCZOS)
        self.display_img = ImageTk.PhotoImage(img_pil)
        self.image_label.config(image=self.display_img)


if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = ObjectDetectionApp(root)
    root.mainloop()
