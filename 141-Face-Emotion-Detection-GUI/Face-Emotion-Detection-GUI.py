import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tensorflow.keras.models import load_model
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tensorflow as tf
import datetime

# ---------------- GPU CHECK ----------------
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)

# ---------------- EMOTION MODEL ----------------
emotion_labels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
model = load_model("fer2013_mini_XCEPTION.102-0.66.hdf5", compile=False)

# ---------------- FACE DETECTOR ----------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

class EmotionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Face Emotion Detection")
        self.root.geometry("1100x850")
        self.root.resizable(False, False)

        tb.Style("superhero")

        # ---------------- Controls ----------------
        control = tb.Frame(root)
        control.pack(pady=10)

        tb.Button(control, text="Start Webcam", bootstyle=SUCCESS, command=self.start).grid(row=0, column=0, padx=5)
        tb.Button(control, text="Stop Webcam", bootstyle=DANGER, command=self.stop).grid(row=0, column=1, padx=5)
        tb.Button(control, text="Save Screenshot", bootstyle=WARNING, command=self.save_snapshot).grid(row=0, column=2, padx=5)

        # ---------------- Labels ----------------
        self.emotion_label = tb.Label(root, text="Emotion: None", font=("Arial", 16))
        self.emotion_label.pack()

        # ---------------- Confidence Bar ----------------
        self.conf_bar = tb.Progressbar(root, length=400, bootstyle=SUCCESS)
        self.conf_bar.pack(pady=5)

        # ---------------- Video ----------------
        self.video_label = tb.Label(root)
        self.video_label.pack(pady=10)

        # ---------------- Emotion History Graph ----------------
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.ax.set_ylim(0, 1)
        self.ax.set_title("Emotion Confidence History")
        self.line, = self.ax.plot([], [])

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.history = deque(maxlen=50)

        # ---------------- Variables ----------------
        self.cap = None
        self.running = False
        self.last_frame = None

    # ---------------- Start ----------------
    def start(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Webcam not accessible")
            return
        self.running = True
        self.update()

    # ---------------- Stop ----------------
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image="")
        self.emotion_label.config(text="Emotion: None")
        self.conf_bar["value"] = 0

    # ---------------- Update Frame ----------------
    def update(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        self.last_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (48, 48))
            face = face / 255.0
            face = np.reshape(face, (1, 48, 48, 1))

            preds = model.predict(face, verbose=0)[0]
            idx = np.argmax(preds)
            emotion = emotion_labels[idx]
            confidence = preds[idx]

            self.emotion_label.config(text=f"Emotion: {emotion}")
            self.conf_bar["value"] = confidence * 100

            self.history.append(confidence)
            self.line.set_data(range(len(self.history)), list(self.history))
            self.ax.set_xlim(0, 50)
            self.canvas.draw()

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, f"{emotion} ({confidence:.2f})",
                        (x,y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0,255,0), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((800, 500), Image.Resampling.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.root.after(30, self.update)

    # ---------------- Save Snapshot ----------------
    def save_snapshot(self):
        if self.last_frame is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
        )
        if path:
            cv2.imwrite(path, self.last_frame)
            messagebox.showinfo("Saved", f"Snapshot saved:\n{path}")

# ---------------- Main ----------------
if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    EmotionApp(root)
    root.mainloop()
