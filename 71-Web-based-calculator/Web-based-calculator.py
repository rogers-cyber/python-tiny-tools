import math
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog

# ---------------- GLOBALS ---------------- #
current_expression = ""
history = []
memory_value = 0.0
use_degrees = True

SAFE_DICT = {
    "sin": lambda x: math.sin(math.radians(x)) if use_degrees else math.sin(x),
    "cos": lambda x: math.cos(math.radians(x)) if use_degrees else math.cos(x),
    "tan": lambda x: math.tan(math.radians(x)) if use_degrees else math.tan(x),
    "log": math.log10,
    "ln": math.log,
    "sqrt": math.sqrt,
    "pi": math.pi,
    "e": math.e,
}

# ---------------- FUNCTIONS ---------------- #
def append_char(char):
    global current_expression
    current_expression += str(char)
    display_var.set(current_expression)

def clear_expression():
    global current_expression
    current_expression = ""
    display_var.set("")

def backspace():
    global current_expression
    current_expression = current_expression[:-1]
    display_var.set(current_expression)

def calculate():
    global current_expression
    try:
        result = eval(current_expression, {"__builtins__": None}, SAFE_DICT)
        history.append(f"{current_expression} = {result}")
        update_history()
        current_expression = str(result)
    except Exception:
        current_expression = "Error"
    display_var.set(current_expression)

# -------- Scientific -------- #
def scientific(func):
    global current_expression
    if func in ["sin", "cos", "tan", "log", "ln", "sqrt"]:
        current_expression += f"{func}("
    elif func == "x2":
        current_expression += "**2"
    display_var.set(current_expression)

# -------- History -------- #
def update_history():
    history_box.delete(0, tk.END)
    for item in reversed(history[-50:]):
        history_box.insert(tk.END, item)

def insert_from_history(event):
    global current_expression
    selection = history_box.curselection()
    if selection:
        current_expression = history_box.get(selection[0]).split("=")[0].strip()
        display_var.set(current_expression)

def export_history():
    file = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text File", "*.txt")]
    )
    if file:
        with open(file, "w") as f:
            for h in history:
                f.write(h + "\n")

# -------- Memory -------- #
def memory_clear():
    global memory_value
    memory_value = 0.0

def memory_add():
    global memory_value
    try:
        memory_value += float(display_var.get())
    except:
        pass

def memory_recall():
    append_char(memory_value)

# -------- Degree / Radian -------- #
def toggle_mode():
    global use_degrees
    use_degrees = bool(mode_var.get())
    mode_label.config(text="DEG" if use_degrees else "RAD")

# -------- Keyboard Support -------- #
def key_input(event):
    if event.char.isdigit() or event.char in "+-*/().":
        append_char(event.char)
    elif event.keysym == "Return":
        calculate()
    elif event.keysym == "BackSpace":
        backspace()
    elif event.keysym == "Escape":
        clear_expression()

# ---------------- GUI ---------------- #
app = tb.Window(
    themename="darkly",
    title="Advanced Web-Style Scientific Calculator",
    size=(1000, 600)
)

app.bind("<Key>", key_input)

# ---------------- LEFT PANEL ---------------- #
left_frame = tb.Frame(app)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

display_var = tk.StringVar()
display = tb.Entry(
    left_frame,
    textvariable=display_var,
    font=("Segoe UI", 24),
    justify=tk.RIGHT
)
display.pack(fill=tk.X, pady=10, ipady=10)

btn_frame = tb.Frame(left_frame)
btn_frame.pack(fill=tk.BOTH, expand=True)

buttons = [
    ["7", "8", "9", "/", "sin"],
    ["4", "5", "6", "*", "cos"],
    ["1", "2", "3", "-", "tan"],
    ["0", ".", "(", ")", "+"],
    ["pi", "e", "√", "x²", "="]
]

for r, row in enumerate(buttons):
    for c, char in enumerate(row):
        if char == "=":
            cmd, style = calculate, "success"
        elif char in ["sin", "cos", "tan"]:
            cmd, style = lambda f=char: scientific(f), "info"
        elif char == "√":
            cmd, style = lambda: scientific("sqrt"), "info"
        elif char == "x²":
            cmd, style = lambda: scientific("x2"), "info"
        else:
            cmd, style = lambda v=char: append_char(v), "secondary"

        tb.Button(btn_frame, text=char, bootstyle=style, command=cmd)\
            .grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

for i in range(5):
    btn_frame.columnconfigure(i, weight=1)
    btn_frame.rowconfigure(i, weight=1)

# -------- Controls -------- #
control = tb.Frame(left_frame)
control.pack(fill=tk.X, pady=5)

tb.Button(control, text="C", bootstyle="danger", command=clear_expression)\
    .pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
tb.Button(control, text="⌫", bootstyle="warning", command=backspace)\
    .pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

# -------- Memory -------- #
mem = tb.Frame(left_frame)
mem.pack(fill=tk.X)

tb.Button(mem, text="MC", command=memory_clear).pack(side=tk.LEFT, expand=True, fill=tk.X)
tb.Button(mem, text="M+", command=memory_add).pack(side=tk.LEFT, expand=True, fill=tk.X)
tb.Button(mem, text="MR", command=memory_recall).pack(side=tk.LEFT, expand=True, fill=tk.X)

# -------- Degree / Radian -------- #
mode_var = tk.IntVar(value=1)
mode_label = tb.Label(left_frame, text="DEG", font=("Segoe UI", 10, "bold"))
mode_label.pack(pady=5)

tb.Checkbutton(
    left_frame,
    text="Degree Mode",
    variable=mode_var,
    bootstyle="info",
    command=toggle_mode
).pack()

# ---------------- RIGHT PANEL (History) ---------------- #
right_frame = tb.Frame(app)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

tb.Label(right_frame, text="History", font=("Segoe UI", 14, "bold")).pack()

history_box = tk.Listbox(right_frame, font=("Segoe UI", 10))
history_box.pack(fill=tk.BOTH, expand=True)
history_box.bind("<Double-1>", insert_from_history)

tb.Button(
    right_frame,
    text="Export History",
    bootstyle="primary",
    command=export_history
).pack(fill=tk.X, pady=5)

app.mainloop()
