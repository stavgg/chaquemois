import sqlite3
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import platform

# Paths
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "images")
DB_PATH = "/Users/stavgreidi/Documents/pro/db.db"

def load_variations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("\U0001F4CB All Tables:", cursor.fetchall())

    cursor.execute("""
    SELECT
        pv.VariationID,
        p.Name,
        pv.Color,
        pv.Size,
        pv.StockLevel,
        pv.ReorderLevel
    FROM ProductVariation pv
    JOIN Product p ON p.ProductID = pv.ProductID
    ORDER BY pv.VariationID ASC
    """)

    rows = cursor.fetchall()
    conn.close()
    print("=== Loaded Variations ===")
    for r in rows:
        print("→", r)
    return rows

def rounded_image(img_path, size=(60, 60)):
    img = Image.open(img_path).resize(size).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), 12, fill=255)
    img.putalpha(mask)
    return ImageTk.PhotoImage(img)

def get_image(product, color):
    filename_raw = f"{product.strip().lower()} {color.strip().lower()}"
    filename = filename_raw + ".webp"
    path = os.path.join(IMAGE_FOLDER, filename)
    if os.path.exists(path):
        return rounded_image(path)
    else:
        return ImageTk.PhotoImage(Image.new("RGB", (60, 60), "lightgray"))

def create_rounded_rect(canvas, x1, y1, x2, y2, radius=8, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def create_stock_label(parent, text, bg_color, width=60, height=30):
    canvas = tk.Canvas(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, bd=0)
    create_rounded_rect(canvas, 2, 2, width - 2, height - 2, radius=10, fill=bg_color, outline=bg_color)
    canvas.create_text(width // 2, height // 2, text=text, fill="white", font=("Helvetica", 10, "bold"))
    return canvas

def bind_mousewheel(widget, target_canvas):
    os_name = platform.system()
    def _on_mousewheel(event):
        if os_name == 'Darwin':
            target_canvas.yview_scroll(-1 * int(event.delta), "units")
        else:
            target_canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", _on_mousewheel))
    widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))
    widget.bind_all("<Button-4>", lambda e: target_canvas.yview_scroll(-1, "units"))
    widget.bind_all("<Button-5>", lambda e: target_canvas.yview_scroll(1, "units"))

import threading
import time

low_stock_alerts = []

def check_stock_levels_periodically(root, alert_label):
    def monitor():
        while True:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.Name, pv.Color, pv.Size, pv.StockLevel, pv.ReorderLevel
                FROM ProductVariation pv
                JOIN Product p ON pv.ProductID = p.ProductID
                WHERE pv.StockLevel < pv.ReorderLevel
            """)
            alerts = cursor.fetchall()
            conn.close()

            if alerts:
                message = f"⚠ Low stock: {len(alerts)} item(s) below threshold"
                alert_label.config(text=message, fg="red")
            else:
                alert_label.config(text="Stock levels normal", fg="green")

            time.sleep(60)

    threading.Thread(target=monitor, daemon=True).start()


def show_inventory():
    root = tk.Tk()
    root.title("Inventory – Chaquemois")
    root.configure(bg="#f9f9f9")
    root.geometry("1200x800")

    title = tk.Label(root, text="Inventory – Chaquemois", font=("Helvetica", 24, "bold"), bg="#f9f9f9", fg="#333")
    title.pack(pady=(10, 10), anchor="center")

    alert_label = tk.Label(root, text="Checking stock levels...", font=("Assistant", 11), bg="#f9f9f9", fg="gray")
    alert_label.pack(pady=(0, 10))

    check_stock_levels_periodically(root, alert_label)

    outer_container = tk.Frame(root, bg="#f9f9f9")
    outer_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer_container, bg="#f9f9f9", highlightthickness=0)
    scrollbar = tk.Scrollbar(outer_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scrollable_frame = tk.Frame(canvas, bg="#f9f9f9")
    window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    scrollable_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))

    bind_mousewheel(canvas, canvas)

    headers = ["Image", "ID", "Product", "Color", "Size", "Stock", "Reorder"]
    header_widths = [8, 6, 10, 6, 4, 6, 6]
    header_font = ("Helvetica", 11, "bold")
    header_row = tk.Frame(scrollable_frame, bg="#eeeeee")
    header_row.grid(row=0, column=0, sticky="ew")
    for idx, h in enumerate(headers):
        tk.Label(header_row, text=h.upper(), font=header_font, bg="#eeeeee", width=header_widths[idx], anchor="w").grid(row=0, column=idx, sticky="ew")
        header_row.columnconfigure(idx, weight=1)

    scrollable_frame.columnconfigure(0, weight=1)

    image_cache = {}
    data = load_variations()

    for i, row in enumerate(data, start=1):
        var_id, product, color, size, stock, reorder = row
        row_frame = tk.Frame(scrollable_frame, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        row_frame.grid(row=i, column=0, sticky="nsew", pady=2)
        scrollable_frame.rowconfigure(i, weight=1)
        for col in range(7):
            row_frame.columnconfigure(col, weight=1)
        font = ("Helvetica", 10)
        cell_options = {"font": font, "bg": "white", "anchor": "w", "padx": 5, "pady": 2}
        photo = get_image(product, color)
        image_cache[i] = photo
        tk.Label(row_frame, image=photo, bg="white", width=60).grid(row=0, column=0, sticky="w")
        tk.Label(row_frame, text=var_id, width=6, **cell_options).grid(row=0, column=1, sticky="w")
        tk.Label(row_frame, text=product, width=10, **cell_options).grid(row=0, column=2, sticky="w")
        tk.Label(row_frame, text=color, width=6, **cell_options).grid(row=0, column=3, sticky="w")
        tk.Label(row_frame, text=size.strip(), width=4, **cell_options).grid(row=0, column=4, sticky="w")
        if stock == 0:
            stock_color = "#dc3545"
        elif stock < reorder:
            stock_color = "#dc3545"
        elif stock < reorder + 3:
            stock_color = "#ffc107"
        else:
            stock_color = "#28a745"
        stock_canvas = create_stock_label(row_frame, str(stock), stock_color)
        stock_canvas.grid(row=0, column=5, padx=10, sticky="w")
        tk.Label(row_frame, text=reorder, width=6, **cell_options).grid(row=0, column=6, sticky="w")
    root.mainloop()

def check_critical_stock_for_login():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.Name, pv.Color, pv.Size, pv.StockLevel, pv.ReorderLevel
        FROM ProductVariation pv
        JOIN Product p ON pv.ProductID = p.ProductID
        WHERE pv.StockLevel < pv.ReorderLevel
    """)
    alerts = cursor.fetchall()
    conn.close()
    return alerts

