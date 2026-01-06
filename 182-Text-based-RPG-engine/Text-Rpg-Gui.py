import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random

# ----- Game Logic -----
class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.level = 1
        self.exp = 0
        self.items = {"Potion": 2, "Elixir": 1, "Bomb": 1}
        self.status_effects = {}

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.hp = self.max_hp
        self.exp = 0
        messagebox.showinfo("Level Up!", f"{self.name} reached level {self.level}!")

    def use_item(self, item_name, target_enemy=None):
        if self.items.get(item_name, 0) > 0:
            if item_name == "Potion":
                heal_amount = 50
                self.hp = min(self.max_hp, self.hp + heal_amount)
                self.items[item_name] -= 1
                return heal_amount, f"{self.name} used a Potion and restored {heal_amount} HP!"
            elif item_name == "Elixir":
                heal_amount = 100
                self.hp = min(self.max_hp, self.hp + heal_amount)
                self.items[item_name] -= 1
                return heal_amount, f"{self.name} used an Elixir and restored {heal_amount} HP!"
            elif item_name == "Bomb" and target_enemy:
                damage = 50
                target_enemy.hp -= damage
                target_enemy.add_status('burn', 2)
                self.items[item_name] -= 1
                return -damage, f"{self.name} used a Bomb on {target_enemy.name} for {damage} damage and inflicted burn!"
        return 0, f"No {item_name}s left!"

    def add_status(self, status_name, duration):
        self.status_effects[status_name] = duration

    def apply_statuses(self):
        total_damage = 0
        if 'poison' in self.status_effects:
            dmg = 5
            self.hp -= dmg
            total_damage += dmg
            self.status_effects['poison'] -= 1
            if self.status_effects['poison'] <= 0:
                del self.status_effects['poison']
        return total_damage

class Enemy:
    def __init__(self, name, hp, exp_reward):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.exp_reward = exp_reward
        self.status_effects = {}

    def add_status(self, status_name, duration):
        self.status_effects[status_name] = duration

    def apply_statuses(self):
        total_damage = 0
        if 'burn' in self.status_effects:
            dmg = 10
            self.hp -= dmg
            total_damage += dmg
            self.status_effects['burn'] -= 1
            if self.status_effects['burn'] <= 0:
                del self.status_effects['burn']
        return total_damage

