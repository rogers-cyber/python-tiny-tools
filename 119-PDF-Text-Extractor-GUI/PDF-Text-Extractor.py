import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from PyPDF2 import PdfReader
import os

class PDFTextExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Text Extractor")
        self.root.geometry("800x600")
        
        # Buttons Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.extract_btn = ttk.Button(button_frame, text="Select PDF(s) and Extract Text", command=self.extract_text)
        self.extract_btn.grid(row=0, column=0, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="Save Extracted Text", command=self.save_text)
        self.save_btn.grid(row=0, column=1, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Text", command=self.clear_text)
        self.clear_btn.grid(row=0, column=2, padx=5)
        
        # Scrolled Text Area
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    def extract_text(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=[("PDF Files", "*.pdf")],
            title="Select PDF file(s)"
        )
        if not file_paths:
            return
        
        all_text = ""
        for file_path in file_paths:
            try:
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                if not text.strip():
                    text = f"[No extractable text found in {os.path.basename(file_path)}]\n"
                all_text += f"--- {os.path.basename(file_path)} ---\n{text}\n\n"
            except Exception as e:
                all_text += f"[Failed to extract {os.path.basename(file_path)}: {str(e)}]\n\n"
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, all_text)
    
    def save_text(self):
        text_content = self.text_area.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showwarning("Warning", "No text to save!")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save extracted text"
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(text_content)
                messagebox.showinfo("Saved", "Text saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save text:\n{str(e)}")
    
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

if __name__ == "__main__":
    app = ttk.Window(themename="cosmo")  # You can try other themes like 'journal', 'flatly'
    PDFTextExtractor(app)
    app.mainloop()
