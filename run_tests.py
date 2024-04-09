#!/usr/bin/env python
import os
import platform
import subprocess
import sys

if platform.system() == "WINDOWS":
    HOME = os.environ['USERPROFILE']
    PY_REL = os.path.join("Scripts", "python.exe")
else:
    HOME = os.environ['HOME']
    PY_REL = os.path.join("bin", "python")

VENV_DIRS = [
    os.path.join(HOME, "kivy_venv"),  # used by Kivy documentation
    os.path.join(HOME, "kivy_env"),
    os.path.join(HOME, ".virtualenvs", "kivy_env"),
    os.path.join(HOME, ".virtualenvs", "kivy_venv"),
    os.path.join(HOME, ".virtualenvs", "kivy"),
    os.path.join(HOME, "virtualenvs", "kivy_env"),
    os.path.join(HOME, "virtualenvs", "kivy_venv"),
    os.path.join(HOME, "virtualenvs", "kivy"),
]

VENV_DIR = None
PY = None


def detect_kivy_venv():
    global VENV_DIR
    global PY
    for try_dir in VENV_DIRS:
        try_file = os.path.join(try_dir, PY_REL)
        if os.path.isfile(try_file):
            VENV_DIR = try_dir
            PY = try_file
            break


def main():
    detect_kivy_venv()
    if PY is None:
        print("Error: A Kivy venv was not detected (tried {})"
              .format(VENV_DIRS), file=sys.stderr)
        return 1
    print("Error: A Kivy venv was detected: {}"
          .format(VENV_DIR), file=sys.stderr)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    args = (PY, "-m", "pytest")
    subprocess.run(args)
    return 0


main()
