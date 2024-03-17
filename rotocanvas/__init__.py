#!/usr/bin/env python
import sys
import os

verbosity = 0
for argI in range(1, len(sys.argv)):
    arg = sys.argv[argI]
    if arg.startswith("--"):
        if arg == "--verbose":
            verbosity = 1
        elif arg == "--debug":
            verbosity = 2

# def is_verbose():
#     return verbose > 0

def set_verbosity(level):
    global verbosity
    if level not in [True, False, 0, 1, 2]:
        raise ValueError("{} is not a valid verbosity.".format(level))
    verbosity = level


def write0(arg):
    sys.stderr.write(arg)
    sys.stderr.flush()


def write1(arg):
    if verbosity < 1:
        return
    sys.stderr.write(arg)
    sys.stderr.flush()


def write2(arg):
    if verbosity < 2:
        return
    sys.stderr.write(arg)
    sys.stderr.flush()


def echo0(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def echo1(*args, **kwargs):
    if verbosity < 1:
        return
    print(*args, file=sys.stderr, **kwargs)


def echo2(*args, **kwargs):
    if verbosity < 2:
        return
    print(*args, file=sys.stderr, **kwargs)


MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR = os.path.join(MODULE_DIR, "assets")
BRUSH_IMAGES_DIR = os.path.join(ASSETS_DIR, "brushes")
if not os.path.isdir(BRUSH_IMAGES_DIR):
    raise FileNotFoundError(BRUSH_IMAGES_DIR)

DEFAULT_ENCLOSURES = (
    ("'", "'"),
    ('"', '"'),
    ('[', ']'),
    ('(', ')'),
    ('{', '}'),
)


def no_enclosures(value, pairs=None):
    if not pairs:
        pairs = DEFAULT_ENCLOSURES
    if not value:
        return value
    if len(value) < 2:
        return value
    for pair in pairs:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            # Remove quotes & replace escaped ender with ender:
            value = value[1:-1].replace('\\'+pair[1], pair[1])
    return value


def main(args):
    print("# You tried to run the module.")
    print("# Instead, import it as follows:")
    print("import pyrotocanvas")
    print("# or:")
    print("# from pyrotocanvas import *")


if __name__ == "__main__":
    main(sys.argv)
