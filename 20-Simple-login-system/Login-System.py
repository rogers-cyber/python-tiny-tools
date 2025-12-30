import tkinter as tk
from tkinter import messagebox
import hashlib
import json
import os

USER_FILE = 'users.json'

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Modern Login System')
        self.root.geometry('450x550')
        self.root.configure(bg='#1f2f3a')
        self.root.resizable(False, False)
        self.users = load_users()
        self.create_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text='Welcome Back!', font=('Helvetica', 28, 'bold'), bg='#1f2f3a', fg='#ffffff').pack(pady=30)

        # Username input
        username_frame = tk.Frame(self.root, bg='#1f2f3a')
        username_frame.pack(pady=10)
        tk.Label(username_frame, text='Username', font=('Helvetica', 12), bg='#1f2f3a', fg='#bdc3c7').pack(anchor='w')
        self.username_entry = tk.Entry(username_frame, font=('Helvetica', 14), bd=0, highlightthickness=2, highlightbackground='#2980b9', width=30)
        self.username_entry.pack(pady=5, ipady=6)  # ipady increases vertical padding inside entry

        # Password input
        password_frame = tk.Frame(self.root, bg='#1f2f3a')
        password_frame.pack(pady=10)
        tk.Label(password_frame, text='Password', font=('Helvetica', 12), bg='#1f2f3a', fg='#bdc3c7').pack(anchor='w')
        self.password_entry = tk.Entry(password_frame, font=('Helvetica', 14), bd=0, highlightthickness=2, highlightbackground='#2980b9', show='*', width=30)
        self.password_entry.pack(pady=5, ipady=6)

        # Buttons
        btn_frame = tk.Frame(self.root, bg='#1f2f3a')
        btn_frame.pack(pady=20)

        login_btn = tk.Button(btn_frame, text='Login', command=self.login, bg='#2980b9', fg='white', font=('Helvetica', 12, 'bold'), width=25, height=2, bd=0, activebackground='#3498db', cursor='hand2')
        login_btn.pack(pady=5)
        register_btn = tk.Button(btn_frame, text='Register', command=self.create_register_screen, bg='#27ae60', fg='white', font=('Helvetica', 12, 'bold'), width=25, height=2, bd=0, activebackground='#2ecc71', cursor='hand2')
        register_btn.pack(pady=5)
        forgot_btn = tk.Button(btn_frame, text='Forgot Password?', command=self.forgot_password, bg='#e67e22', fg='white', font=('Helvetica', 12, 'bold'), width=25, height=2, bd=0, activebackground='#f39c12', cursor='hand2')
        forgot_btn.pack(pady=5)

    def create_register_screen(self):
        self.clear_screen()
        tk.Label(self.root, text='Create Account', font=('Helvetica', 28, 'bold'), bg='#1f2f3a', fg='#ffffff').pack(pady=30)

        # Username
        username_frame = tk.Frame(self.root, bg='#1f2f3a')
        username_frame.pack(pady=10)
        tk.Label(username_frame, text='Username', font=('Helvetica', 12), bg='#1f2f3a', fg='#bdc3c7').pack(anchor='w')
        self.reg_username = tk.Entry(username_frame, font=('Helvetica', 14), bd=0, highlightthickness=2, highlightbackground='#27ae60', width=30)
        self.reg_username.pack(pady=5, ipady=6)

        # Password
        password_frame = tk.Frame(self.root, bg='#1f2f3a')
        password_frame.pack(pady=10)
        tk.Label(password_frame, text='Password', font=('Helvetica', 12), bg='#1f2f3a', fg='#bdc3c7').pack(anchor='w')
        self.reg_password = tk.Entry(password_frame, font=('Helvetica', 14), bd=0, highlightthickness=2, highlightbackground='#27ae60', show='*', width=30)
        self.reg_password.pack(pady=5, ipady=6)

        # Confirm Password
        confirm_frame = tk.Frame(self.root, bg='#1f2f3a')
        confirm_frame.pack(pady=10)
        tk.Label(confirm_frame, text='Confirm Password', font=('Helvetica', 12), bg='#1f2f3a', fg='#bdc3c7').pack(anchor='w')
        self.reg_confirm = tk.Entry(confirm_frame, font=('Helvetica', 14), bd=0, highlightthickness=2, highlightbackground='#27ae60', show='*', width=30)
        self.reg_confirm.pack(pady=5, ipady=6)

        # Buttons
        btn_frame = tk.Frame(self.root, bg='#1f2f3a')
        btn_frame.pack(pady=20)

        register_btn = tk.Button(btn_frame, text='Register', command=self.register, bg='#27ae60', fg='white', font=('Helvetica', 12, 'bold'), width=25, height=2, bd=0, activebackground='#2ecc71', cursor='hand2')
        register_btn.pack(pady=5)
        back_btn = tk.Button(btn_frame, text='Back to Login', command=self.create_login_screen, bg='#c0392b', fg='white', font=('Helvetica', 12, 'bold'), width=25, height=2, bd=0, activebackground='#e74c3c', cursor='hand2')
        back_btn.pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed = hash_password(password)
        if username in self.users and self.users[username] == hashed:
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
        if password != confirm:
            messagebox.showerror('Error', 'Passwords do not match')
            return
        if username in self.users:
            messagebox.showerror('Error', 'Username already exists')
            return

        self.users[username] = hash_password(password)
        save_users(self.users)
        messagebox.showinfo('Success', 'Registration successful!')
        self.create_login_screen()

    def forgot_password(self):
        username = self.username_entry.get()
        if username in self.users:
            messagebox.showinfo('Password Reset', f'Password reset link sent to {username} (mock)')
        else:
            messagebox.showerror('Error', 'Username not found')

if __name__ == '__main__':
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
