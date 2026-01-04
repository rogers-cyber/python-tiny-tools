import tkinter as tk
from tkinter import messagebox, ttk
from dataclasses import dataclass
from typing import List
import random, time, threading, platform, os, math

from PIL import Image, ImageTk, ImageSequence, ImageFilter

import ttkbootstrap as tb

# ---------------- CONFIG ---------------- #
UPDATE_INTERVAL = 2000
ANIM_INTERVAL = 150
DAY_NIGHT_STEP = 0.002
SPECIES_LIST = ["cat","dog","rabbit","hamster","parrot"]
NEGLECT_LIMIT = 15
CANVAS_SIZE = 80
TOY_COUNT = 3
QUEST_INTERVAL = 15000  # milliseconds

# ---------------- SOUND ALERT ---------------- #
try:
    if platform.system() == "Windows":
        import winsound
        def play_alert(): winsound.Beep(1000,300)
    else:
        from playsound import playsound
        def play_alert():
            threading.Thread(target=lambda: playsound("alert.mp3"), daemon=True).start()
except: 
    def play_alert(): pass

# ---------------- PET DATA STRUCTURE ---------------- #
@dataclass
class Pet:
    name: str
    species: str
    mood: str="Happy"
    energy: int=100
    hunger: int=100
    social: int=50
    last_alive_time: float=time.time()
    alive: bool=True
    frame: tk.Frame=None
    mood_bar: ttk.Progressbar=None
    energy_bar: ttk.Progressbar=None
    canvas: tk.Canvas=None
    base_images: List[Image.Image]=None
    tk_images: List[ImageTk.PhotoImage]=None
    canvas_image=None
    anim_index:int=0
    target_object=None
    interacting_with: 'Pet'=None
    current_quest=None
    x: float=0.0
    y: float=0.0
    dx: float=0.0
    dy: float=0.0

@dataclass
class EnvObject:
    canvas_item: int
    type: str
    x: int
    y: int
    img: ImageTk.PhotoImage

# ---------------- HELPERS ---------------- #
def blend_color(energy:int):
    energy=max(0,min(100,energy))
    if energy>=50: r=int((100-energy)/50*255); g=255
    else: r=255; g=int(energy/50*255)
    return (r,g,0)

def apply_color_overlay(img:Image.Image, color:tuple):
    overlay = Image.new("RGBA", img.size, color+(120,))
    return Image.alpha_composite(img.convert("RGBA"), overlay)

def distance(p1,p2): return math.hypot(p1.x-p2.x,p1.y-p2.y)
def distance_point(x1,y1,x2,y2): return math.hypot(x1-x2,y1-y2)

# ---------------- GENERATE PETS ---------------- #
def generate_pets(n=5)->List[Pet]:
    pets=[]
    for i in range(n):
        name=f"Pet{i+1}"
        species=random.choice(SPECIES_LIST)
        energy=random.randint(50,100)
        pets.append(Pet(name,species,energy=energy))
    return pets

def load_pet_images(species:str)->List[Image.Image]:
    path=f"images/{species}.gif"
    if not os.path.exists(path): return []
    img=Image.open(path)
    frames=[frame.copy().resize((CANVAS_SIZE,CANVAS_SIZE)) for frame in ImageSequence.Iterator(img)]
    return frames

# ---------------- ENVIRONMENT ---------------- #
clouds=[]
stars=[]
toys=[]
quests=[]
def create_environment(canvas):
    def _create():
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        # Retry if canvas too small
        if width <= 100 or height <= 100:
            canvas.after(100, _create)
            return

        global clouds, stars, toys

        # Clouds
        for i in range(5):
            x = random.randint(0, width)
            y = random.randint(10, max(11, 100))
            oval = canvas.create_oval(x, y, x + 100, y + 40, fill="white", outline="")
            clouds.append((oval, random.randint(1, 3)))

        # Stars
        for i in range(50):
            x = random.randint(0, width)
            y = random.randint(0, max(1, 150))
            star = canvas.create_oval(x, y, x + 2, y + 2, fill="white", outline="")
            stars.append(star)

        # Toys
        for i in range(TOY_COUNT):
            x = random.randint(50, max(51, width - 50))
            y = random.randint(50, max(51, height - 50))
            oval = canvas.create_oval(x, y, x + 20, y + 20, fill="orange", outline="")
            toys.append(EnvObject(canvas_item=oval, type="toy", x=x, y=y, img=None))

    canvas.after(100, _create)

