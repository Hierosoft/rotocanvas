#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Based on
# <https://geeksforgeeks.org/python-display-images-with-pygame/>
# importing required library
from __future__ import division
import os
import sys

import tkinter as tk
# import PIL
from PIL import (
    ImageTk,
    Image,
    ImageFile,
)

ImageFile.LOAD_TRUNCATED_IMAGES = True
# ^ Avoids issue #14 (GIMP images with
#   "Raw profile type exif"), and image is displayed
#   (often image isn't really broken,
#   such as if saved with GIMP)
TEST_SUBMODULE_DIR = os.path.dirname(os.path.realpath(__file__))
TESTS_DIR = os.path.dirname(TEST_SUBMODULE_DIR)
REPO_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, REPO_DIR)

from data_for_tests import image_groups  # noqa: E402
# group_key = 'pil-compatible'  # never triggers issue #14
group_key = 'pil-incompatible'

root = None
path = None
paths = None
path_i = 0


def load():
    global path_i
    if path_i >= len(paths):
        return False
    try:
        # image1.show()
        # show just opens it with the default application (or xv), so:
        image1 = Image.open(paths[path_i])
        # ^ causes:
        # PIL.UnidentifiedImageError: cannot identify image file '...'
        # where ... is the path of a PIL-incompatible image (issue #14)
        # *unless* ImageFile.LOAD_TRUNCATED_IMAGES = True
        test = ImageTk.PhotoImage(image1)
        label1 = tk.Label(root, image=test)
        label1.image = test
        label1.pack()
        path_i += 1
        root.after(200, load)
    except Exception as ex:
        label1 = tk.Label(
            root,
            text="{}: {}".format(type(ex).__name__, ex)
        )
        label1.pack()
        raise


def exit_window():
    root.destroy()


def main():
    global root
    global path
    global paths
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if len(sys.argv) > 2:
            print("Error: Got extra arg.", file=sys.stderr)
            return 1
    if not path:
        image_paths = sorted(image_groups[group_key])
        if image_paths:
            paths = image_paths
            path = image_paths[-1]
            print('Automatically selected "{}"'.format(path))
    else:
        paths = [path]
    root = tk.Tk()
    root.title("Tkinter Image Loading Test")
    W = root.winfo_screenwidth() // 4
    H = root.winfo_screenheight() // 4

    root.geometry("{}x{}".format(W, H))
    root.after(1, load)
    root.after(2000, exit_window)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
