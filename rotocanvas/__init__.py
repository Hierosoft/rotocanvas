#!/usr/bin/env python
import sys
import os
import platform

# region same as hierosoft/__init__.py


class Constants(dict):
    """Read-only Dictionary.

    based on https://stackoverflow.com/a/19023331/4541104
    and hierosoft.Constants
    """
    def __init__(self):
        dict.__init__(self)
        self.__readonly = False

    def readonly(self, readonly=True):
        """Allow or deny modifying dictionary"""
        if readonly is None:
            readonly = False
        elif readonly not in (True, False):
            raise TypeError("readonly shoul be True or False (got {})"
                            "".format(readonly))
        self.__readonly = readonly

    def __setitem__(self, key, value):
        if self.__readonly:
            raise TypeError("__setitem__ is not supported")
        return dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        if self.__readonly:
            raise TypeError("__delitem__ is not supported")
        return dict.__delitem__(self, key)


sysdirs = Constants()  # Call .readonly() after vars are set below.

# For semi-standard folders on Windows and Darwin see
# <johnkoerner.com/csharp/special-folder-values-on-windows-versus-mac/>
if platform.system() == "Windows":
    HOME = os.environ['USERPROFILE']
    sysdirs['HOME'] = HOME
    sysdirs['SHORTCUTS_DIR'] = os.path.join(HOME, "Desktop")
    sysdirs['APPDATA'] = os.environ['APPDATA']
    sysdirs['LOCALAPPDATA'] = os.environ['LOCALAPPDATA']
    sysdirs['PROGRAMS'] = os.path.join(sysdirs['LOCALAPPDATA'], "Programs")
    sysdirs['CACHES'] = os.path.join(sysdirs['LOCALAPPDATA'], "Caches")
elif platform.system() == "Darwin":
    # See <https://developer.apple.com/library/archive/
    #   documentation/MacOSX/Conceptual/BPFileSystem/Articles/
    #   WhereToPutFiles.html>
    HOME = os.environ['HOME']
    sysdirs['HOME'] = HOME
    sysdirs['SHORTCUTS_DIR'] = os.path.join(HOME, "Desktop")
    # APPDATA = os.path.join(HOME, "Library", "Preferences")
    # ^ Don't use Preferences: It only stores plist format files
    #   generated using the macOS Preferences API.
    # APPDATA = "/Library/Application Support" # .net-like
    sysdirs['APPDATA'] = os.path.join(HOME, ".config")  # .net Core-like
    sysdirs['LOCALAPPDATA'] = os.path.join(HOME, ".local",
                                           "share")  # .net Core-like
    sysdirs['CACHES'] = os.path.join(HOME, "Library",
                                     "Caches")  # .net Core-like
    # ^ APPDATA & LOCALAPPDATA & CACHES can also be in "/" not HOME
    #   (.net-like)
    # sysdirs['PROGRAMS'] = os.path.join(HOME, "Applications")
    # ^ Should only be used for Application Bundle, so:
    sysdirs['PROGRAMS'] = os.path.join(HOME, ".local", "lib")
else:
    HOME = os.environ['HOME']
    sysdirs['HOME'] = HOME
    sysdirs['SHORTCUTS_DIR'] = os.path.join(HOME, ".local", "share",
                                            "applications")
    sysdirs['APPDATA'] = os.path.join(HOME, ".config")
    sysdirs['LOCALAPPDATA'] = os.path.join(HOME, ".local",
                                           "share")  # .net-like
    sysdirs['CACHES'] = os.path.join(HOME, ".cache")
    sysdirs['PROGRAMS'] = os.path.join(HOME, ".local", "lib")

del HOME

sysdirs.readonly()

# endregion same as hierosoft/__init__.py


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