def animate_environment(canvas):
    for idx, (cloud, speed) in enumerate(clouds):
        pos = canvas.coords(cloud)
        if not pos or len(pos) < 4:
            continue  # skip invalid cloud
        canvas.move(cloud, speed, 0)
        if pos[0] > canvas.winfo_width():
            canvas.move(cloud, -canvas.winfo_width()-100, 0)
    for star in stars:
        if canvas.coords(star):
            canvas.itemconfig(star, fill="yellow" if random.random()<0.1 else "white")
    canvas.after(100, lambda: animate_environment(canvas))

# ---------------- PET UI ---------------- #
def update_pet_ui(pet:Pet):
    if not pet.alive:
        if pet.energy_bar and pet.mood_bar: pet.energy_bar['value']=0; pet.mood_bar['value']=0
        if pet.canvas and pet.tk_images: pet.canvas.itemconfig(pet.canvas_image,image=pet.tk_images[0])
        pet.frame.config(highlightbackground="black",highlightthickness=2)
        return
    if pet.energy_bar and pet.mood_bar:
        pet.energy_bar['value']=pet.energy
        pet.mood_bar['value']=100 if pet.mood in ["Happy","Playful","Excited"] else pet.energy
    pet.frame.config(highlightbackground="red",highlightthickness=3 if pet.energy<20 else 0)
    pet.tk_images=[]
    for frame in pet.base_images:
        blended = apply_color_overlay(frame, blend_color(pet.energy))
        glow = blended.filter(ImageFilter.GaussianBlur(radius=4))
        combined = Image.alpha_composite(glow, blended.convert("RGBA"))
        shadow = Image.new("RGBA", combined.size, (0,0,0,0))
        shadow_ellipse = Image.new("RGBA",(int(combined.width*0.8),int(combined.height*0.2)),(0,0,0,100))
        shadow.paste(shadow_ellipse,(int(combined.width*0.1),int(combined.height*0.75)),shadow_ellipse)
        final = Image.alpha_composite(shadow, combined)
        pet.tk_images.append(ImageTk.PhotoImage(final))

# ---------------- PET ANIMATION ---------------- #
def animate_pet(pet:Pet):
    if not pet.alive or not pet.tk_images: return
    pet.anim_index=(pet.anim_index+1)%len(pet.tk_images)
    pulse_scale = 0.8 + 0.4*(pet.energy/100)
    size=int(CANVAS_SIZE*pulse_scale)
    canvas_img = ImageTk.PhotoImage(pet.base_images[pet.anim_index].resize((size,size)))
    pet.canvas.itemconfig(pet.canvas_image,image=canvas_img)
    pet.canvas.image = canvas_img
    pet.frame.after(ANIM_INTERVAL, lambda: animate_pet(pet))

# ---------------- AUTONOMOUS MOVEMENT ---------------- #
def move_pet(pet:Pet):
    if not pet.alive or not pet.canvas or not pet.tk_images: 
        pet.frame.after(ANIM_INTERVAL, lambda: move_pet(pet))
        return

    canvas = pet.canvas
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    # Check social interaction
    nearby = [p for p in pets if p != pet and p.alive and distance(p, pet) < 150]
    if nearby and pet.mood == "Playful":
        partner = random.choice(nearby)
        pet.interacting_with = partner
        dx = partner.x - pet.x
        dy = partner.y - pet.y
        dist = math.hypot(dx, dy)
        if dist > 2:
            pet.dx = dx * 0.05
            pet.dy = dy * 0.05
        else:
            pet.dx = pet.dy = 0
            pet.mood = partner.mood = "Excited"
            pet.energy = min(pet.energy + 5, 100)
            partner.energy = min(partner.energy + 5, 100)
            pet.interacting_with = None
    # Check quests/treats
    elif quests:
        nearest = min(quests, key=lambda q: distance_point(pet.x, pet.y, q.x, q.y))
        dx = nearest.x - pet.x
        dy = nearest.y - pet.y
        dist = math.hypot(dx, dy)
        if dist > 2:
            pet.dx = dx * 0.05
            pet.dy = dy * 0.05
        else:
            pet.dx = pet.dy = 0
            pet.energy = min(pet.energy + 15, 100)
            pet.mood = "Excited"
            canvas.delete(nearest.canvas_item)
            quests.remove(nearest)
            play_alert()
    # Random wandering
    else:
        if random.random() < 0.05:
            pet.dx = random.uniform(-2, 2)
            pet.dy = random.uniform(-2, 2)

    # Update position
    pet.x += pet.dx
    pet.y += pet.dy

    # ✅ Constrain within canvas
    pet.x = max(0, min(pet.x, width - CANVAS_SIZE))
    pet.y = max(0, min(pet.y, height - CANVAS_SIZE))

    # Update canvas
    pet.canvas.coords(pet.canvas_image, pet.x, pet.y)
    pet.frame.after(ANIM_INTERVAL, lambda: move_pet(pet))

