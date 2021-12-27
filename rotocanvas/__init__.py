#!/usr/bin/env python
import sys

def prerr(msg):
    sys.stderr.write("{}\n".format(msg))
    sys.stderr.flush()


def main(args):
    print("# You tried to run the module.")
    print("# Instead, import it as follows:")
    print("import pyrotocanvas")
    print("# or:")
    print("# from pyrotocanvas import *")


if __name__ == "__main__":
    main(sys.argv)
