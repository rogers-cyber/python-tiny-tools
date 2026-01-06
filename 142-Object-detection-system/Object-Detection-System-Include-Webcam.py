import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from collections import Counter

# Initialize YOLO model
model = YOLO("yolov8n.pt")  # YOLOv8 Nano model

class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Object Detection System")
        self.root.geometry("1000x750")
        self.root.resizable(False, False)

        # ttkbootstrap style
        self.style = tb.Style("superhero")

        # ---------------- Top Frame ----------------
        self.top_frame = tb.Frame(root)
        self.top_frame.pack(side=TOP, pady=10)

        # Buttons
        self.load_btn = tb.Button(self.top_frame, text="Load Image", bootstyle=PRIMARY, command=self.load_image)
        self.load_btn.grid(row=0, column=0, padx=5)

        self.detect_btn = tb.Button(self.top_frame, text="Detect Image", bootstyle=SUCCESS, command=self.detect_objects)
        self.detect_btn.grid(row=0, column=1, padx=5)

        self.start_cam_btn = tb.Button(self.top_frame, text="Start Webcam", bootstyle=INFO, command=self.start_webcam)
        self.start_cam_btn.grid(row=0, column=2, padx=5)

        self.stop_cam_btn = tb.Button(self.top_frame, text="Stop Webcam", bootstyle=DANGER, command=self.stop_webcam)
        self.stop_cam_btn.grid(row=0, column=3, padx=5)

        self.save_snapshot_btn = tb.Button(self.top_frame, text="Save Snapshot", bootstyle=WARNING, command=self.save_snapshot)
        self.save_snapshot_btn.grid(row=0, column=4, padx=5)

        # ---------------- Confidence Slider ----------------
        self.conf_label = tb.Label(self.top_frame, text="Confidence Threshold: 0.25")
        self.conf_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Fixed ttkbootstrap scale (remove increment)
        self.conf_slider = tb.Scale(
            self.top_frame,
            from_=0.0,
            to=1.0,
            bootstyle=INFO,
            orient=tk.HORIZONTAL,
            command=self.update_conf_label
        )
        self.conf_slider.set(0.25)
        self.conf_slider.grid(row=1, column=2, columnspan=3, sticky="we", padx=5)

        # ---------------- Image Frame ----------------
        self.image_label = tb.Label(root)
        self.image_label.pack(pady=10)

        # ---------------- Class Counts Frame ----------------
        self.counts_label = tb.Label(root, text="Detected Objects: None", font=("Arial", 12))
        self.counts_label.pack(pady=5)

        # ---------------- Variables ----------------
        self.img_path = None
        self.display_img = None
        self.cap = None
        self.webcam_running = False
        self.current_frame = None
        self.conf_threshold = 0.25

    # ---------------- Update Confidence Label ----------------
    def update_conf_label(self, val):
        self.conf_threshold = round(float(val), 2)
        self.conf_label.config(text=f"Confidence Threshold: {self.conf_threshold:.2f}")

    # ---------------- Load Image ----------------
    def load_image(self):
        self.img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.img_path:
            img = Image.open(self.img_path)
            img = img.resize((800, 500), Image.Resampling.LANCZOS)
            self.display_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.display_img)

    # ---------------- Detect Image ----------------
    def detect_objects(self):
        if not self.img_path:
            messagebox.showwarning("Warning", "Please load an image first!")
            return

        results = model(self.img_path)[0]

        img_cv = cv2.imread(self.img_path)
        detected_classes = []

        for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
            if conf < self.conf_threshold:
                continue
            x1, y1, x2, y2 = map(int, box)
            label = f"{model.names[int(cls)]} {conf:.2f}"
            detected_classes.append(model.names[int(cls)])
            cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_cv, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Update class counts
        self.update_class_counts(detected_classes)

        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil = img_pil.resize((800, 500), Image.Resampling.LANCZOS)
        self.display_img = ImageTk.PhotoImage(img_pil)
        self.image_label.config(image=self.display_img)

    # ---------------- Start Webcam ----------------
    def start_webcam(self):
        if self.webcam_running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot open webcam")
            return
        self.webcam_running = True
        self.update_webcam_frame()

    # ---------------- Stop Webcam ----------------
    def stop_webcam(self):
        self.webcam_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.counts_label.config(text="Detected Objects: None")

    # ---------------- Update Webcam Frame ----------------
    def update_webcam_frame(self):
        if not self.webcam_running:
            return
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            results = model(frame)[0]
            detected_classes = []

            for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
                if conf < self.conf_threshold:
                    continue
                x1, y1, x2, y2 = map(int, box)
                label = f"{model.names[int(cls)]} {conf:.2f}"
                detected_classes.append(model.names[int(cls)])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Update class counts
            self.update_class_counts(detected_classes)

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_pil = img_pil.resize((800, 500), Image.Resampling.LANCZOS)
            self.display_img = ImageTk.PhotoImage(img_pil)
            self.image_label.config(image=self.display_img)

        self.root.after(30, self.update_webcam_frame)  # ~33 FPS

    # ---------------- Update Class Counts ----------------
    def update_class_counts(self, detected_classes):
        if detected_classes:
            counts = Counter(detected_classes)
            counts_str = ", ".join([f"{cls}: {cnt}" for cls, cnt in counts.items()])
        else:
            counts_str = "None"
        self.counts_label.config(text=f"Detected Objects: {counts_str}")

    # ---------------- Save Snapshot ----------------
    def save_snapshot(self):
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No frame available to save!")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"),
                                                            ("PNG files", "*.png")])
        if save_path:
            frame = self.current_frame.copy()
            results = model(frame)[0]
            for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
                if conf < self.conf_threshold:
                    continue
                x1, y1, x2, y2 = map(int, box)
                label = f"{model.names[int(cls)]} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imwrite(save_path, frame)
            messagebox.showinfo("Saved", f"Snapshot saved to {save_path}")


# ---------------- Main ----------------
if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = ObjectDetectionApp(root)
    root.mainloop()
