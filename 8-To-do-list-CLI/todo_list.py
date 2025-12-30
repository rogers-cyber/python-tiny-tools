import sys
import os
import csv
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

TODO_FILE = resource_path("todo_list.csv")
tasks = []

def save_tasks():
    try:
        with open(TODO_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            for task in tasks:
                writer.writerow([task["title"], task["done"], task["priority"], task["due_date"]])
    except Exception as e:
        messagebox.showerror("Error", f"Saving tasks failed: {e}")

def load_tasks():
    if not os.path.exists(TODO_FILE):
        return
    try:
        with open(TODO_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 4:
                    due_date = row[3].strip()
                    # Normalize date to YYYY-MM-DD
                    if due_date:
                        try:
                            # Try existing YYYY-MM-DD
                            datetime.strptime(due_date, "%Y-%m-%d")
                        except:
                            try:
                                # Try MM/DD/YYYY and convert
                                dt = datetime.strptime(due_date, "%m/%d/%Y")
                                due_date = dt.strftime("%Y-%m-%d")
                            except:
                                # Invalid format, ignore
                                due_date = ""
                    tasks.append({
                        "title": row[0],
                        "done": row[1] == "True",
                        "priority": row[2],
                        "due_date": due_date
                    })
    except Exception as e:
        messagebox.showerror("Error", f"Loading tasks failed: {e}")

def get_filtered_sorted_tasks(filter_type=None, sort_by=None, search_text=""):
    filtered = tasks
    today_str = date.today().strftime("%Y-%m-%d")

    # Filters
    if filter_type == "today":
        filtered = [t for t in filtered if t["due_date"] == today_str]
    elif filter_type == "overdue":
        filtered = [t for t in filtered if t["due_date"] and t["due_date"] < today_str and not t["done"]]
    elif filter_type == "high":
        filtered = [t for t in filtered if t["priority"] == "High"]

    # Search
    if search_text:
        filtered = [t for t in filtered if search_text.lower() in t["title"].lower()]

    # Sorting
    if sort_by == "due":
        filtered.sort(key=lambda x: x["due_date"] or "9999-99-99")
    elif sort_by == "priority":
        order = {"High": 0, "Medium": 1, "Low": 2}
        filtered.sort(key=lambda x: order.get(x["priority"], 3))

    return filtered

# =========================
# GUI Functions
# =========================
def refresh_treeview(*args):
    for row in tree.get_children():
        tree.delete(row)
    filter_type = filter_var.get()
    sort_by = sort_var.get()
    search_text = search_var.get()
    for task in get_filtered_sorted_tasks(filter_type, sort_by, search_text):
        due_display = task["due_date"] if task["due_date"] else "—"
        tree.insert("", "end", values=(
            task["title"], 
            "✅" if task["done"] else "❌", 
            task["priority"], 
            due_display
        ))
        # Color coding
        tags = []
        if task["done"]:
            tags.append("done")
        elif task["priority"] == "High":
            tags.append("high")
        elif task["priority"] == "Medium":
            tags.append("medium")
        elif task["priority"] == "Low":
            tags.append("low")
        if task["due_date"]:
            due_dt = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            if due_dt < date.today() and not task["done"]:
                tags.append("overdue")
        tree.item(tree.get_children()[-1], tags=tags)

def add_task():
    title = title_entry.get().strip()
    if not title:
        messagebox.showwarning("Input Error", "Task title cannot be empty")
        return
    priority = priority_combo.get()
    due_date = due_entry.get().strip()
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except:
            messagebox.showwarning("Input Error", "Invalid due date format. Use YYYY-MM-DD")
            return
    tasks.append({"title": title, "done": False, "priority": priority, "due_date": due_date})
    save_tasks()
    refresh_treeview()
    title_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)

def remove_task():
    selected = tree.selection()
    if not selected: return
    idx = tree.index(selected[0])
    removed = tasks.pop(idx)
    save_tasks()
    refresh_treeview()
    messagebox.showinfo("🗑️ Removed", f"Removed task: {removed['title']}")

def mark_done():
    selected = tree.selection()
    if not selected: return
    idx = tree.index(selected[0])
    tasks[idx]["done"] = True
    save_tasks()
    refresh_treeview()

def clear_all_tasks():
    if messagebox.askyesno("⚠️ Clear All", "Are you sure you want to remove all tasks?"):
        tasks.clear()
        save_tasks()
        refresh_treeview()

def export_tasks():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file","*.csv"),("Text file","*.txt")])
    if not file_path: return
    try:
        if file_path.endswith(".csv"):
            with open(file_path,"w",newline="") as f:
                writer = csv.writer(f)
                for task in tasks:
                    writer.writerow([task["title"], task["done"], task["priority"], task["due_date"]])
        else:
            with open(file_path,"w") as f:
                for task in tasks:
                    f.write(f"{task['title']} | {'Done' if task['done'] else 'Pending'} | {task['priority']} | {task['due_date'] or '—'}\n")
        messagebox.showinfo("💾 Exported", f"Tasks exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Export failed: {e}")

# =========================
# GUI Setup
# =========================
root = tk.Tk()
root.title("ToDoMate 📝")
root.geometry("950x600")
root.configure(bg="#f0f4f8")

# Notebook
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ---------------- Dashboard Tab ----------------
dash_tab = ttk.Frame(notebook, padding=20)
notebook.add(dash_tab, text="🏠 Dashboard")

ttk.Label(dash_tab, text="ToDoMate 📝", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0,10))
ttk.Label(dash_tab, text="A modern productivity tool to manage your tasks efficiently with priorities, due dates, filters, and sorting.", wraplength=750, font=("Segoe UI",12)).pack(anchor="w", pady=(0,15))