# ----- Game Engine -----
class GameEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-Based RPG")
        self.style = ttk.Style(theme="cosmo")

        self.player = None
        self.current_enemy = None

        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill=BOTH, expand=YES)

        self.label = ttk.Label(self.frame, text="Enter your hero's name:")
        self.label.pack(pady=5)

        self.entry = ttk.Entry(self.frame)
        self.entry.pack(pady=5)

        self.start_button = ttk.Button(self.frame, text="Start Adventure", command=self.start_game)
        self.start_button.pack(pady=10)

        # HP bars
        self.player_hp_bar = ttk.Progressbar(self.frame, length=300, maximum=100)
        self.enemy_hp_bar = ttk.Progressbar(self.frame, length=300, maximum=100)

        # Status labels
        self.player_status_label = ttk.Label(self.frame, text="Player Status: None")
        self.enemy_status_label = ttk.Label(self.frame, text="Enemy Status: None")

        # Canvas for attack/heal animations
        self.animation_canvas = tk.Canvas(self.frame, width=300, height=50, bg="white")
        self.animation_canvas.pack(pady=5)

        self.text_area = tk.Text(self.frame, height=10, state=DISABLED)
        self.text_area.pack(pady=10, fill=BOTH, expand=YES)

        self.action_frame = ttk.Frame(self.frame)
        self.action_frame.pack(pady=10)

    def start_game(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a valid name.")
            return

        self.player = Player(name)
        self.entry.destroy()
        self.start_button.destroy()
        self.label.config(text=f"Welcome, {name}! Choose your action:")

        # Show HP bars and status labels
        self.player_hp_bar.pack(pady=5)
        self.enemy_hp_bar.pack(pady=5)
        self.player_status_label.pack()
        self.enemy_status_label.pack()

        self.show_main_actions()
        self.update_bars()

    def show_main_actions(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        ttk.Button(self.action_frame, text="Explore", command=self.explore).pack(side=LEFT, padx=5)
        ttk.Button(self.action_frame, text="Show Stats", command=self.show_stats).pack(side=LEFT, padx=5)
        ttk.Button(self.action_frame, text="Quit", command=self.root.quit).pack(side=LEFT, padx=5)

    def explore(self):
        enemies = [Enemy("Goblin", 50, 20), Enemy("Orc", 80, 40), Enemy("Dragon", 150, 100)]
        self.current_enemy = random.choice(enemies)
        self.log(f"You encountered a {self.current_enemy.name} with {self.current_enemy.hp} HP!")
        self.enemy_hp_bar['maximum'] = self.current_enemy.max_hp
        self.enemy_hp_bar['value'] = self.current_enemy.hp
        self.show_combat_menu()
        self.update_status_labels()

    def show_combat_menu(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        ttk.Button(self.action_frame, text="Attack", command=self.attack).pack(side=LEFT, padx=5)
        ttk.Button(self.action_frame, text="Defend", command=self.defend).pack(side=LEFT, padx=5)
        ttk.Button(self.action_frame, text="Use Item", command=self.show_inventory).pack(side=LEFT, padx=5)
        ttk.Button(self.action_frame, text="Run", command=self.run_away).pack(side=LEFT, padx=5)

    def attack(self):
        damage = random.randint(15, 30)
        self.animate_attack(target='enemy')
        self.current_enemy.hp -= damage
        self.log(f"You attack {self.current_enemy.name} for {damage} damage.")
        self.apply_status_effects()
        self.update_bars()
        self.check_battle_end()
        self.enemy_turn()

    def defend(self):
        self.log(f"{self.player.name} braces for the next attack, reducing damage taken!")
        self.apply_status_effects()
        self.update_bars()
        self.enemy_turn(defending=True)

    def show_inventory(self):
        inv_window = tk.Toplevel(self.root)
        inv_window.title("Inventory")
        for item, count in self.player.items.items():
            if count > 0:
                def use_item_closure(item_name=item):
                    amount, result = self.player.use_item(item_name, target_enemy=self.current_enemy)
                    if amount > 0:
                        self.animate_heal(amount)
                    elif amount < 0:
                        self.animate_attack(target='enemy')
                    self.log(result)
                    inv_window.destroy()
                    self.apply_status_effects()
                    self.update_bars()
                    self.check_battle_end()
                    self.enemy_turn()
                ttk.Button(inv_window, text=f"{item} x{count}", command=use_item_closure).pack(pady=5)

    def animate_attack(self, target='enemy'):
        bar = self.enemy_hp_bar if target=='enemy' else self.player_hp_bar
        original_color = bar.cget('style')
        flash_color = 'danger.Horizontal.TProgressbar'
        self.style.configure(flash_color, troughcolor='white', background='red')
        bar['style'] = flash_color
        self.root.after(200, lambda: bar.configure(style=original_color))

    def animate_heal(self, amount):
        bar = self.player_hp_bar
        original_color = bar.cget('style')
        flash_color = 'success.Horizontal.TProgressbar'
        self.style.configure(flash_color, troughcolor='white', background='green')
        bar['style'] = flash_color
        self.root.after(200, lambda: bar.configure(style=original_color))

    def run_away(self):
        success = random.random() > 0.3
        if success:
            self.log("You successfully ran away!")
            self.show_main_actions()
        else:
            self.log("Failed to run away!")
            self.apply_status_effects()
            self.update_bars()
            self.enemy_turn()

    def enemy_turn(self, defending=False):
        if self.current_enemy.hp <= 0:
            return
        damage = random.randint(10, 25)
        if defending:
            damage //= 2
        self.player.hp -= damage
        self.animate_attack(target='player')
        self.log(f"{self.current_enemy.name} attacks you for {damage} damage.")
        self.apply_status_effects()
        self.update_bars()
        self.check_player_defeat()

    def apply_status_effects(self):
        player_damage = self.player.apply_statuses()
        enemy_damage = self.current_enemy.apply_statuses() if self.current_enemy else 0
        if player_damage > 0:
            self.animate_attack(target='player')
            self.log(f"{self.player.name} took {player_damage} damage from status effects!")
        if enemy_damage > 0:
            self.animate_attack(target='enemy')
            self.log(f"{self.current_enemy.name} took {enemy_damage} damage from status effects!")
        self.update_status_labels()

    def update_bars(self):
        if self.player:
            self.player_hp_bar['maximum'] = self.player.max_hp
            self.player_hp_bar['value'] = max(0, self.player.hp)
        if self.current_enemy:
            self.enemy_hp_bar['maximum'] = self.current_enemy.max_hp
            self.enemy_hp_bar['value'] = max(0, self.current_enemy.hp)

    def update_status_labels(self):
        player_status = ', '.join([f"{k}({v})" for k,v in self.player.status_effects.items()]) or 'None'
        enemy_status = ', '.join([f"{k}({v})" for k,v in self.current_enemy.status_effects.items()]) if self.current_enemy else 'None'
        self.player_status_label.config(text=f"Player Status: {player_status}")
        self.enemy_status_label.config(text=f"Enemy Status: {enemy_status}")

    def show_stats(self):
        items_list = ', '.join([f"{k} x{v}" for k, v in self.player.items.items() if v > 0])
        status_list = ', '.join([f"{k} ({v} turns)" for k, v in self.player.status_effects.items()])
        status_text = status_list if status_list else 'None'
        self.log(f"Name: {self.player.name} | HP: {self.player.hp}/{self.player.max_hp} | Level: {self.player.level} | EXP: {self.player.exp} | Items: {items_list} | Status: {status_text}")

    def check_battle_end(self):
        if self.current_enemy and self.current_enemy.hp <= 0:
            self.log(f"You defeated {self.current_enemy.name}!")
            self.player.gain_exp(self.current_enemy.exp_reward)
            self.current_enemy = None
            self.show_main_actions()
            self.update_bars()

    def check_player_defeat(self):
        if self.player.hp <= 0:
            self.log("You were defeated! Game Over.")
            messagebox.showinfo("Game Over", "You have fallen in battle.")
            self.root.quit()

    def log(self, message):
        self.text_area.config(state=NORMAL)
        self.text_area.insert(END, message + "\n")
        self.text_area.see(END)
        self.text_area.config(state=DISABLED)

# ----- Main Application -----
if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = GameEngine(root)
    root.mainloop()
