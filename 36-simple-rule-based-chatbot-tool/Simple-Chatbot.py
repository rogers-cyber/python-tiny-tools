import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sv_ttk

# =========================
# Helpers
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

QA_FILE = "qa_data.json"

def load_qa():
    if os.path.exists(QA_FILE):
        with open(QA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return [
            {"condo": "Condo A", "category": "Sell", "question": "Sell Condo", "response": "We can assist with selling Condo A."},
            {"condo": "Condo A", "category": "Rent", "question": "Rent Condo", "response": "We can list Condo A for rent."},
            {"condo": "Condo B", "category": "Price", "question": "Price", "response": "Condo B prices vary by floor and size."},
            {"condo": "Condo B", "category": "Service Fee", "question": "Service Fee", "response": "Service fee depends on condo type."},
            {"condo": "Condo C", "category": "Facilities", "question": "Facilities", "response": "Condo C has gym, pool, and security."},
        ]

def save_qa():
    with open(QA_FILE, "w", encoding="utf-8") as f:
        json.dump(qa_data, f, ensure_ascii=False, indent=4)

def set_status(msg):
    status_var.set(msg)
    root.update_idletasks()

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("💬 Condo Assistant Bot")
root.geometry("1180x650")
sv_ttk.set_theme("light")

# =========================
# Globals
# =========================
qa_data = load_qa()
dark_mode_var = tk.BooleanVar(value=False)

# =========================
# Helper Functions
# =========================
def get_condos(): return sorted(list({qa["condo"] for qa in qa_data}))
def get_categories(condo): return sorted(list({qa["category"] for qa in qa_data if qa["condo"] == condo}))
def get_questions(condo, category): return [qa["question"] for qa in qa_data if qa["condo"] == condo and qa["category"] == category]
def get_response(condo, category, question):
    for qa in qa_data:
        if qa["condo"] == condo and qa["category"] == category and qa["question"] == question:
            return qa["response"]
    return "No response found."

# =========================
# Chat Functions with Bubble Styling
# =========================
def insert_bubble(message, sender="user"):
    chat_text.config(state="normal")
    if sender == "user":
        chat_text.insert(tk.END, f"  {message}  \n\n", "user_bubble")
    else:
        chat_text.insert(tk.END, f"  {message}  \n\n", "bot_bubble")
    chat_text.see(tk.END)
    chat_text.config(state="disabled")

def update_category_dropdown(event=None):
    selected_condo = condo_combo.get()
    categories = get_categories(selected_condo)
    category_combo['values'] = categories
    if categories:
        category_combo.current(0)
    update_question_dropdown()

def update_question_dropdown(event=None):
    selected_condo = condo_combo.get()
    selected_category = category_combo.get()
    questions = get_questions(selected_condo, selected_category)
    question_combo['values'] = questions
    if questions:
        question_combo.current(0)

def send_message():
    condo = condo_combo.get()
    category = category_combo.get()
    question = question_combo.get()
    if not (condo and category and question):
        messagebox.showwarning("Incomplete Selection", "Please select condo, category, and question.")
        return
    response = get_response(condo, category, question)
    insert_bubble(f"You: {condo} | {category} | {question}", "user")
    insert_bubble(f"Bot: {response}", "bot")
    set_status(f"Responded to: {question}")

# =========================
# Admin Functions with Top Add Section
# =========================
def manage_qa_ui():
    admin_win = tk.Toplevel(root)
    admin_win.title("Manage Q&A")
    admin_win.geometry("1050x550")
    admin_win.resizable(False, False)

    # Make it modal
    admin_win.transient(root)  # Keep above main window
    admin_win.grab_set()       # Block interaction with main window

    # Add New Q&A Above Tree
    add_frame = ttk.LabelFrame(admin_win, text="➕ Add New Q&A", padding=10)
    add_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(add_frame, text="Condo:").grid(row=0, column=0, padx=5, pady=2)
    new_condo = tk.Entry(add_frame, width=15)
    new_condo.grid(row=0, column=1, padx=5)

    ttk.Label(add_frame, text="Category:").grid(row=0, column=2, padx=5, pady=2)
    new_category = tk.Entry(add_frame, width=15)
    new_category.grid(row=0, column=3, padx=5)

    ttk.Label(add_frame, text="Question:").grid(row=0, column=4, padx=5, pady=2)
    new_question = tk.Entry(add_frame, width=25)
    new_question.grid(row=0, column=5, padx=5)

    ttk.Label(add_frame, text="Response:").grid(row=0, column=6, padx=5, pady=2)
    new_response = tk.Entry(add_frame, width=35)
    new_response.grid(row=0, column=7, padx=5)

    def add_new_qa():
        condo_val = new_condo.get().strip()
        category_val = new_category.get().strip()
        question_val = new_question.get().strip()
        response_val = new_response.get().strip()
        if condo_val and category_val and question_val and response_val:
            qa_data.append({"condo": condo_val, "category": category_val, "question": question_val, "response": response_val})
            save_qa()
            refresh_tree()
            new_condo.delete(0, tk.END)
            new_category.delete(0, tk.END)
            new_question.delete(0, tk.END)
            new_response.delete(0, tk.END)
            set_status(f"Added Q&A: {question_val}")
        else:
            messagebox.showwarning("Incomplete", "Fill all fields to add Q&A.")

    ttk.Button(add_frame, text="Add Q&A", command=add_new_qa).grid(row=0, column=8, padx=5)

    # Treeview Section
    tree_frame = ttk.Frame(admin_win)
    tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
    columns = ("condo", "category", "question", "response")
    global tree
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150 if col != "response" else 350)
    tree.pack(expand=True, fill="both", side="left")
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    def refresh_tree():
        tree.delete(*tree.get_children())
        for qa in qa_data:
            tree.insert("", "end", values=(qa["condo"], qa["category"], qa["question"], qa["response"]))
        condo_combo['values'] = get_condos()
        update_category_dropdown()
        save_qa()

    def update_selected_qa():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a Q&A to update.")
            return
        idx = tree.index(selected[0])
        qa = qa_data[idx]

        condo_val = simpledialog.askstring("Update Q&A", "Condo:", initialvalue=qa["condo"])
        category_val = simpledialog.askstring("Update Q&A", "Category:", initialvalue=qa["category"])
        question_val = simpledialog.askstring("Update Q&A", "Question:", initialvalue=qa["question"])
        response_val = simpledialog.askstring("Update Q&A", "Response:", initialvalue=qa["response"])

        if condo_val and category_val and question_val and response_val:
            qa_data[idx] = {"condo": condo_val, "category": category_val, "question": question_val, "response": response_val}
            save_qa()
            refresh_tree()
            set_status(f"Updated Q&A: {question_val}")

    ttk.Button(admin_win, text="✏️ Update Selected Q&A", command=update_selected_qa).pack(pady=5)

    refresh_tree()

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
style.configure("Ask.TButton", foreground="white", background="#2196F3")
style.configure("Update.TButton", foreground="white", background="#FF9800")

