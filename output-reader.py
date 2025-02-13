import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class JSONCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Canvas Viewer")

        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack()

        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save As", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        self.img = None
        self.tk_img = None
        self.current_file = None

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        with open(file_path, "r") as file:
            data = json.load(file)

        self.draw_image(data)
        self.current_file = file_path

    def draw_image(self, data):
        self.img = Image.new("RGB", (20, 20), "gray")
        max_value = -1
        for key, value in data.items():
            if value > max_value:
                max_value = value
        for key, value in data.items():
            try:
                x, y = map(int, key.split(","))
                gray_value = int(value / max_value * 255)
                self.img.putpixel((x, y), (gray_value, gray_value, gray_value))
            except ValueError:
                print(f"Skipping invalid key: {key}")

        self.tk_img = ImageTk.PhotoImage(self.img.resize((400, 400), Image.NEAREST))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

    def save_file(self):
        if not self.img:
            messagebox.showinfo("Save File", "There is no image.")
            return

        initialfile = None
        if self.current_file:
            initialfile = os.path.splitext(self.current_file)[0] + ".png"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=initialfile,
        )

        if not file_path:
            return

        if os.path.exists(file_path):
            confirm = messagebox.askyesno("Confirm Save", f"{file_path} already exists. Overwrite?")
            if not confirm:
                return

        self.img.save(file_path, "PNG")
        messagebox.showinfo("Save File", f"Image saved as {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONCanvasApp(root)
    root.mainloop()
