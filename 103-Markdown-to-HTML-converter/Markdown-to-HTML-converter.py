import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as tb
from tkinterdnd2 import TkinterDnD, DND_FILES
import markdown

# =================== Utility ===================
def convert_markdown_to_html(md_text):
    """
    Convert Markdown text to HTML with common extensions.
    """
    html = markdown.markdown(
        md_text,
        extensions=[
            "fenced_code", "tables", "toc", "codehilite", "nl2br", "sane_lists"
        ]
    )
    return html

def wrap_html(body_html, title="Markdown Output"):
    """
    Wrap the HTML body in a full HTML template with basic CSS.
    """
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; background-color: #f4f4f4; color: #333; }}
pre {{ background-color: #272822; color: #f8f8f2; padding: 10px; overflow-x: auto; border-radius: 5px; }}
code {{ padding: 2px 4px; border-radius: 3px; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
table, th, td {{ border: 1px solid #999; }}
th, td {{ padding: 8px; text-align: left; }}
h1, h2, h3, h4, h5, h6 {{ color: #222; }}
a {{ color: #1a73e8; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""
    return template

# =================== GUI App ===================
class MarkdownConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown to HTML Batch Converter")
        self.root.geometry("900x600")

        style = tb.Style(theme="cosmo")

        # ===== Buttons =====
        button_frame = tb.Frame(root)
        button_frame.pack(pady=10)

        self.browse_btn = tb.Button(button_frame, text="📂 Browse Markdown Files", bootstyle="success-outline",
                                    width=25, command=self.browse_files)
        self.browse_btn.grid(row=0, column=0, padx=5)

        self.convert_btn = tb.Button(button_frame, text="📝 Convert to HTML", bootstyle="info-outline",
                                     width=20, command=self.start_conversion)
        self.convert_btn.grid(row=0, column=1, padx=5)

        self.clear_btn = tb.Button(button_frame, text="🧹 Clear Log", bootstyle="warning-outline", width=20,
                                   command=self.clear_log)
        self.clear_btn.grid(row=0, column=2, padx=5)

        self.about_btn = tb.Button(button_frame, text="ℹ️ About", bootstyle="secondary-outline", width=15,
                                   command=self.show_about)
        self.about_btn.grid(row=0, column=3, padx=5)

        # ===== Log Area =====
        self.log_area = scrolledtext.ScrolledText(root, wrap="word", font=("Arial", 12))
        self.log_area.pack(expand=True, fill="both", padx=10, pady=10)

        # ===== Drag & Drop =====
        self.files_to_process = []
        root.drop_target_register(DND_FILES)
        root.dnd_bind('<<Drop>>', self.handle_drop)

    # ===== Logging =====
    def log(self, message):
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")

    def clear_log(self):
        self.log_area.delete(1.0, "end")

    # ===== Browse Files =====
    def browse_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Markdown files",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_paths:
            self.files_to_process.extend(file_paths)
            self.log(f"Selected {len(file_paths)} file(s).")

    # ===== Drag & Drop =====
    def handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        added = 0
        for path in paths:
            if os.path.isfile(path) and path.lower().endswith(".md"):
                if path not in self.files_to_process:
                    self.files_to_process.append(path)
                    added += 1
        self.log(f"Queued {added} Markdown file(s) from drag & drop.")

    # ===== Conversion Worker =====
    def conversion_worker(self):
        if not self.files_to_process:
            self.log("No files to convert.")
            return

        total_files = len(self.files_to_process)
        self.log(f"Starting batch conversion for {total_files} file(s)...")

        for idx, file_path in enumerate(self.files_to_process, 1):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    md_text = f.read()

                html_body = convert_markdown_to_html(md_text)
                html_content = wrap_html(html_body, title=os.path.basename(file_path))

                # Auto save HTML in the same folder
                folder = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(folder, base_name + ".html")

                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                self.log(f"[{idx}/{total_files}] Converted: {file_path} → {save_path}")

            except Exception as e:
                self.log(f"[{idx}/{total_files}] Error converting {file_path}: {str(e)}")

        self.files_to_process.clear()
        self.log("Batch conversion completed!")

    # ===== Start Conversion Thread =====
    def start_conversion(self):
        if not self.files_to_process:
            messagebox.showwarning("No Files", "Please select or drop Markdown files to convert.")
            return
        threading.Thread(target=self.conversion_worker, daemon=True).start()

    # ===== About =====
    def show_about(self):
        messagebox.showinfo(
            "About Markdown to HTML Batch Converter",
            "Markdown to HTML Batch Converter v1.1\n\n"
            "Drag & drop or browse multiple Markdown (.md) files.\n"
            "Automatically converts them to styled HTML in the same folder.\n\n"
            "Supports headings, code blocks, tables, lists, and links.\n\n"
            "Developed by MateTools"
        )

# =================== Main ===================
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MarkdownConverterApp(root)
    root.mainloop()
