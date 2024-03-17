
import os
import sys

from collections import OrderedDict
import tkinter as tk
import PIL
from PIL import ImageTk, Image

if __name__ == "__main__":
    MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
    REPO_DIR = os.path.dirname(MODULE_DIR)
    sys.path.insert(0, REPO_DIR)

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
        self.images = OrderedDict()
        self.paths = OrderedDict(
            base=None,
            head=None,
        )
        self.root = parent
        container = self
        # container = tk.Frame(self.root)
        # container.pack()
        self.container = container

    def set_base_path(self, path):
        self.paths['base'] = path

    def set_head_path(self, path):
        self.paths['head'] = path

    def _load_item(self, key, path=None):
        """Load an internal keyed image.

        Args:
            key (str): Must be 'base' or 'head'.
            path (str, optional): Set self.paths[key], which is the path
                to load. Defaults to self.paths[key].

        Raises:
            FileNotFoundError: If path (default self.paths[key]) is set
                but file doesn't exist.

        Returns:
            dict: *Only* should be truthy on error.
        """
        if key not in ('base', 'head'):
            raise KeyError("_load_item can only load base or head, but got {}"
                           "".format(key))
        if not path:
            path = self.paths[key]
        else:
            self.paths[key] = path

        if not path:
            result = OrderedDict()
            result[key] = {}  # There is nothing to load.
            return result

        if not os.path.isfile(path):
            # Avoid strange "AttributeError: 'NoneType' object has no
            #   attribute 'read'" in io.BytesIO in PIL/Image.py and
            #   show the real error instead.
            raise FileNotFoundError(path)
        try:
            self.images[key] = Image.open(path)
            # ^ must not go out of scope or will be lost.
        except PIL.UnidentifiedImageError:
            return {
                'base': {
                    'error': "UnidentifiedImageError"
                },
                'head': {
                },  # It must be a dict to prevent a key error.
            }

    def load(self):
        prefix = "[MainForm load] "
        result = OrderedDict()
        self.pimages = OrderedDict()
        if self.paths is None:
            raise NotImplementedError("self.paths is None.")
        for key, _ in self.paths.items():
            if not _:
                continue
            print(prefix+"loading {}".format(key))
            this_result = self._load_item(key)
            if this_result:
                # *Only* should be truthy on error.
                result.update(this_result)
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
            return
        if ('base' in self.images) and ('head' in self.images):
            results = gen_diff_image(self.images['base'], self.images['head'])
        else:
            return
        images = OrderedDict()
        images['base'] = self.images['base']  # results['base_image']
        images['head'] = self.images['head']  # results['head_image']
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
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.minsize(screen_w//10, screen_h//10)
    root.title("RotoCanvas DiffImage")
    mainform = MainForm(root)
    if len(sys.argv) != 3:
        mainform.error = "You must specify two files."
        print(mainform.error)
    else:
        mainform.set_base_path(sys.argv[1])
        mainform.set_head_path(sys.argv[2])
    mainform.pack()
    mainform.load()
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())