# ---------------- DAY/NIGHT ---------------- #
day_night_progress=0.0
day_night_direction=1
def update_background():
    global day_night_progress, day_night_direction
    day_color=(135,206,250)
    night_color=(0,31,63)
    r=int(day_color[0]*(1-day_night_progress)+night_color[0]*day_night_progress)
    g=int(day_color[1]*(1-day_night_progress)+night_color[1]*day_night_progress)
    b=int(day_color[2]*(1-day_night_progress)+night_color[2]*day_night_progress)
    hex_color=f"#{r:02x}{g:02x}{b:02x}"
    app.configure(bg=hex_color)
    pet_container.configure(bg=hex_color)
    day_night_progress += DAY_NIGHT_STEP*day_night_direction
    if day_night_progress>=1.0 or day_night_progress<=0.0: day_night_direction*=-1
    app.after(50, update_background)

# ---------------- PET STATE UPDATE ---------------- #
def update_pet_states():
    for pet in pets:
        if not pet.alive: continue
        pet.energy=max(pet.energy-random.randint(2,6),0)
        pet.hunger=max(pet.hunger-random.randint(1,4),0)
        pet.social=max(pet.social-random.randint(1,3),0)
        if pet.energy<20: pet.mood="Hungry"; play_alert()
        elif pet.energy<50: pet.mood="Sleepy"
        else: pet.mood=random.choice(["Happy","Playful","Excited"])
        if pet.energy<=0 and time.time()-pet.last_alive_time>NEGLECT_LIMIT:
            pet.alive=False; pet.mood="Dead"; pet.energy=0
            messagebox.showwarning("Oh no!",f"{pet.name} has died from neglect!")
        update_pet_ui(pet)
    app.after(UPDATE_INTERVAL,update_pet_states)

# ---------------- SPAWN QUEST ---------------- #
def spawn_quest(canvas):
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    if width <= 100 or height <= 100:
        canvas.after(100, lambda: spawn_quest(canvas))
        return

    x = random.randint(50, max(51, width-50))
    y = random.randint(50, max(51, height-50))

    oval = canvas.create_oval(x, y, x + 15, y + 15, fill="gold", outline="")
    quests.append(EnvObject(canvas_item=oval, type="treat", x=x, y=y, img=None))
    canvas.after(QUEST_INTERVAL, lambda: spawn_quest(canvas))