def show_login():
    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == "admin" and password == "1234":
            login_window.destroy()
            show_inventory()
        else:
            error_label.config(text="\u274c Incorrect username or password")
    def toggle_password():
        if password_entry.cget("show") == "":
            password_entry.config(show="*")
            toggle_btn.config(text="Show password")
        else:
            password_entry.config(show="")
            toggle_btn.config(text="Hide password")
    alerts_before_login = check_critical_stock_for_login()
    login_window = tk.Tk()
    login_window.title("Admin Login – Chaquemois")
    login_window.geometry("400x460")
    login_window.configure(bg="#ffffff")
    login_window.resizable(False, False)
    try:
        base_path = os.path.dirname(__file__)
        logo_path = os.path.join(base_path, "images", "logo.png")
        logo_img = Image.open(logo_path)
        max_width, max_height = 120, 120
        logo_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        logo_tk = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(login_window, image=logo_tk, bg="#ffffff")
        logo_label.image = logo_tk
        logo_label.pack(pady=(20, 10))
    except Exception as e:
        print("\u26a0\ufe0f Failed to load logo:", e)
    tk.Label(login_window, text="Admin Login", font=("Assistant", 16, "bold"), bg="#ffffff", fg="#222").pack(pady=(0, 20))
    tk.Label(login_window, text="Username", font=("Assistant", 11), bg="#ffffff", anchor="w").pack(padx=30, fill="x")
    username_entry = tk.Entry(login_window, font=("Helvetica", 11), bd=1, relief="solid")
    username_entry.pack(padx=30, fill="x", ipady=5)
    tk.Label(login_window, text="Password", font=("Helvetica", 11), bg="#ffffff", anchor="w").pack(padx=30, pady=(10, 0), fill="x")
    password_entry = tk.Entry(login_window, show="*", font=("Helvetica", 11), bd=1, relief="solid")
    password_entry.pack(padx=30, fill="x", ipady=5)
    toggle_btn = tk.Button(login_window, text="Show password", font=("Assistant", 9), bg="#ffffff", bd=0, command=toggle_password)
    toggle_btn.pack(pady=(5, 0))
    error_label = tk.Label(login_window, text="", fg="red", bg="#ffffff", font=("Assistant", 10))
    error_label.pack(pady=(10, 0))
    canvas_btn = tk.Canvas(login_window, width=240, height=40, bg="#ffffff", highlightthickness=0)
    canvas_btn.pack(pady=(10, 0))

    if alerts_before_login:
        tk.Label(login_window, text=f"⚠ {len(alerts_before_login)} item(s) need restock", font=("Assistant", 10), fg="red", bg="#ffffff").pack(pady=(10, 5))

    # יצירת כפתור עגול מודרני
    create_rounded_rect(canvas_btn, 0, 0, 240, 40, radius=20, fill="#12033f", outline="#12033f")
    canvas_btn.create_text(120, 20, text="→ Login", fill="white", font=("Assistant", 12, "bold"))

    canvas_btn.bind("<Button-1>", lambda e: attempt_login())
    
    login_window.mainloop()

if __name__ == "__main__":
    alerts = check_critical_stock_for_login()
    if alerts:
        popup = tk.Tk()
        popup.title("Low Stock Alert")
        popup.geometry("320x140")
        popup.configure(bg="white")
        tk.Label(
        popup,
        text=("Low stock alert: Some items are below the reorder level.""Please review inventory."),
                font=("Assistant", 12, "bold"), fg="red", bg="white", justify="center", wraplength=280
    ).pack(pady=20)
        canvas_ok = tk.Canvas(popup, width=240, height=40, bg="white", highlightthickness=0)
        canvas_ok.pack()
        create_rounded_rect(canvas_ok, 0, 0, 240, 40, radius=20, fill="#12033f", outline="#12033f")
        canvas_ok.create_text(120, 20, text="OK", fill="white", font=("Assistant", 12, "bold"))
        canvas_ok.pack(pady=10)
        canvas_ok.bind("<Button-1>", lambda e: popup.destroy())
        popup.mainloop()

    show_login()
