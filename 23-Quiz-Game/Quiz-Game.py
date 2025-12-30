import tkinter as tk
from tkinter import ttk
import threading
import random
import winsound  # Windows; replace with playsound for Mac/Linux

# ====================
# Quiz Data
# ====================
quiz_categories = {
    "General Knowledge": [
        {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"], "answer": "Paris"},
        {"question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Mars"}
    ],
    "Literature": [
        {"question": "Who wrote 'Romeo and Juliet'?", "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"], "answer": "William Shakespeare"},
        {"question": "Which novel begins with 'Call me Ishmael'?", "options": ["Moby Dick", "1984", "Great Expectations", "The Odyssey"], "answer": "Moby Dick"}
    ]
}

# ====================
# Main Game Class
# ====================
class MiniGameShow:
    def __init__(self, root):
        self.root = root
        self.root.title("🎉 Mini Game Show 🎉")
        self.root.geometry("800x700")
        self.root.resizable(False, False)  # Disable resizing
        self.root.configure(bg="#1E1E2F")

        self.score = 0
        self.current_question = 0
        self.selected_category = None
        self.questions = []
        self.time_left = 15
        self.timer_running = False
        self.animating = False

        self.create_category_screen()

    # --------------------
    # Category Selection
    # --------------------
    def create_category_screen(self):
        self.stop_animations()
        self.clear_screen()
        title = tk.Label(self.root, text="Choose Your Category", font=("Helvetica", 28, "bold"), fg="#FFD700", bg="#1E1E2F")
        title.pack(pady=50)
        for category in quiz_categories:
            btn = tk.Button(self.root, text=category, font=("Helvetica", 20), width=25, bg="#4B0082", fg="white",
                            command=lambda c=category: self.start_quiz(c))
            btn.pack(pady=15)

    # --------------------
    # Start Quiz
    # --------------------
    def start_quiz(self, category):
        self.selected_category = category
        self.questions = quiz_categories[category]
        self.current_question = 0
        self.score = 0
        self.show_question()

    # --------------------
    # Show Question
    # --------------------
    def show_question(self):
        if self.current_question >= len(self.questions):
            self.show_result()
            return

        self.stop_animations()
        self.clear_screen()
        self.time_left = 15
        self.timer_running = True
        question_data = self.questions[self.current_question]

        # Question label
        self.question_label = tk.Label(self.root, text=question_data["question"], font=("Helvetica", 22, "bold"),
                                       fg="#00FFFF", bg="#1E1E2F", wraplength=750)
        self.question_label.pack(pady=50)

        # Timer progress bar
        self.progress = ttk.Progressbar(self.root, orient='horizontal', length=500, mode='determinate', maximum=15)
        self.progress.pack(pady=10)
        self.update_timer()

        # Option buttons
        self.option_buttons = []
        for option in question_data["options"]:
            btn = tk.Button(self.root, text=option, font=("Helvetica", 18), width=30, bg="#6A5ACD", fg="white",
                            command=lambda o=option: self.check_answer(o))
            btn.pack(pady=10)
            self.option_buttons.append(btn)

    # --------------------
    # Update Timer
    # --------------------
    def update_timer(self):
        if self.time_left >= 0 and self.timer_running:
            self.progress['value'] = 15 - self.time_left
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left < 0:
            self.timer_running = False
            self.flash_color("#FF4500")  # Time up
            self.root.after(800, self.next_question)

    # --------------------
    # Check Answer
    # --------------------
    def check_answer(self, selected_option):
        if not self.timer_running:
            return
        self.timer_running = False

        correct_answer = self.questions[self.current_question]["answer"]
        if selected_option == correct_answer:
            self.score += 1
            self.flash_color("#00FF00")
            threading.Thread(target=self.play_sound, args=("correct.wav",)).start()
        else:
            self.flash_color("#FF4500")
            threading.Thread(target=self.play_sound, args=("wrong.wav",)).start()

        self.root.after(800, self.next_question)

    # --------------------
    # Next Question
    # --------------------
    def next_question(self):
        self.current_question += 1
        self.show_question()

    # --------------------
    # Flash Background
    # --------------------
    def flash_color(self, color):
        original = self.root["bg"]
        self.root.configure(bg=color)
        self.root.after(500, lambda: self.root.configure(bg=original))

    # --------------------
    # Play Sound
    # --------------------
    def play_sound(self, filename):
        try:
            winsound.PlaySound(filename, winsound.SND_FILENAME)
        except:
            pass

    # --------------------
    # Show Result with Dynamic Confetti & Animated Text
    # --------------------
    def show_result(self):
        self.stop_animations()
        self.clear_screen()
        self.animating = True

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="#1E1E2F", highlightthickness=0)
        self.canvas.pack()

        # Dynamic confetti based on score
        particles_count = 50 + self.score * 50  # Higher score = more particles
        self.confetti_particles = []
        self.create_confetti(particles_count)

        # Animated text
        self.result_text_id = self.canvas.create_text(400, 100,
            text=f"🏆 Game Over! Your Score: {self.score}/{len(self.questions)} 🏆",
            font=("Helvetica", 24, "bold"), fill="#FFD700")
        self.text_blink = True
        self.animate_text()

        # Play celebratory sound
        threading.Thread(target=self.play_sound, args=("celebration.wav",)).start()

        # Confetti animation
        self.animate_confetti()

        # Buttons container frame
        button_frame = tk.Frame(self.root, bg="#1E1E2F")
        button_frame.pack(side="bottom", pady=30)

        # Play Again button
        restart_btn = tk.Button(button_frame, text="Play Again", font=("Helvetica", 20), width=25, bg="#4B0082", fg="white",
                                command=self.create_category_screen)
        restart_btn.pack(side="left", padx=10)

        # Exit button
        exit_btn = tk.Button(button_frame, text="Exit", font=("Helvetica", 20), width=25, bg="#FF0000", fg="white",
                             command=self.root.destroy)
        exit_btn.pack(side="left", padx=10)

    # --------------------
    # Stop animations safely
    # --------------------
    def stop_animations(self):
        self.animating = False
        self.timer_running = False
        self.text_blink = False

    # --------------------
    # Create Confetti
    # --------------------
    def create_confetti(self, count=150):
        for _ in range(count):
            x = random.randint(0, 800)
            y = random.randint(-600, 0)
            size = random.randint(5, 12)
            color = random.choice(["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"])
            particle = {"x": x, "y": y, "size": size, "color": color, "speed": random.randint(3, 8), "shape": None}
            self.confetti_particles.append(particle)

    # --------------------
    # Animate Confetti safely
    # --------------------
    def animate_confetti(self):
        if self.animating and hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.delete("confetti")
            for p in self.confetti_particles:
                p["y"] += p["speed"]
                if p["y"] > 600:
                    p["y"] = random.randint(-100, 0)
                    p["x"] = random.randint(0, 800)
                p["shape"] = self.canvas.create_oval(p["x"], p["y"], p["x"] + p["size"], p["y"] + p["size"],
                                                     fill=p["color"], outline="", tags="confetti")
            self.root.after(50, self.animate_confetti)

    # --------------------
    # Animate Blinking Text safely
    # --------------------
    def animate_text(self):
        if self.animating and hasattr(self, 'canvas') and self.canvas.winfo_exists():
            if self.text_blink:
                self.canvas.itemconfig(self.result_text_id, fill=random.choice(
                    ["#FFD700", "#FF69B4", "#00FFFF", "#00FF00", "#FF4500"]))
            self.root.after(500, self.animate_text)

    # --------------------
    # Clear Screen Utility
    # --------------------
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# ====================
# Run the Game
# ====================
if __name__ == "__main__":
    root = tk.Tk()
    game = MiniGameShow(root)
    root.mainloop()