# ---------------- SETUP SCROLLABLE PET CONTAINER ---------------- #
def setup_pet_container():
    global pet_container, pet_container_canvas

    # Scrollable canvas for pet panels
    pet_container_canvas = tk.Canvas(app, bg="#1f1f1f", highlightthickness=0)
    scrollbar = tk.Scrollbar(app, orient="vertical", command=pet_container_canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    pet_container_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    pet_container_canvas.configure(yscrollcommand=scrollbar.set)

    # Frame inside canvas
    pet_container = tk.Frame(pet_container_canvas, bg="#2c2c2c")
    container_window = pet_container_canvas.create_window((0,0), window=pet_container, anchor="nw", width=pet_container_canvas.winfo_width(), tags="container_window")

    # Update scroll region dynamically
    def update_scroll_region(event):
        pet_container_canvas.configure(scrollregion=pet_container_canvas.bbox("all"))
        # Stretch frame to full canvas width
        pet_container_canvas.itemconfig("container_window", width=event.width)

    pet_container_canvas.bind("<Configure>", update_scroll_region)
    pet_container.bind("<Configure>", update_scroll_region)

def init_pet_position(pet):
    # Delay execution so canvas has proper width
    def _init():
        width = pet.canvas.winfo_width()
        height = pet.canvas.winfo_height()
        pet.x = random.randint(0, max(1, width - CANVAS_SIZE))
        pet.y = random.randint(0, max(1, height - CANVAS_SIZE))
        if pet.tk_images:
            pet.canvas.coords(pet.canvas_image, pet.x, pet.y)
    pet.canvas.after(100, _init)  # small delay to allow canvas to render

# ---------------- CREATE FULL-WIDTH PET PANELS ---------------- #
def create_pet_panels():
    for pet in pets:
        # Main panel frame
        frame = tk.Frame(pet_container, relief="raised", borderwidth=2, padx=10, pady=10, bg="#2c2c2c")
        frame.pack(fill=tk.X, expand=True, padx=10, pady=8)
        pet.frame = frame

        # Pet title
        tb.Label(frame, text=f"{pet.name} ({pet.species})", 
                 font=("Segoe UI", 14, "bold"), bootstyle="inverse").pack(anchor=tk.W, pady=(0,5))

        # Full-width canvas for pet animation
        canvas = tk.Canvas(frame, bg="#1f1f1f", highlightthickness=0, height=CANVAS_SIZE*3)
        canvas.pack(fill=tk.X, expand=True, padx=5, pady=5)
        pet.canvas = canvas

        # Load pet images
        pet.base_images = load_pet_images(pet.species)
        update_pet_ui(pet)
        if pet.tk_images: 
            pet.canvas_image = canvas.create_image(0, 0, anchor="nw", image=pet.tk_images[0])

        # Safe random initial position after canvas renders
        def init_position():
            width = pet.canvas.winfo_width()
            height = pet.canvas.winfo_height()
            pet.x = random.randint(0, max(1, width - CANVAS_SIZE))
            pet.y = random.randint(0, max(1, height - CANVAS_SIZE))
            if pet.tk_images:
                pet.canvas.coords(pet.canvas_image, pet.x, pet.y)
        pet.canvas.after(100, init_position)

        # Start animation & movement
        animate_pet(pet)
        move_pet(pet)
        spawn_quest(canvas)
        create_environment(canvas)
        animate_environment(canvas)

        # Info & controls below canvas
        info_frame = tk.Frame(frame, bg="#2c2c2c")
        info_frame.pack(fill=tk.X, padx=15, pady=5)

        energy_bar = ttk.Progressbar(info_frame, length=300, maximum=100)
        energy_bar.pack(anchor=tk.W, pady=4)
        energy_bar['value'] = pet.energy
        pet.energy_bar = energy_bar
        tb.Label(info_frame, text="Energy", bootstyle="secondary").pack(anchor=tk.W)

        mood_bar = ttk.Progressbar(info_frame, length=300, maximum=100)
        mood_bar.pack(anchor=tk.W, pady=4)
        mood_bar['value'] = 100
        pet.mood_bar = mood_bar
        tb.Label(info_frame, text="Mood", bootstyle="secondary").pack(anchor=tk.W)

        btn_frame = tk.Frame(info_frame, bg="#2c2c2c")
        btn_frame.pack(anchor=tk.W, pady=5)
        tb.Button(btn_frame, text="▶ Play", bootstyle="info-outline", width=10, 
                  command=lambda p=pet: setattr(p, "mood", "Playful")).pack(side=tk.LEFT, padx=3)
        tb.Button(btn_frame, text="🍖 Feed", bootstyle="success-outline", width=10, 
                  command=lambda p=pet: setattr(p, "energy", min(p.energy+25,100))).pack(side=tk.LEFT, padx=3)
        tb.Button(btn_frame, text="🛌 Sleep", bootstyle="secondary-outline", width=10, 
                  command=lambda p=pet: setattr(p, "energy", min(p.energy+30,100))).pack(side=tk.LEFT, padx=3)

# ---------------- MAIN APP ---------------- #
app = tb.Window(title="Autonomous Ultimate Tamagotchi Ecosystem",
                themename="darkly",
                size=(1000, 500),
                resizable=(True, True))

tb.Label(app, text="🐾 Autonomous Ultimate Tamagotchi Ecosystem",
         font=("Segoe UI", 18, "bold")).pack(pady=10, padx=10)

# Setup scrollable container
setup_pet_container()

# Generate pets
pets = generate_pets(5)

# Create panels
create_pet_panels()

# Background and updates
update_background()
app.after(UPDATE_INTERVAL, update_pet_states)
app.mainloop()
