import sys
import os
import tkinter as tk
from tkinter import ttk
import sv_ttk
import re
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# =========================
# Helper to get resource path
# =========================
def resource_path(file_name):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, file_name)

# =========================
# App Setup
# =========================
root = tk.Tk()
root.title("TempForge - Temperature Converter")
root.geometry("1100x720")
# root.iconbitmap(resource_path("logo.ico"))

sv_ttk.set_theme("light")
dark_mode_var = tk.BooleanVar(value=False)
editing_flag = False

# =========================
# Conversion Functions
# =========================
def c_to_f(c): return c * 9 / 5 + 32
def f_to_c(f): return (f - 32) * 5 / 9

# =========================
# Input Validation
# =========================
def validate_numeric(new_value):
    if new_value == "" or new_value == "-": return True
    return bool(re.match(r"^-?\d*\.?\d*$", new_value))

# =========================
# Update Functions
# =========================
def update_celsius(*args):
    global editing_flag
    if editing_flag: return
    val = c_var.get().strip()
    if val == "" or val == "-":
        f_var.set("")
        update_graph()
        return
    try:
        editing_flag = True
        f_var.set(f"{c_to_f(float(val)):.2f}")
        status_var.set(f"{val}°C → {f_var.get()}°F")
        update_graph()
    except:
        f_var.set("")
        status_var.set("Invalid Celsius input")
    finally:
        editing_flag = False

def update_fahrenheit(*args):
    global editing_flag
    if editing_flag: return
    val = f_var.get().strip()
    if val == "" or val == "-":
        c_var.set("")
        update_graph()
        return
    try:
        editing_flag = True
        c_var.set(f"{f_to_c(float(val)):.2f}")
        status_var.set(f"{val}°F → {c_var.get()}°C")
        update_graph()
    except:
        c_var.set("")
        status_var.set("Invalid Fahrenheit input")
    finally:
        editing_flag = False

# =========================
# Clipboard Functions
# =========================
def copy_celsius(): 
    val = c_var.get()
    if val: root.clipboard_clear(); root.clipboard_append(val); status_var.set(f"Celsius {val} copied!")

def copy_fahrenheit(): 
    val = f_var.get()
    if val: root.clipboard_clear(); root.clipboard_append(val); status_var.set(f"Fahrenheit {val} copied!")

# =========================
# Theme Toggle
# =========================
def toggle_theme():
    style.theme_use("clam")
    if dark_mode_var.get():
        root.configure(bg="#2E2E2E")
        style.configure("TLabel", background="#2E2E2E", foreground="#FFFFFF", font=("Segoe UI",16,"bold"))
        style.configure("TFrame", background="#2E2E2E")
        style.configure("TEntry", fieldbackground="#3C3C3C", foreground="#FFFFFF", font=("Segoe UI",20), padding=12)
        style.configure("TButton", background="#FF6F61", foreground="#FFFFFF", font=("Segoe UI",14,"bold"), padding=12)
        style.map("TButton", background=[("active","#FF8A65")])
        style.configure("TCheckbutton", background="#2E2E2E", foreground="#FFFFFF", font=("Segoe UI",14,"bold"))
    else:
        root.configure(bg="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="#333333", font=("Segoe UI",16,"bold"))
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TEntry", fieldbackground="#F0F0F0", foreground="#000000", font=("Segoe UI",20), padding=12)
        style.configure("TButton", background="#4CAF50", foreground="#FFFFFF", font=("Segoe UI",14,"bold"), padding=12)
        style.map("TButton", background=[("active","#45A049")])
        style.configure("TCheckbutton", background="#FFFFFF", foreground="#333333", font=("Segoe UI",14,"bold"))

# =========================
# Styles & Status
# =========================
style = ttk.Style()
style.theme_use("clam")

status_var = tk.StringVar(value="Ready")
ttk.Label(root, textvariable=status_var, anchor="w", font=("Segoe UI",12,"italic")).pack(side=tk.BOTTOM, fill="x", padx=5, pady=5)

main_frame = ttk.Frame(root, padding=25)
main_frame.pack(expand=True, fill="both")
ttk.Label(main_frame, text="Temperature Converter", font=("Segoe UI",28,"bold")).pack(pady=(0,20))

vcmd = (root.register(validate_numeric), "%P")

# =========================
# Input Card Function
# =========================
def create_input_card(parent, label_text, var, copy_command, bg_color):
    frame = tk.Frame(parent, bg=bg_color, bd=3, relief="raised")
    ttk.Label(frame, text=label_text, anchor="w", font=("Segoe UI",18,"bold")).pack(anchor="w", padx=15, pady=(15,8))
    entry = tk.Entry(frame, textvariable=var, font=("Segoe UI",24,"bold"), width=14, justify="center",
                     relief="groove", bd=4, validate="key", validatecommand=vcmd)
    entry.pack(anchor="w", padx=15, pady=(0,12), ipady=10)
    btn = tk.Button(frame, text=f"Copy {label_text}", command=copy_command, bg="#FF8A65", fg="white",
                    font=("Segoe UI",14,"bold"), activebackground="#FF7043", relief="raised", bd=3)
    btn.pack(anchor="w", padx=15, pady=(0,15))
    return frame

# =========================
# Row Frame for Inputs
# =========================
row_frame = tk.Frame(main_frame)
row_frame.pack(fill="x", pady=15, padx=10)

# ---------------- Celsius Input ----------------
c_var = tk.StringVar()
c_card = create_input_card(row_frame, "Celsius (°C)", c_var, copy_celsius, "#FFE082")
c_card.pack(side="left", expand=True, fill="both", padx=12)
c_var.trace_add("write", update_celsius)

# ---------------- Fahrenheit Input ----------------
f_var = tk.StringVar()
f_card = create_input_card(row_frame, "Fahrenheit (°F)", f_var, copy_fahrenheit, "#81D4FA")
f_card.pack(side="left", expand=True, fill="both", padx=12)
f_var.trace_add("write", update_fahrenheit)

# ---------------- Dark Mode Toggle ----------------
ttk.Checkbutton(main_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_theme).pack(pady=18)

# =========================
# Dynamic Graph
# =========================
fig = Figure(figsize=(9,3), dpi=100)
ax = fig.add_subplot(111)
ax.set_title("Celsius ↔ Fahrenheit", fontsize=16)
ax.set_xlabel("Celsius (°C)")
ax.set_ylabel("Fahrenheit (°F)")
ax.grid(True)
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas.get_tk_widget().pack(pady=20, fill="both", expand=True)

def update_graph():
    ax.clear()
    c_range = list(range(-50,101))
    f_range = [c_to_f(c) for c in c_range]
    ax.plot(c_range, f_range, color="#FF5722", linewidth=2, label="C→F Curve")
    try:
        val_c = float(c_var.get()) if c_var.get() not in ["", "-"] else None
        val_f = float(f_var.get()) if f_var.get() not in ["", "-"] else None
    except: val_c = val_f = None
    if val_c is not None: ax.scatter(val_c, c_to_f(val_c), color="green", s=180, zorder=5, label="Current Celsius")
    elif val_f is not None: ax.scatter(f_to_c(val_f), val_f, color="blue", s=180, zorder=5, label="Current Fahrenheit")
    ax.set_xlabel("Celsius (°C)")
    ax.set_ylabel("Fahrenheit (°F)")
    ax.set_title("Celsius ↔ Fahrenheit", fontsize=16)
    ax.grid(True)
    ax.legend()
    canvas.draw()

# Animate graph smoothly
def animate(i): update_graph()
ani = FuncAnimation(fig, animate, interval=100, save_count=200)


update_graph()
root.mainloop()
