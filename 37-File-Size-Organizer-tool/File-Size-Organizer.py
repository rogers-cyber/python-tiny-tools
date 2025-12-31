import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import sv_ttk
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =========================
# Helpers
# =========================
CONFIG_FILE = "folders_data.json"

def load_folders():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_folders():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(folders_data, f, ensure_ascii=False, indent=4)

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

def sanitize_folder_name(name):
    return "".join(c for c in name if c not in r'<>:"/\|?*')

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"

def categorize_file(size):
    if size < 1024*1024:
        return "Small_1MB"
    elif size < 10*1024*1024:
        return "Medium_1-10MB"
    else:
        return "Large_10MB_plus"

# =========================
# App Setup
# =========================
root = TkinterDnD.Tk()
root.title("📂 File Size Organizer Pro - Filter & Sort")
root.geometry("1300x620")

# =========================
# Globals
# =========================
folders_data = load_folders()
last_operation = []
combined_files = []
filtered_files = []
observer = None
current_filter = tk.StringVar(value="All")
current_sort = tk.StringVar(value="Name")

# =========================
# Folder & File Functions
# =========================
def add_folder(path):
    path = path.strip()

    # 1️⃣ Empty validation
    if not path:
        messagebox.showwarning("Invalid Folder", "Please select or enter a folder path.")
        return

    path = os.path.abspath(path)

    # 2️⃣ Directory validation
    if not os.path.isdir(path):
        messagebox.showwarning("Invalid Folder", "The selected path is not a valid folder.")
        return

    # 3️⃣ Duplicate validation
    for folder in folders_data:
        if os.path.abspath(folder) == path:
            messagebox.showinfo("Already Added", "This folder is already being monitored.")
            return

    # 4️⃣ Add folder
    folders_data.append(path)
    save_folders()
    start_watcher(path)
    refresh_combined_preview()
    set_status(f"Added folder: {path}")

def remove_folder(path):
    path = os.path.abspath(path.strip())

    for folder in folders_data:
        if os.path.abspath(folder) == path:
            folders_data.remove(folder)
            save_folders()
            refresh_combined_preview()
            set_status(f"Removed folder: {path}")
            return

    messagebox.showwarning("Not Found", "Folder not found in the list.")

def scan_folder(folder_path):
    folder_path = os.path.abspath(folder_path)
    files = []
    if not os.path.exists(folder_path):
        return files

    for f in os.listdir(folder_path):
        path = os.path.join(folder_path, f)
        if os.path.isfile(path):
            try:
                size = os.path.getsize(path)
            except (FileNotFoundError, PermissionError):
                continue  # file moved or locked, safely skip

            category = sanitize_folder_name(categorize_file(size))
            files.append((folder_path, f, size, category))

    return files

def refresh_combined_preview():
    global combined_files
    combined_files = []
    for folder in folders_data:
        combined_files.extend(scan_folder(folder))
    apply_filter_sort()

# =========================
# Filter & Sort Functions
# =========================
def apply_filter_sort():
    global filtered_files
    # Filter
    if current_filter.get() == "All":
        filtered_files = combined_files.copy()
    else:
        filtered_files = [f for f in combined_files if f[3] == current_filter.get()]
    # Sort
    sort_key = current_sort.get()
    if sort_key == "Name":
        filtered_files.sort(key=lambda x: x[1].lower())
    elif sort_key == "Size":
        filtered_files.sort(key=lambda x: x[2])
    elif sort_key == "Folder":
        filtered_files.sort(key=lambda x: x[0].lower())
    elif sort_key == "Category":
        filtered_files.sort(key=lambda x: x[3].lower())
    update_file_tree()

def update_file_tree():
    file_tree.delete(*file_tree.get_children())
    counts = {"Small_1MB":0, "Medium_1-10MB":0, "Large_10MB_plus":0}
    for folder, f, size, category in filtered_files:
        file_tree.insert("", "end", values=(folder, f, format_size(size), category))
        if category in counts:
            counts[category] +=1
    total_files_var.set(f"Total Files: {len(filtered_files)} | Small: {counts['Small_1MB']} | Medium: {counts['Medium_1-10MB']} | Large: {counts['Large_10MB_plus']}")

# =========================
# File Operations
# =========================
def organize_files_thread():
    global watcher_paused
    watcher_paused = True
    progress_var.set(0)

    if not combined_files:
        watcher_paused = False
        return

    global last_operation
    last_operation = []
    total = len(combined_files)

    for idx, (folder, f, size, category) in enumerate(combined_files, start=1):
        src = os.path.join(folder, f)
        dst_folder = os.path.join(folder, category)
        os.makedirs(dst_folder, exist_ok=True)
        dst = os.path.join(dst_folder, f)

        try:
            shutil.move(src, dst)
            last_operation.append((dst, src))
        except Exception:
            pass

        progress_var.set(int(idx / total * 100))
        root.update_idletasks()

    watcher_paused = False
    refresh_combined_preview()
    set_status("Files organized successfully!")

def organize_files():
    Thread(target=organize_files_thread, daemon=True).start()

