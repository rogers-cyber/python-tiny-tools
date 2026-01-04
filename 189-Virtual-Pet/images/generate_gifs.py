import os
from PIL import Image, ImageDraw

# ---------------- CREATE IMAGES FOLDER ---------------- #
folder = "images"
if not os.path.exists(folder):
    os.makedirs(folder)

# ---------------- PET NAMES AND BASE COLORS ---------------- #
animals = ["cat", "dog", "rabbit", "hamster", "parrot"]
# Colors for moods: High energy / Medium / Low
mood_colors = [
    ("#4CAF50", "#FFD700", "#FF4C4C"),  # green, yellow, red
    ("#8B4513", "#DAA520", "#CD5C5C"),  # brown variants
    ("#808080", "#FFFF66", "#FF6666"),  # gray variants
    ("#FFFF00", "#FFD700", "#FF6347"),  # yellow variants
    ("#00FF00", "#ADFF2F", "#FF4500")   # green variants
]

# ---------------- CREATE ANIMATED GIFS ---------------- #
for idx, name in enumerate(animals):
    colors = mood_colors[idx]
    frames = []

    # Each pet will have 9 frames: 3 frames per mood cycling
    for state_color in colors:
        for i in range(3):  # 3 frames per mood for animation
            img = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # draw a circle that slightly changes size per frame
            draw.ellipse([10+i*2, 10+i*2, 70-i*2, 70-i*2], fill=state_color)
            frames.append(img)

    gif_path = os.path.join(folder, f"{name}.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], loop=0, duration=200)

print(f"All mood-aware GIFs created in folder '{folder}' successfully!")