ttk.Label(dash_tab, text="✨ Key Features:", font=("Segoe UI",14,"bold")).pack(anchor="w", pady=(10,5))
features = [
    "🗂️ Two-tab interface: Dashboard & To-Do List",
    "✅ Add, remove, mark tasks as done",
    "📅 Priority levels and due dates with color coding",
    "🔍 Filters: Today, Overdue, High-priority",
    "🔎 Search tasks by title",
    "↕ Sort tasks by due date or priority",
    "💾 Export tasks to CSV or TXT"
]
for feat in features:
    ttk.Label(dash_tab, text=feat, font=("Segoe UI",11)).pack(anchor="w")

ttk.Label(dash_tab, text="About Developer:", font=("Segoe UI",14,"bold")).pack(anchor="w", pady=(20,5))
ttk.Label(dash_tab, text="MateTools – Practical and user-friendly digital tools for productivity.\nWebsite: https://matetools.gumroad.com", wraplength=750, font=("Segoe UI",11)).pack(anchor="w")

# ---------------- To-Do Tab ----------------
todo_tab = ttk.Frame(notebook, padding=10)
notebook.add(todo_tab, text="📝 To-Do List")

# Form frame
form_frame = ttk.LabelFrame(todo_tab, text="➕ Add New Task", padding=10)
form_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
title_entry = ttk.Entry(form_frame, width=40)
title_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Priority:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
priority_combo = ttk.Combobox(form_frame, values=["High","Medium","Low"], width=10)
priority_combo.set("Medium")
priority_combo.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(form_frame, text="Due Date:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
due_entry = ttk.Entry(form_frame, width=15)
due_entry.grid(row=0, column=5, padx=5, pady=5)
ttk.Label(form_frame, text="YYYY-MM-DD").grid(row=0, column=6, sticky="w", padx=2)

ttk.Button(form_frame, text="✅ Add Task", command=add_task, style="Accent.TButton").grid(row=0, column=7, padx=5, pady=5)

# Toolbar frame
toolbar_frame = ttk.Frame(todo_tab)
toolbar_frame.pack(fill="x", padx=10, pady=5)

ttk.Button(toolbar_frame, text="🗑️ Remove", command=remove_task, style="Accent.TButton").pack(side="left", padx=5)
ttk.Button(toolbar_frame, text="✅ Done", command=mark_done, style="Accent.TButton").pack(side="left", padx=5)
ttk.Button(toolbar_frame, text="⚠️ Clear All", command=clear_all_tasks, style="Accent.TButton").pack(side="left", padx=5)
ttk.Button(toolbar_frame, text="💾 Export", command=export_tasks, style="Accent.TButton").pack(side="left", padx=5)

ttk.Label(toolbar_frame, text="Filter:").pack(side="left", padx=(20,5))
filter_var = tk.StringVar(value="all")
filter_menu = ttk.Combobox(toolbar_frame, textvariable=filter_var, values=["all","today","overdue","high"], width=10)
filter_menu.pack(side="left", padx=5)
filter_menu.bind("<<ComboboxSelected>>", refresh_treeview)

ttk.Label(toolbar_frame, text="Sort by:").pack(side="left", padx=(20,5))
sort_var = tk.StringVar(value="none")
sort_menu = ttk.Combobox(toolbar_frame, textvariable=sort_var, values=["none","due","priority"], width=10)
sort_menu.pack(side="left", padx=5)
sort_menu.bind("<<ComboboxSelected>>", refresh_treeview)

ttk.Label(toolbar_frame, text="🔎 Search:").pack(side="left", padx=(20,5))
search_var = tk.StringVar()
search_var.trace("w", refresh_treeview)
search_entry = ttk.Entry(toolbar_frame, textvariable=search_var, width=20)
search_entry.pack(side="left", padx=5)

# Treeview frame
tree_frame = ttk.Frame(todo_tab)
tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("Title", "Status", "Priority", "Due Date")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200, anchor="center")
tree.pack(fill="both", expand=True)

# Color tags
tree.tag_configure("done", foreground="gray")
tree.tag_configure("high", background="#ffcccc")
tree.tag_configure("medium", background="#fff0b3")
tree.tag_configure("low", background="#ccffcc")
tree.tag_configure("overdue", foreground="red")

# =========================
# Style
# =========================
style = ttk.Style(root)

# Modern accent buttons with readable text
style.configure("Accent.TButton",
                foreground="#000000",  # dark text
                background="#ffd966",  # light yellow background
                font=("Segoe UI", 10, "bold"),
                padding=5)
style.map("Accent.TButton",
          foreground=[("active", "#000000")],
          background=[("active", "#ffbf00")])  # darker yellow on hover

# =========================
# Load tasks and run
# =========================
load_tasks()
refresh_treeview()
root.mainloop()
