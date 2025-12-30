import tkinter as tk
from tkinter import filedialog, messagebox
import os
from copy import deepcopy

class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Renamer")
        self.root.geometry("700x700")
        self.root.configure(bg="#1f2f3a")
        self.root.resizable(False, False)

        self.folder_path = ""
        self.files = []
        self.original_files = []
        self.preview_files = []

        self.create_ui()

    def create_ui(self):
        # Title
        tk.Label(self.root, text="File Renamer", font=("Helvetica", 28, "bold"),
                 bg="#1f2f3a", fg="#ffffff").pack(pady=20)

        # Folder selection
        folder_frame = tk.Frame(self.root, bg="#1f2f3a")
        folder_frame.pack(pady=10, fill="x", padx=20)
        tk.Label(folder_frame, text="Select Folder:", font=("Helvetica", 12),
                 bg="#1f2f3a", fg="#bdc3c7").pack(anchor="w")
        self.folder_entry = tk.Entry(folder_frame, font=("Helvetica", 14), bd=0,
                                     highlightthickness=2, highlightbackground="#2980b9", width=50)
        self.folder_entry.pack(side="left", pady=5, ipady=6)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder,
                  bg="#2980b9", fg="white", font=("Helvetica", 12, "bold"), bd=0,
                  width=10, height=2, activebackground="#3498db", cursor="hand2").pack(side="left", padx=5)

        # Options frame
        options_frame = tk.Frame(self.root, bg="#1f2f3a")
        options_frame.pack(pady=10, fill="x", padx=20)

        options_frame = tk.Frame(self.root, bg="#1f2f3a")
        options_frame.pack(pady=10, fill="x", padx=20)

        # Row 0: Prefix and Suffix
        tk.Label(options_frame, text="Prefix:", font=("Helvetica", 12), bg="#1f2f3a", fg="#bdc3c7").grid(row=0, column=0, sticky="w")
        self.prefix_entry = tk.Entry(options_frame, font=("Helvetica", 12), bd=0,
                                     highlightthickness=2, highlightbackground="#27ae60", width=25)
        self.prefix_entry.grid(row=0, column=1, pady=5, padx=5, ipady=4)

        tk.Label(options_frame, text="Suffix:", font=("Helvetica", 12), bg="#1f2f3a", fg="#bdc3c7").grid(row=0, column=2, sticky="w")
        self.suffix_entry = tk.Entry(options_frame, font=("Helvetica", 12), bd=0,
                                     highlightthickness=2, highlightbackground="#27ae60", width=25)
        self.suffix_entry.grid(row=0, column=3, pady=5, padx=5, ipady=4)

        # Row 1: Find and Replace
        tk.Label(options_frame, text="Find:", font=("Helvetica", 12), bg="#1f2f3a", fg="#bdc3c7").grid(row=1, column=0, sticky="w")
        self.find_entry = tk.Entry(options_frame, font=("Helvetica", 12), bd=0,
                                   highlightthickness=2, highlightbackground="#27ae60", width=25)
        self.find_entry.grid(row=1, column=1, pady=5, padx=5, ipady=4)

        tk.Label(options_frame, text="Replace:", font=("Helvetica", 12), bg="#1f2f3a", fg="#bdc3c7").grid(row=1, column=2, sticky="w")
        self.replace_entry = tk.Entry(options_frame, font=("Helvetica", 12), bd=0,
                                      highlightthickness=2, highlightbackground="#27ae60", width=25)
        self.replace_entry.grid(row=1, column=3, pady=5, padx=5, ipady=4)

        # Preview frame
        preview_frame = tk.Frame(self.root, bg="#1f2f3a")
        preview_frame.pack(pady=10, fill="both", expand=True, padx=20)
        tk.Label(preview_frame, text="Preview Files:", font=("Helvetica", 12), bg="#1f2f3a", fg="#bdc3c7").pack(anchor="w")

        self.preview_listbox = tk.Listbox(preview_frame, font=("Helvetica", 12), bg="#2c3e50",
                                          fg="white", selectbackground="#2980b9", selectforeground="white")
        self.preview_listbox.pack(fill="both", expand=True, pady=5)
        scrollbar = tk.Scrollbar(self.preview_listbox, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.preview_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.preview_listbox.yview)

        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="#1f2f3a")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Preview Changes", command=self.preview_changes,
                  bg="#2980b9", fg="white", font=("Helvetica", 12, "bold"),
                  width=20, height=2, bd=0, activebackground="#3498db", cursor="hand2").grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Rename Files", command=self.rename_files,
                  bg="#27ae60", fg="white", font=("Helvetica", 12, "bold"),
                  width=20, height=2, bd=0, activebackground="#2ecc71", cursor="hand2").grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Undo", command=self.undo_rename,
                  bg="#e67e22", fg="white", font=("Helvetica", 12, "bold"),
                  width=20, height=2, bd=0, activebackground="#f39c12", cursor="hand2").grid(row=0, column=2, padx=10)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)
            self.load_files()

    def load_files(self):
        self.files = []
        self.original_files = []
        self.preview_files = []
        self.preview_listbox.delete(0, tk.END)
        for f in os.listdir(self.folder_path):
            full_path = os.path.join(self.folder_path, f)
            if os.path.isfile(full_path):
                self.files.append(f)
        self.original_files = deepcopy(self.files)
        self.update_preview_list(self.files)

    def update_preview_list(self, file_list):
        self.preview_listbox.delete(0, tk.END)
        for f in file_list:
            self.preview_listbox.insert(tk.END, f)

    def preview_changes(self):
        if not self.files:
            messagebox.showerror("Error", "No files to preview.")
            return

        prefix = self.prefix_entry.get()
        suffix = self.suffix_entry.get()
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()

        self.preview_files = []
        for filename in self.files:
            new_name = filename
            if find_text:
                new_name = new_name.replace(find_text, replace_text)
            if prefix:
                new_name = prefix + new_name
            if suffix:
                name, ext = os.path.splitext(new_name)
                new_name = name + suffix + ext
            self.preview_files.append(new_name)

        self.update_preview_list(self.preview_files)

    def rename_files(self):
        if not self.preview_files:
            messagebox.showerror("Error", "Please preview changes first!")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to rename all files?")
        if not confirm:
            return

        try:
            self.last_rename = []  # reset last rename
            for old_name, new_name in zip(self.original_files, self.preview_files):
                old_path = os.path.join(self.folder_path, old_name)
                new_path = os.path.join(self.folder_path, new_name)
                if old_name != new_name:
                    os.rename(old_path, new_path)
                    self.last_rename.append((new_name, old_name))  # store for undo

            messagebox.showinfo("Success", "Files renamed successfully!")
            self.load_files()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename files: {e}")

    def undo_rename(self):
        if not hasattr(self, "last_rename") or not self.last_rename:
            messagebox.showerror("Error", "No rename actions to undo.")
            return

        confirm = messagebox.askyesno("Undo", "Are you sure you want to undo the last rename?")
        if not confirm:
            return

        try:
            for current_name, original_name in self.last_rename:
                current_path = os.path.join(self.folder_path, current_name)
                original_path = os.path.join(self.folder_path, original_name)
                if os.path.exists(current_path):
                    os.rename(current_path, original_path)

            messagebox.showinfo("Success", "Undo successful!")
            self.load_files()
            self.last_rename = []  # clear after undo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to undo rename: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
