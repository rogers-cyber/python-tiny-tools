import threading
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ---------------- GLOBALS ---------------- #
url_list = []

# ---------------- FUNCTIONS ---------------- #
def add_urls():
    """Add URLs from entry (comma separated)"""
    urls = url_entry.get().strip()
    if not urls:
        return
    for url in urls.split(","):
        url = url.strip()
        if url and url not in url_list:
            url_list.append(url)
            tree.insert("", tk.END, iid=url, values=(url, "Pending"), tags=("pending",))
    url_entry.delete(0, tk.END)

def remove_selected():
    """Remove selected URLs from Treeview and list"""
    selected = tree.selection()
    for url in selected:
        url_list.remove(url)
        tree.delete(url)

def check_status(url):
    """Check HTTP status and update Treeview row"""
    try:
        response = requests.get(url, timeout=5)
        status_text = f"{response.status_code} {response.reason}"
        color_tag = "ok" if response.status_code == 200 else "error"
    except requests.exceptions.RequestException as e:
        status_text = f"Error: {str(e)}"
        color_tag = "error"
    # Update treeview row safely
    tree.item(url, values=(url, status_text), tags=(color_tag,))

def check_all_urls():
    """Start threads to check all URLs"""
    for url in url_list:
        tree.item(url, values=(url, "Checking..."), tags=("checking",))
        threading.Thread(target=check_status, args=(url,), daemon=True).start()

def save_results():
    """Save URL status results to a text file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )
    if not file_path:
        return
    with open(file_path, "w") as f:
        for url in url_list:
            status = tree.item(url)["values"][1]
            f.write(f"{url} → {status}\n")
    messagebox.showinfo("Saved", f"Results saved to {file_path}")

# ---------------- GUI ---------------- #
app = tb.Window(themename="darkly", title="Live URL Status Checker", size=(800, 500))

# Input Frame
input_frame = tb.Frame(app)
input_frame.pack(fill=tk.X, padx=10, pady=10)
url_entry = tb.Entry(input_frame, width=60)
url_entry.pack(side=tk.LEFT, padx=5)
tb.Button(input_frame, text="Add URL(s)", bootstyle="primary", command=add_urls).pack(side=tk.LEFT, padx=5)
tb.Button(input_frame, text="Remove Selected", bootstyle="danger", command=remove_selected).pack(side=tk.LEFT, padx=5)

# Treeview Frame
tree_frame = tb.Frame(app)
tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
tree = tb.Treeview(tree_frame, columns=("URL", "Status"), show="headings", height=15)
tree.heading("URL", text="URL")
tree.heading("Status", text="Status")
tree.column("URL", width=500)
tree.column("Status", width=200)
tree.pack(fill=tk.BOTH, expand=True)

# Tag colors
tree.tag_configure("pending", background="#444444", foreground="white")
tree.tag_configure("checking", background="#666666", foreground="yellow")
tree.tag_configure("ok", background="#1abc9c", foreground="black")   # greenish
tree.tag_configure("error", background="#e74c3c", foreground="white") # red

# Controls Frame
control_frame = tb.Frame(app)
control_frame.pack(pady=10)
tb.Button(control_frame, text="Check Status", bootstyle="success", command=check_all_urls).pack(side=tk.LEFT, padx=5)
tb.Button(control_frame, text="Save Results", bootstyle="info", command=save_results).pack(side=tk.LEFT, padx=5)

app.mainloop()
