import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as tb
from cryptography.fernet import Fernet
import os
import sys
import base64
import hashlib

def resource_path(file_name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

def derive_key(password: str) -> bytes:
    """Derive a Fernet key from a password using SHA256"""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

class FileEncryptor:
    def __init__(self, root):
        self.root = root
        self.root.title("FileCryptor - File Encryption Tool")
        self.root.geometry("1100x660")
        # self.root.iconbitmap(resource_path("logo.ico"))

        # ===== Buttons Frame =====
        button_frame = tb.Frame(self.root)
        button_frame.pack(pady=10)

        self.encrypt_btn = tb.Button(
            button_frame, text="🔒 Encrypt Files", bootstyle="success-outline", width=25,
            command=lambda: self.start_process(encrypt=True)
        )
        self.encrypt_btn.grid(row=0, column=0, padx=5)

        self.decrypt_btn = tb.Button(
            button_frame, text="🔓 Decrypt Files", bootstyle="info-outline", width=25,
            command=lambda: self.start_process(encrypt=False)
        )
        self.decrypt_btn.grid(row=0, column=1, padx=5)

        self.cancel_event = threading.Event()

        self.cancel_btn = tb.Button(
            button_frame, text="❌ Cancel", bootstyle="danger-outline", width=20,
            state=tk.DISABLED, command=self.cancel_process
        )
        self.cancel_btn.grid(row=0, column=2, padx=5)

        self.clear_btn = tb.Button(
            button_frame, text="🧹 Clear Log", bootstyle="warning-outline", width=20,
            command=self.clear_log
        )
        self.clear_btn.grid(row=0, column=3, padx=5)

        self.about_btn = tb.Button(
            button_frame, text="ℹ️ About", bootstyle="secondary-outline", width=20,
            command=self.show_about_guide
        )
        self.about_btn.grid(row=0, column=4, padx=5)

        # ===== Log Area =====
        self.log_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 12))
        self.log_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # ===== Progress Bar Frame =====
        progress_frame = tb.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.progress_label = tb.Label(progress_frame, text="Ready")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress = tb.Progressbar(progress_frame, bootstyle="success-striped", mode="determinate")
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def cancel_process(self):
        self.cancel_event.set()
        self.progress_label.config(text="Cancelling...")

    def _reset_ui(self):
        self.progress["value"] = 0
        self.progress_label.config(text="Ready")
        self.encrypt_btn.config(state=tk.NORMAL)
        self.decrypt_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.cancel_event.clear()

    def _update_progress(self, value):
        self.progress["value"] = value
        self.progress_label.config(text=f"Processing... {int(value)}%")

    def _log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def clear_log(self):
        self.log_area.delete(1.0, tk.END)

    # ===== Worker =====
    def _process_worker(self, file_paths, password, encrypt=True):
        try:
            key = derive_key(password)
            fernet = Fernet(key)
            total_files = len(file_paths)
            step = 100 / total_files
            current_progress = 0

            for file_path in file_paths:
                if self.cancel_event.is_set():
                    self.root.after(0, self._reset_ui)
                    self._log("Process cancelled.")
                    return

                filename = os.path.basename(file_path)
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()

                    if encrypt:
                        processed_data = fernet.encrypt(data)
                        out_file = file_path + ".enc"
                    else:
                        processed_data = fernet.decrypt(data)
                        if file_path.endswith(".enc"):
                            out_file = file_path[:-4]
                        else:
                            out_file = file_path + ".dec"

                    with open(out_file, "wb") as f:
                        f.write(processed_data)

                    self._log(f"{'Encrypted' if encrypt else 'Decrypted'}: {filename}")

                except Exception as e:
                    self._log(f"Error processing {filename}: {str(e)}")

                current_progress += step
                self.root.after(0, self._update_progress, current_progress)

            self.root.after(0, self._reset_ui)
            self._log("Process completed.")

        except Exception as e:
            self.root.after(0, self._reset_ui)
            self._log(f"Fatal error: {str(e)}")

    # ===== Start Process =====
    def start_process(self, encrypt=True):
        action = "Encrypt" if encrypt else "Decrypt"
        file_paths = filedialog.askopenfilenames(title=f"Select files to {action}")
        if not file_paths:
            return

        password = tk.simpledialog.askstring("Password", f"Enter password to {action} files:", show="*")
        if not password:
            messagebox.showwarning("Password required", "Operation cancelled. Password is required!")
            return

        self.cancel_event.clear()
        self.encrypt_btn.config(state=tk.DISABLED)
        self.decrypt_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_label.config(text="Preparing...")
        self.progress["value"] = 0

        threading.Thread(target=self._process_worker, args=(file_paths, password, encrypt), daemon=True).start()

    # ===== About / Guide =====
    def show_about_guide(self):
        guide_window = tb.Toplevel(self.root)
        guide_window.title("📘 About / Guide")
        guide_window.geometry("600x480")
        guide_window.resizable(False, False)
        guide_window.grab_set()
        guide_window.attributes("-toolwindow", True)

        self.root.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        win_width = 600
        win_height = 480
        pos_x = root_x + (root_width // 2) - (win_width // 2)
        pos_y = root_y + (root_height // 2) - (win_height // 2)
        guide_window.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")

        frame = tb.Frame(guide_window, padding=10)
        frame.pack(fill="both", expand=True)

        sections = {
            "About FileCryptor": (
                "FileCryptor is a secure and easy-to-use desktop tool for encrypting and decrypting files.\n"
                "It uses password-based encryption (Fernet symmetric encryption) to protect your data."
            ),
            "Key Features": (
                "- Encrypt and decrypt multiple files\n"
                "- Password protected\n"
                "- Cancel operations anytime\n"
                "- Real-time progress bar\n"
                "- Modern, clean interface"
            ),
            "Built With": (
                "- Python\n"
                "- Tkinter & ttkbootstrap\n"
                "- cryptography library\n"
                "- Multithreading for responsive UI"
            ),
            "Developer": (
                "Developed by MateTools\n"
                "https://matetools.gumroad.com"
            )
        }

        for title, text in sections.items():
            tb.Label(frame, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 0))
            tb.Label(frame, text=text, font=("Segoe UI", 10), wraplength=600, justify="left").pack(anchor="w", pady=(2, 5))

        tb.Button(frame, text="Close", bootstyle="danger-outline", width=15,
                  command=guide_window.destroy).pack(pady=10)

if __name__ == "__main__":
    app = tb.Window(themename="cosmo")
    FileEncryptor(app)
    app.mainloop()
