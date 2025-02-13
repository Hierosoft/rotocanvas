
"""

ChatGPT prompt
- 2025-02-13
Write a tkinter canvas program with File Open menu that opens json files and when one is opened, assume it is a dict. First fill the canvas with gray. Iterate the pairs. The key is a string, and should be split by "," to get coordinates, converted to an int pair. If the value is True, draw black at the coordinates, otherwise draw white. Here is an example input file:
- paste json

Now assume that instead of true and false, there will be a float value from 0 to 1. Create a gray pixel of the value.

"""
import json
import tkinter as tk
from tkinter import filedialog

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return

    with open(file_path, "r") as file:
        data = json.load(file)

    draw_canvas(data)

def draw_canvas(data):
    canvas.delete("all")
    canvas_width, canvas_height = 400, 400
    cell_size = 20  # Each cell is 20x20 pixels

    # Fill background with gray
    canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="gray")
    max_value = -1
    for key, value in data.items():
        if value > max_value:
            max_value = value
    for key, value in data.items():
        try:
            x, y = map(int, key.split(","))
            value = value / max_value
            # if value > 1.0:
            #     value = 1.0
            gray_value = int(value * 255)
            color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            canvas.create_rectangle(
                x * cell_size, y * cell_size,
                (x + 1) * cell_size, (y + 1) * cell_size,
                fill=color, outline=color
            )
        except ValueError:
            print(f"Skipping invalid key: {key}")

# Initialize main window
root = tk.Tk()
root.title("JSON Canvas Viewer")

# Create menu
menu = tk.Menu(root)
root.config(menu=menu)
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Create canvas
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

root.mainloop()
