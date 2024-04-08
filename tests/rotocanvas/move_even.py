#!/usr/bin/env python
import sys
import os

if os.path.exists("../rotocanvas/__init__.py"):
    sys.path.append(os.path.realpath(".."))
from rotocanvas.util import divide_frames_in


def main(args):
    if len(args) < 2:
        print("You must specify a directory.")
        exit(1)
    divide_frames_in(args[1], 0, 2)


if __name__ == "__main__":
    main(sys.argv)
