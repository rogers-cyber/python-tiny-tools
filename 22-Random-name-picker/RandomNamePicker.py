import tkinter as tk
from tkinter import filedialog, messagebox
import random
import os

class RandomNamePickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Name Picker")
        self.root.geometry("700x750")
        self.root.configure(bg="#1f2f3a")
        self.root.resizable(False, False)

        self.names = []
        self.file_path = None

        self.create_ui()

    def create_ui(self):
        # Title
        tk.Label(self.root, text="Random Name Picker", font=("Helvetica", 28, "bold"),
                 bg="#1f2f3a", fg="#ffffff").pack(pady=20)

        # Input frame
        input_frame = tk.Frame(self.root, bg="#1f2f3a")
        input_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(input_frame, text="Enter Name:", font=("Helvetica", 12), 
                 bg="#1f2f3a", fg="#bdc3c7").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(input_frame, font=("Helvetica", 12), bd=0, 
                                   highlightthickness=2, highlightbackground="#27ae60", width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5, ipady=12)

        tk.Button(input_frame, text="Add Name", command=self.add_name,
                  bg="#2980b9", fg="white", font=("Helvetica", 12, "bold"),
                  width=12, height=2, bd=0, activebackground="#3498db", cursor="hand2").grid(row=0, column=2, padx=5)

        # Names listbox
        list_frame = tk.Frame(self.root, bg="#1f2f3a")
        list_frame.pack(pady=10, fill="both", expand=True, padx=20)
        tk.Label(list_frame, text="Names List:", font=("Helvetica", 12), bg="#1f2f3a", fg="#bdc3c7").pack(anchor="w")

        self.listbox = tk.Listbox(list_frame, font=("Helvetica", 12), bg="#2c3e50",
                                  fg="white", selectbackground="#2980b9", selectforeground="white")
        self.listbox.pack(fill="both", expand=True, pady=5)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="#1f2f3a")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Pick Random Name", command=self.pick_random_name,
                  bg="#27ae60", fg="white", font=("Helvetica", 12, "bold"),
                  width=20, height=2, bd=0, activebackground="#2ecc71", cursor="hand2").grid(row=0, column=0, padx=10, pady=5)

        tk.Button(btn_frame, text="Pick Multiple Names", command=self.pick_multiple_names,
                  bg="#2980b9", fg="white", font=("Helvetica", 12, "bold"),
                  width=20, height=2, bd=0, activebackground="#3498db", cursor="hand2").grid(row=0, column=1, padx=10, pady=5)

        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected,
                  bg="#e67e22", fg="white", font=("Helvetica", 12, "bold"),
                  width=20, height=2, bd=0, activebackground="#f39c12", cursor="hand2").grid(row=1, column=0, padx=10, pady=5)

        tk.Button(btn_frame, text="Clear All", command=self.clear_all,
                  bg="#c0392b", fg="white", font=("Helvetica", 12, "bold"),
                  width=20, height=2, bd=0, activebackground="#e74c3c", cursor="hand2").grid(row=1, column=1, padx=10, pady=5)

        # File operations frame
        file_frame = tk.Frame(self.root, bg="#1f2f3a")
        file_frame.pack(pady=10)

        tk.Button(file_frame, text="Load Names from File", command=self.load_from_file,
                  bg="#8e44ad", fg="white", font=("Helvetica", 12, "bold"),
                  width=25, height=2, bd=0, activebackground="#9b59b6", cursor="hand2").grid(row=0, column=0, padx=10, pady=5)

        tk.Button(file_frame, text="Save Names to File", command=self.save_to_file,
                  bg="#16a085", fg="white", font=("Helvetica", 12, "bold"),
                  width=25, height=2, bd=0, activebackground="#1abc9c", cursor="hand2").grid(row=0, column=1, padx=10, pady=5)

        # Remove winners option
        option_frame = tk.Frame(self.root, bg="#1f2f3a")
        option_frame.pack(pady=5)
        self.remove_var = tk.IntVar()
        tk.Checkbutton(option_frame, text="Remove winners after picking", variable=self.remove_var,
                       font=("Helvetica", 12), bg="#1f2f3a", fg="#bdc3c7", activebackground="#1f2f3a",
                       selectcolor="#2980b9").pack(anchor="w", padx=20)

    # --- Core Functionalities ---
    def add_name(self):
        name = self.name_entry.get().strip()
        if name:
            self.names.append(name)
            self.update_listbox()
            self.name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter a name.")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for name in self.names:
            self.listbox.insert(tk.END, name)

    def pick_random_name(self):
        if not self.names:
            messagebox.showerror("Error", "No names to pick from!")
            return
        winner = random.choice(self.names)
        messagebox.showinfo("Winner", f"The selected name is:\n\n{winner}")
        if self.remove_var.get():
            self.names.remove(winner)
            self.update_listbox()

    def pick_multiple_names(self):
        if not self.names:
            messagebox.showerror("Error", "No names to pick from!")
            return

        # Ask for number of winners
        num_window = tk.Toplevel(self.root)
        num_window.title("Number of Winners")
        num_window.geometry("300x150")
        num_window.configure(bg="#1f2f3a")
        tk.Label(num_window, text="Enter number of winners:", font=("Helvetica", 12),
                 bg="#1f2f3a", fg="#bdc3c7").pack(pady=20)
        num_entry = tk.Entry(num_window, font=("Helvetica", 12), bd=0,
                             highlightthickness=2, highlightbackground="#27ae60", width=10)
        num_entry.pack(pady=5)

        def pick_winners():
            try:
                n = int(num_entry.get())
                if n <= 0:
                    raise ValueError
                if n > len(self.names):
                    messagebox.showerror("Error", f"Cannot pick {n} names from {len(self.names)} available!")
                    return
                winners = random.sample(self.names, n)
                messagebox.showinfo("Winners", "The selected winners are:\n\n" + "\n".join(winners))
                if self.remove_var.get():
                    for winner in winners:
                        self.names.remove(winner)
                    self.update_listbox()
                num_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive integer.")

        tk.Button(num_window, text="Pick", command=pick_winners,
                  bg="#27ae60", fg="white", font=("Helvetica", 12, "bold"),
                  width=10, height=2, bd=0, activebackground="#2ecc71", cursor="hand2").pack(pady=10)

    def remove_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No name selected!")
            return
        for index in reversed(selected):
            del self.names[index]
        self.update_listbox()

    def clear_all(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all names?")
        if confirm:
            self.names = []
            self.update_listbox()

    # --- File Operations ---
    def load_from_file(self):
        path = filedialog.askopenfilename(title="Select file", filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded_names = [line.strip() for line in f.readlines() if line.strip()]
                if loaded_names:
                    self.names.extend(loaded_names)
                    self.update_listbox()
                    self.file_path = path
                    messagebox.showinfo("Success", f"Loaded {len(loaded_names)} names from file.")
                else:
                    messagebox.showwarning("Warning", "The file is empty.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_to_file(self):
        if not self.names:
            messagebox.showerror("Error", "No names to save!")
            return

        if self.file_path:
            save_path = self.file_path
        else:
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if not save_path:
                return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                for name in self.names:
                    f.write(name + "\n")
            messagebox.showinfo("Success", f"Saved {len(self.names)} names to file.")
            self.file_path = save_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomNamePickerApp(root)
    root.mainloop()
