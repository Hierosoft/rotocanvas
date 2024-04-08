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

verbosity_levels = {
    0: 50,  # CRITICAL
    1: 40,  # ERROR
    2: 30,  # WARNING
    3: 20,  # INFO
    4: 10,  # DEBUG
}


class Verbosity:  # NOTE: There is no enum in Python 2 (added in 3.4).
    CRITICAL = 0  # 50
    ERROR = 1  # 40
    WARNING = 2  # 30
    INFO = 3  # 20
    DEBUG = 4  # 10


verbosity = Verbosity.WARNING  # default of WARNING mimics logging module
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
    if level not in verbosity_levels:
        raise ValueError("{} is not a valid verbosity.".format(level))
    verbosity = level


def write0(arg):
    """CRITICAL message"""
    sys.stderr.write(arg)
    sys.stderr.flush()
    return True


def write1(arg):
    """ERROR message"""
    if verbosity < 1:
        return False
    sys.stderr.write(arg)
    sys.stderr.flush()
    return True


def write2(arg):
    """WARNING message"""
    if verbosity < 2:
        return False
    sys.stderr.write(arg)
    sys.stderr.flush()
    return True


def write3(arg):
    """INFO message"""
    if verbosity < 3:
        return False
    sys.stderr.write(arg)
    sys.stderr.flush()
    return True


def write4(arg):
    """DEBUG message"""
    if verbosity < 4:
        return False
    sys.stderr.write(arg)
    sys.stderr.flush()
    return True


def echo0(*args, **kwargs):
    """CRITICAL message"""
    print(*args, file=sys.stderr, **kwargs)
    return True


def echo1(*args, **kwargs):
    """ERROR message"""
    if verbosity < 1:
        return False
    print(*args, file=sys.stderr, **kwargs)
    return True


def echo2(*args, **kwargs):
    """WARNING message"""
    if verbosity < 2:
        return False
    print(*args, file=sys.stderr, **kwargs)
    return True


def echo3(*args, **kwargs):
    """INFO message"""
    if verbosity < 3:
        return False
    print(*args, file=sys.stderr, **kwargs)
    return True


def echo4(*args, **kwargs):
    """DEBUG message"""
    if verbosity < 4:
        return False
    print(*args, file=sys.stderr, **kwargs)
    return True


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
    echo0("# You tried to run the module.")
    echo0("# Instead, import it as follows:")
    echo0("import rotocanvas")
    echo0("# not:")
    echo0("# from rotocanvas import x  # where x is a submodule or symbol")


if __name__ == "__main__":
    main(sys.argv)