def undo_last_operation():
    if not last_operation:
        messagebox.showinfo("Nothing to undo", "No operation to undo.")
        return
    for dst, src in reversed(last_operation):
        if os.path.exists(dst):
            shutil.move(dst, src)
    last_operation.clear()
    refresh_combined_preview()
    set_status("Undo completed!")

# =========================
# Drag & Drop
# =========================
def drop(event):
    paths = root.tk.splitlist(event.data)
    for path in paths:
        if os.path.isdir(path):
            add_folder(path)

# =========================
# Watchdog Handler
# =========================
class FolderEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if watcher_paused:
            return
        root.after(200, refresh_combined_preview)

def start_watcher(folder_path):
    global observer
    if observer is None:
        observer = Observer()
        observer.start()
    handler = FolderEventHandler()
    observer.schedule(handler, folder_path, recursive=True)

# =========================
# GUI Setup
# =========================
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")

ttk.Label(main_frame, text="📂 File Size Organizer Pro - Filter & Sort", font=("Segoe UI", 22, "bold")).pack(pady=(0,5))
ttk.Label(main_frame, text="Drag folders or add manually. Files auto-update in real-time.", font=("Segoe UI", 12)).pack(pady=(0,10))

# Folder selection and management
folder_frame = ttk.LabelFrame(main_frame, text="Folders", padding=10)
folder_frame.pack(fill="x", pady=5)

folder_entry = tk.Entry(folder_frame, width=80)
folder_entry.grid(row=0, column=0, padx=5)

def browse_folder():
    path = filedialog.askdirectory()
    if path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, path)

ttk.Button(folder_frame, text="Browse", command=browse_folder).grid(row=0, column=1, padx=5)
ttk.Button(folder_frame, text="Add Folder", style="Manage.TButton", command=lambda:add_folder(folder_entry.get().strip())).grid(row=0, column=2, padx=5)
ttk.Button(folder_frame, text="Remove Folder", style="Undo.TButton", command=lambda: remove_folder(folder_entry.get().strip())).grid(row=0, column=3, padx=5)

# Buttons styles
ttk.Style().configure("Organize.TButton", foreground="black", background="#4CAF50")
ttk.Style().configure("Undo.TButton", foreground="black", background="#FF9800")
ttk.Style().configure("Manage.TButton", foreground="black", background="#2196F3")

ttk.Button(folder_frame, text="📂 Organize Files", style="Organize.TButton", command=organize_files).grid(row=0, column=4, padx=5)
ttk.Button(folder_frame, text="↩️ Undo Last", style="Undo.TButton", command=undo_last_operation).grid(row=0, column=5, padx=5)

# Filter & Sort Panel
filter_sort_frame = ttk.LabelFrame(main_frame, text="Filter & Sort", padding=10)
filter_sort_frame.pack(fill="x", pady=5)

ttk.Label(filter_sort_frame, text="Filter by Category:").grid(row=0, column=0, padx=5)
filter_combo = ttk.Combobox(filter_sort_frame, state="readonly", width=20, textvariable=current_filter)
filter_combo['values'] = ["All", "Small_1MB", "Medium_1-10MB", "Large_10MB_plus"]
filter_combo.current(0)
filter_combo.grid(row=0, column=1, padx=5)
filter_combo.bind("<<ComboboxSelected>>", lambda e: apply_filter_sort())

ttk.Label(filter_sort_frame, text="Sort by:").grid(row=0, column=2, padx=5)
sort_combo = ttk.Combobox(filter_sort_frame, state="readonly", width=20, textvariable=current_sort)
sort_combo['values'] = ["Name", "Size", "Folder", "Category"]
sort_combo.current(0)
sort_combo.grid(row=0, column=3, padx=5)
sort_combo.bind("<<ComboboxSelected>>", lambda e: apply_filter_sort())

# File preview Treeview
tree_frame = ttk.Frame(main_frame)
tree_frame.pack(expand=True, fill="both", pady=10)
columns = ("folder", "name", "size", "category")
file_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
file_tree.heading("folder", text="Folder")
file_tree.heading("name", text="File Name")
file_tree.heading("size", text="Size")
file_tree.heading("category", text="Category")
file_tree.column("folder", width=300)
file_tree.column("name", width=400)
file_tree.column("size", width=100)
file_tree.column("category", width=150)
file_tree.pack(expand=True, fill="both", side="left")

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=file_tree.yview)
scrollbar.pack(side="right", fill="y")
file_tree.configure(yscrollcommand=scrollbar.set)

# File counts
total_files_var = tk.StringVar(value="Total Files: 0 | Small: 0 | Medium: 0 | Large: 0")
ttk.Label(main_frame, textvariable=total_files_var, font=("Segoe UI", 12)).pack()

# Progress bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", maximum=100, variable=progress_var)
progress_bar.pack(fill="x", pady=5)

# Drag & Drop binding
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

# Status Bar
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side="bottom", fill="x")

# Initial load and start watchers
for folder in folders_data:
    start_watcher(folder)
refresh_combined_preview()

# Run App
try:
    root.mainloop()
finally:
    if observer:
        observer.stop()
        observer.join()
