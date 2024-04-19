#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Based on
# <https://geeksforgeeks.org/python-display-images-with-pygame/>
# importing required library
from __future__ import print_function
from __future__ import division
import os
import sys
# import time
import unittest

import tkinter as tk
# import PIL
from PIL import (
    ImageTk,
    Image,
    ImageFile,
)


def echo0(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# BELOW PREVENTS the regression *if* done in all files that import PIL:
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


class TestPilIncompatible(unittest.TestCase):

    # def __init__(self, *args, **kwargs):
    #     unittest.TestCase.__init__(self, *args, **kwargs)

    def test_loading(self):
        prefix = "[TestPilIncompatible test_loading] "
        print(prefix + "{}".format(group_key))
        self.root = None
        self.path = None
        self.paths = None
        self.path_i = 0
        self.path = None
        self.image_delay = 200
        self.load_delay = 1
        # if len(sys.argv) > 1:
        #     self.path = sys.argv[1]
        #     if len(sys.argv) > 2:
        #         echo0("Error: Got extra arg.", file=sys.stderr)
        #         return 1
        if not self.path:
            image_paths = sorted(image_groups[group_key])
            if image_paths:
                self.paths = image_paths
                self.path = image_paths[-1]
                print('Automatically selected "{}"'.format(self.path))
            else:
                raise FileNotFoundError("tests/data/{}"
                                        .format(group_key))
        else:
            self.paths = [self.path]
        self.root = tk.Tk()
        self.root.title("Tkinter Image Loading Test")
        W = self.root.winfo_screenwidth() // 4
        H = self.root.winfo_screenheight() // 4

        self.exit_delay = (
            (self.image_delay * len(self.paths))
            + self.image_delay
            + self.load_delay
        )  # Must wait to exit until *after* every image has been shown
        print(prefix + " created a window.")
        self.root.geometry("{}x{}".format(W, H))
        self.root.after(self.load_delay, self.load)
        self.root.after(self.exit_delay, self.exit_window)
        # time.sleep(self.exit_delay/1000.0+1)
        self.root.mainloop()
        # ^ or instead of mainloop, potentially do pump_events
        #   (See ivan_pozdeev's answer
        #   <https://stackoverflow.com/a/49028688/4541104>
        #   based on IPython, answering
        #   <https://stackoverflow.com/questions/4083796/
        #   how-do-i-run-unittest-on-a-tkinter-app>)

    def pump_events(self):
        while self.root.dooneevent(tk.ALL_EVENTS | tk.DONT_WAIT):
            pass

    def load(self):
        if self.path_i is None:
            # load should run *after* test (that schedules it)
            raise ValueError("self.path_i was {}".format(self.path_i))
        if self.path_i >= len(self.paths):
            print("[TestPilIncompatible load] passed for all images")
            return False
        try:
            print("[TestPilIncompatible load] image {}".format(self.path_i))
            # image1.show()
            # show just opens it with the default application (or xv), so:
            image1 = Image.open(self.paths[self.path_i])
            # ^ causes:
            # PIL.UnidentifiedImageError: cannot identify image file '...'
            # where ... is the path of a PIL-incompatible image (issue #14)
            # *unless* ImageFile.LOAD_TRUNCATED_IMAGES = True
            test = ImageTk.PhotoImage(image1)
            label1 = tk.Label(self.root, image=test)
            label1.image = test
            label1.pack()
            self.path_i += 1
            self.root.after(self.image_delay, self.load)
        except Exception as ex:
            label1 = tk.Label(
                self.root,
                text="{}: {}".format(type(ex).__name__, ex)
            )
            label1.pack()
            raise

    def exit_window(self):
        print("[TestPilIncompatible exit_window] {}".format(group_key))
        if self.path_i is None:
            # exit_window should run *after* test (that schedules it)
            raise ValueError("self.path_i was {}".format(self.path_i))

        if self.path_i < len(self.paths):
            raise RuntimeError("Uh oh, only tested {} of {}"
                               .format(self.path_i, len(self.paths)))
        self.root.destroy()


if __name__ == "__main__":
    unittest.main()
