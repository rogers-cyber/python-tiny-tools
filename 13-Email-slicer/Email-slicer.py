import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sv_ttk
import re
import csv

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("Advanced Email Slicer")
root.geometry("950x650")
root.iconbitmap("")  # Add path to your icon if needed

sv_ttk.set_theme("light")  # Default theme

# =========================
# Globals
# =========================
sliced_emails = []  # List of tuples (username, domain)

# =========================
# Helpers
# =========================
def slice_email(email):
    """Return username and domain if valid, else None"""
    email = email.strip()
    pattern = r"^[\w\.\-]+@[\w\.\-]+\.\w+$"
    if re.match(pattern, email):
        username, domain = email.split("@")
        return username, domain
    return None

def check_emails():
    input_text = email_entry.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showerror("Invalid Input", "Enter at least one email address.")
        return
    
    emails = re.split(r"[,\s]+", input_text)
    invalid_emails = []
    count_new = 0

    for email in emails:
        if email:
            result = slice_email(email)
            if result:
                sliced_emails.append(result)
                count_new += 1
            else:
                invalid_emails.append(email)
    
    update_results()
    email_entry.delete("1.0", tk.END)

    if invalid_emails:
        messagebox.showwarning(
            "Invalid Emails",
            f"The following emails are invalid and were skipped:\n{', '.join(invalid_emails)}"
        )
    elif count_new > 0:
        messagebox.showinfo("Success", f"{count_new} emails processed successfully!")

def update_results():
    result_text.configure(state="normal")
    result_text.delete("1.0", tk.END)
    for username, domain in sliced_emails:
        result_text.insert(tk.END, f"📧 Username: {username} | Domain: {domain}\n")
    result_text.configure(state="disabled")

def clear_history():
    sliced_emails.clear()
    update_results()

def copy_results():
    root.clipboard_clear()
    root.clipboard_append(result_text.get("1.0", tk.END))
    messagebox.showinfo("Copied", "Results copied to clipboard.")

def export_to_csv():
    if not sliced_emails:
        messagebox.showwarning("No Data", "No emails to export. Please slice some emails first.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save CSV"
    )
    if file_path:
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Username", "Domain"])
                for username, domain in sliced_emails:
                    writer.writerow([username, domain])
            messagebox.showinfo("Exported", f"Results successfully exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")

# =========================
# Styles
# =========================
style = ttk.Style()
style.theme_use("clam")

style.configure("Action.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#4CAF50", padding=8)
style.map("Action.TButton", background=[("active", "#45a049"), ("disabled", "#a5d6a7")])

style.configure("Secondary.TButton", font=("Segoe UI", 11, "bold"),
                foreground="white", background="#2196F3", padding=8)
style.map("Secondary.TButton", background=[("active", "#1976D2"), ("disabled", "#90caf9")])

# =========================
# Layout
# =========================
top_frame = ttk.Frame(root, padding=20)
top_frame.pack(fill="x")

ttk.Label(top_frame, text="Advanced Email Slicer", font=("Segoe UI", 20, "bold")).pack(anchor="w")
ttk.Label(
    top_frame,
    text="Enter one or more email addresses (comma, space, or newline separated) to slice username and domain.",
    font=("Segoe UI", 11)
).pack(anchor="w", pady=(0,10))

input_frame = ttk.Frame(root, padding=10)
input_frame.pack(fill="x")

ttk.Label(input_frame, text="Emails:", font=("Segoe UI", 12)).pack(anchor="w", pady=(0,5))
email_entry = scrolledtext.ScrolledText(input_frame, height=6, font=("Segoe UI", 12))
email_entry.pack(fill="x", pady=(0,5))

button_frame = ttk.Frame(root, padding=10)
button_frame.pack(fill="x")
ttk.Button(button_frame, text="Slice Emails", command=check_emails, style="Action.TButton").pack(side="left", padx=5)
ttk.Button(button_frame, text="Clear History", command=clear_history, style="Secondary.TButton").pack(side="left", padx=5)
ttk.Button(button_frame, text="Copy Results", command=copy_results, style="Secondary.TButton").pack(side="left", padx=5)
ttk.Button(button_frame, text="Export CSV", command=export_to_csv, style="Secondary.TButton").pack(side="left", padx=5)

result_frame = ttk.LabelFrame(root, text="Results", padding=15)
result_frame.pack(fill="both", expand=True, padx=20, pady=20)

result_text = scrolledtext.ScrolledText(result_frame, state="disabled", font=("Consolas", 12))
result_text.pack(fill="both", expand=True)

# =========================
# Run App
# =========================
root.mainloop()
