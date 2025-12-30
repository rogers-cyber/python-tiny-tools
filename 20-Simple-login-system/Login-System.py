import tkinter as tk
from tkinter import messagebox
import json
import os
import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


# -------------------- Config --------------------

USER_FILE = 'users.json'

ph = PasswordHasher(
    time_cost=3,        # iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16
)


# -------------------- Storage --------------------

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)


# -------------------- Password Security --------------------

def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return ph.verify(stored_hash, password)
    except VerifyMismatchError:
        return False


def validate_password_strength(password: str) -> str | None:
    if len(password) < 12:
        return "Password must be at least 12 characters long"

    if not re.search(r"[A-Z]", password):
        return "Password must contain an uppercase letter"

    if not re.search(r"[a-z]", password):
        return "Password must contain a lowercase letter"

    if not re.search(r"\d", password):
        return "Password must contain a digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain a special character"

    return None


# -------------------- App --------------------

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Secure Login System')
        self.root.geometry('450x550')
        self.root.configure(bg='#1f2f3a')
        self.root.resizable(False, False)

        self.users = load_users()
        self.create_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # -------------------- Login Screen --------------------

    def create_login_screen(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text='Welcome Back!',
            font=('Helvetica', 28, 'bold'),
            bg='#1f2f3a',
            fg='#ffffff'
        ).pack(pady=30)

        frame = tk.Frame(self.root, bg='#1f2f3a')
        frame.pack(pady=10)

        tk.Label(frame, text='Username', fg='#bdc3c7', bg='#1f2f3a').pack(anchor='w')
        self.username_entry = tk.Entry(frame, font=('Helvetica', 14), width=30)
        self.username_entry.pack(ipady=6)

        frame = tk.Frame(self.root, bg='#1f2f3a')
        frame.pack(pady=10)

        tk.Label(frame, text='Password', fg='#bdc3c7', bg='#1f2f3a').pack(anchor='w')
        self.password_entry = tk.Entry(frame, font=('Helvetica', 14), show='*', width=30)
        self.password_entry.pack(ipady=6)

        frame = tk.Frame(self.root, bg='#1f2f3a')
        frame.pack(pady=20)

        tk.Button(frame, text='Login', height=2, width=46, command=self.login).pack(pady=5)
        tk.Button(frame, text='Register', height=2, width=46, command=self.create_register_screen).pack(pady=5)
        tk.Button(frame, text='Forgot Password?', height=2, width=46, command=self.forgot_password).pack(pady=5)

    # -------------------- Register Screen --------------------

    def create_register_screen(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text='Create Account',
            font=('Helvetica', 28, 'bold'),
            bg='#1f2f3a',
            fg='#ffffff'
        ).pack(pady=30)

        frame = tk.Frame(self.root, bg='#1f2f3a')
        frame.pack(pady=10)

        tk.Label(frame, text='Username', fg='#bdc3c7', bg='#1f2f3a').pack(anchor='w')
        self.reg_username = tk.Entry(frame, font=('Helvetica', 14), width=30)
        self.reg_username.pack(ipady=6)

        frame = tk.Frame(self.root, bg='#1f2f3a')
        frame.pack(pady=10)

        tk.Label(frame, text='Password', fg='#bdc3c7', bg='#1f2f3a').pack(anchor='w')
        self.reg_password = tk.Entry(frame, font=('Helvetica', 14), show='*', width=30)
        self.reg_password.pack(ipady=6)

        frame = tk.Frame(self.root, bg='#1f2f3a')
        frame.pack(pady=10)

        tk.Label(frame, text='Confirm Password', fg='#bdc3c7', bg='#1f2f3a').pack(anchor='w')
        self.reg_confirm = tk.Entry(frame, font=('Helvetica', 14), show='*', width=30)
        self.reg_confirm.pack(ipady=6)

        frame = tk.Frame(self.root, bg='#1f2f3a')
        frame.pack(pady=20)

        tk.Button(frame, text='Register', height=2, width=46, command=self.register).pack(pady=5)
        tk.Button(frame, text='Back', height=2, width=46, command=self.create_login_screen).pack(pady=5)

    # -------------------- Logic --------------------

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.users and verify_password(password, self.users[username]):
            messagebox.showinfo('Success', f'Welcome {username}!')
        else:
            messagebox.showerror('Error', 'Invalid username or password')

    def register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if not username or not password:
            messagebox.showerror('Error', 'All fields are required')
            return

        if username in self.users:
            messagebox.showerror('Error', 'Username already exists')
            return

        if password != confirm:
            messagebox.showerror('Error', 'Passwords do not match')
            return

        strength_error = validate_password_strength(password)
        if strength_error:
            messagebox.showerror('Weak Password', strength_error)
            return

        self.users[username] = hash_password(password)
        save_users(self.users)

        messagebox.showinfo('Success', 'Registration successful!')
        self.create_login_screen()

    def forgot_password(self):
        username = self.username_entry.get()
        if username in self.users:
            messagebox.showinfo(
                'Password Reset',
                f'Password reset link sent to {username} (mock)'
            )
        else:
            messagebox.showerror('Error', 'Username not found')


# -------------------- Run --------------------

if __name__ == '__main__':
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