# Bubble tags
chat_text = tk.Text(root, wrap="word", state="disabled", font=("Segoe UI", 12), bg="#f5f5f5")
chat_text.tag_configure("user_bubble", background="#DCF8C6", foreground="black", spacing3=5, lmargin1=30, rmargin=5)
chat_text.tag_configure("bot_bubble", background="#FFFFFF", foreground="black", spacing3=5, lmargin1=5, rmargin=30)

# =========================
# Main UI
# =========================
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")

ttk.Label(main_frame, text="💬 Condo Assistant Bot",
          font=("Segoe UI", 22, "bold")).pack(pady=(0,5))
ttk.Label(main_frame, text="Select Condo, Category, and Question to ask",
          font=("Segoe UI", 12)).pack(pady=(0,10))

# Input Frame
input_frame = ttk.LabelFrame(main_frame, text="Ask a Question", padding=10)
input_frame.pack(fill="x", pady=8)

ttk.Label(input_frame, text="Condo:").grid(row=0, column=0, padx=5, pady=2)
condo_combo = ttk.Combobox(input_frame, state="readonly", width=20)
condo_combo.grid(row=0, column=1, padx=5)
condo_combo['values'] = get_condos()
if condo_combo['values']:
    condo_combo.current(0)

ttk.Label(input_frame, text="Category:").grid(row=0, column=2, padx=5)
category_combo = ttk.Combobox(input_frame, state="readonly", width=20)
category_combo.grid(row=0, column=3, padx=5)

ttk.Label(input_frame, text="Question:").grid(row=0, column=4, padx=5)
question_combo = ttk.Combobox(input_frame, state="readonly", width=30)
question_combo.grid(row=0, column=5, padx=5)

condo_combo.bind("<<ComboboxSelected>>", update_category_dropdown)
category_combo.bind("<<ComboboxSelected>>", update_question_dropdown)
update_category_dropdown()
update_question_dropdown()

ttk.Button(input_frame, text="💬 Ask", command=send_message, style="Ask.TButton").grid(row=0, column=6, padx=5)

# Options
options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
options_frame.pack(fill="x", pady=8)
ttk.Button(options_frame, text="Manage Q&A", command=manage_qa_ui, style="Update.TButton").pack(side="right")

# =========================
# Chat Frame with Scrollbar
# =========================
chat_frame = ttk.Frame(main_frame)
chat_frame.pack(expand=True, fill="both", pady=10)

# Chat Text widget
chat_text = tk.Text(
    chat_frame,
    wrap="word",
    state="disabled",
    font=("Segoe UI", 12),
    bg="#f5f5f5",
    relief="flat",
    padx=10,
    pady=10
)
chat_text.pack(side="left", expand=True, fill="both")

# Scrollbar
scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=chat_text.yview)
scrollbar.pack(side="right", fill="y")
chat_text.configure(yscrollcommand=scrollbar.set)

# Bubble styling
chat_text.tag_configure(
    "user_bubble",
    background="#DCF8C6",
    foreground="black",
    spacing3=5,
    lmargin1=30,
    rmargin=5,
    font=("Segoe UI", 12)
)
chat_text.tag_configure(
    "bot_bubble",
    background="#FFFFFF",
    foreground="black",
    spacing3=5,
    lmargin1=5,
    rmargin=30,
    font=("Segoe UI", 12)
)


# Status Bar
status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill="x")

# =========================
# Run App
# =========================
root.mainloop()
