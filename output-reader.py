
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return

    with open(file_path, "r") as file:
        data = json.load(file)

    draw_image(data)

    global current_file
    current_file = file_path

def draw_image(data):
    global img, tk_img
    img = Image.new("RGB", (20, 20), "gray")

    for key, value in data.items():
        try:
            x, y = map(int, key.split(","))
            gray_value = int(value * 255)
            img.putpixel((x, y), (gray_value, gray_value, gray_value))
        except ValueError:
            print(f"Skipping invalid key: {key}")

    tk_img = ImageTk.PhotoImage(img.resize((400, 400), Image.NEAREST))
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)


def save_file():
    if not img:
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if not file_path:
        return

    img_resized = img.resize((400, 400), Image.NEAREST)
    img_resized.save(file_path, "PNG")
    messagebox.showinfo("Save File", f"Image saved as {file_path}")


# Initialize main window
root = tk.Tk()
root.title("JSON Canvas Viewer")

# Create menu
menu = tk.Menu(root)
root.config(menu=menu)
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save As", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Create canvas
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

img = None
current_file = None

root.mainloop()
