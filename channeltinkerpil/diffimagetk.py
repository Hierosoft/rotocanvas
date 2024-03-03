
# import os
import sys

from collections import OrderedDict
import tkinter as tk
import PIL
from PIL import ImageTk, Image

from channeltinkerpil import (
    gen_diff_image,
)

# from channeltinker import diff_images


class MainForm(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        # if len(args) > 0:
        #     print("MainApp ignored args")
        # if len(kwargs) > 0:
        #     print("MainApp ignored kwargs")
        # tk.Frame.__init__(self, parent)
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.result = None
        self.base_path = None
        self.head_path = None
        self.root = parent
        self.container = self

    def load(self):
        result = None
        self.pimages = {}
        try:
            self.base = Image.open(self.base_path)
            # ^ must not go out of scope or will be lost.
        except PIL.UnidentifiedImageError:
            result = {
                'base': {
                    'error': "UnidentifiedImageError"
                },
                'head': {
                },  # It must be a dict to prevent a key error.
            }
        try:
            self.head = Image.open(self.head_path)
            # ^ must not go out of scope or will be lost.
        except PIL.UnidentifiedImageError:
            result2 = {
                'base': {
                },  # It must be a dict to prevent a key error.
                'head': {
                    'error': "UnidentifiedImageError"
                }
            }
            if result is None:
                result = result2
            else:
                result['head'] = result2['head']
        self.result = result
        row = 0
        column = 0
        if self.result:
            for name, meta in self.result.items():
                error = meta.get('error')
                if error:
                    label = tk.Label(master=self.container, text=name+":")
                    label.grid(row=row, column=0)
                    label = tk.Label(master=self.container, text=error)
                    label.grid(row=row, column=1)
                    row += 1
            # END
            return
        results = gen_diff_image(self.base, self.head)
        images = OrderedDict()
        images['base'] = self.base  # results['base_image']
        images['head'] = self.head  # results['head_image']
        images['diff'] = results['diff_image']

        column = -1
        for key in images.keys():
            column += 1
            frame = tk.Frame(
                master=self.container,
                relief=tk.RAISED,
                borderwidth=1
            )
            frame.grid(row=row, column=column)
            label = tk.Label(master=frame, text=key)
            label.pack()
        row += 1
        column = -1
        for context, image in images.items():
            column += 1
            self.pimages[context] = ImageTk.PhotoImage(image)
            frame = tk.Frame(
                master=self.container,
                relief=tk.RAISED,
                borderwidth=1
            )
            frame.grid(row=row, column=column)
            label = tk.Label(
                master=frame,
                image=self.pimages[context],
            )
            # label.image = self.pimages[context]
            label.pack()
        row += 1
        same_msg = "unknown"
        if results.get('same') is True:
            same_msg = "same"
        elif results.get('same') is False:
            same_msg = "differs"
        label = tk.Label(master=self.container, text=same_msg)
        label.grid(row=row, column=2)


def main():
    root = tk.Tk()
    mainform = MainForm(root)
    if len(sys.argv) != 3:
        mainform.error = "You must specify two files."
    else:
        mainform.base_path = sys.argv[1]
        mainform.head_path = sys.argv[2]
    mainform.pack()
    mainform.load()
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())