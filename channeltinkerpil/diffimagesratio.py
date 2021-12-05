#!/usr/bin/env python3
'''
Recursively show a checklist of image paths in two given directories
where any of the following apply:
- The aspect ratio differs.
- The destination file is new (doesn't exist in the source).
- The source or destination can't be read by PIL.

Example:
cd ~/minetest/games
~/git/gimp-plugin-channel-tinker/diffimagesratio.py ../bucket_game-200527 bucket_game | grep -v narrower | grep -v "[Ss]creenshot"
~/git/gimp-plugin-channel-tinker/diffimagesratio.py ../bucket_game-200527 bucket_game --max-source-ratio .5 --exclude projects --exclude src --exclude etc --exclude 3d_armor --exclude signs_lib | grep -v narrower | grep -v "[Ss]creenshot"
'''
import sys
import os
# from PIL import ImageDraw
import json

from channeltinkerpil import diff_images_by_path
from channeltinker import (
    error,
)

checkDotTypes = [
    ".png",
    ".jpg",
    ".bmp",
]
# ^ see also typeExtensions['image/raster'] in mtanalyze/ffcmd.py


def usage():
    error(__doc__)
    error("")


def showDiffRatioForImages(base_path, head_path, root=None, indent="",
                           max_source_ratio=None, skipDirNames=[]):
    '''
    This will show images added or where ratio changed (but not images
    that were removed, because base_path isn't traversed, only checked
    for existing files and directories parallel to head_path).

    Keyword arguments:
    root -- This part is always removed from head_path before displaying
            it.
    max_source_ratio -- only show items where the source ratio is less
                        than or equal to this number.
    skipDirNames -- exclude these directory names.

    When adding new options, pass them onto BOTH recursive calls!
    '''
    if max_source_ratio is not None:
        max_source_ratio = float(max_source_ratio)
    # if not os.path.isdir(base_path):
    #     raise ValueError("The base_path must be a directory.")
    if not os.path.isdir(head_path):
        raise ValueError("The head_path must be a directory.")
    for sub in os.listdir(head_path):
        if sub.startswith("."):
            continue
        baseSubPath = os.path.join(base_path, sub)
        headSubPath = os.path.join(head_path, sub)
        headShowPath = headSubPath
        if root is not None:
            if headShowPath.startswith(root):
                headShowPath = headShowPath[len(root):]
        if os.path.isdir(headSubPath):
            if sub in skipDirNames:
                continue
            newindent = indent
            if not os.path.isdir(baseSubPath):
                newindent = indent + "  "
                # print("sub: \"{}\"".format(sub))
                # print("skipDirNames: \"{}\"".format(skipDirNames))
                print(indent+"- +new dir:   {}".format(headSubPath))
            showDiffRatioForImages(
                baseSubPath,
                headSubPath,
                root=root,
                indent=newindent,
                max_source_ratio=max_source_ratio,
                skipDirNames=skipDirNames
            )
        else:
            extLower = os.path.splitext(sub)[1].lower()
            if extLower not in checkDotTypes:
                continue
            if os.path.isfile(baseSubPath):
                results = diff_images_by_path(baseSubPath, headSubPath)
                if results['head'].get('error') is not None:
                    print(indent+"- [ ] unreadable: {}".format(headSubPath))
                elif results['base'].get('error') is not None:
                    print(indent+"- [ ] unreadable in previous version: {}".format(headSubPath))
                elif results['head']['ratio'] > results['base']['ratio']:
                    if (max_source_ratio is not None) and (results['base']['ratio'] > max_source_ratio):
                        continue
                    print(indent+"- [ ] wider:      {}".format(headSubPath))
                elif results['head']['ratio'] < results['base']['ratio']:
                    if (max_source_ratio is not None) and (results['base']['ratio'] > max_source_ratio):
                        continue
                    print(indent+"- [ ] narrower:   {}".format(headSubPath))
            else:
                print(indent+"- [ ] +new file:  {}".format(headSubPath))


def main():
    base_path = None
    head_path = None
    prev_arg = None
    options = {}
    options['excludes'] = []
    option_name = None
    for arg in sys.argv:
        if prev_arg is None:
            prev_arg = arg
            continue
        if arg.startswith("--"):
            if arg == "--max-source-ratio":
                option_name = "max_source_ratio"
            elif arg == "--exclude":
                option_name = "excludes"
            else:
                usage()
                error("Error: Unknown option: {}".format(arg))
                exit(1)
        elif option_name is not None:
            old = options.get(option_name)
            if (old is not None) and isinstance(old, list):
                options[option_name].append(arg)
            else:
                options[option_name] = arg
            option_name = None
        elif base_path is None:
            base_path = arg
        elif head_path is None:
            head_path = arg
        else:
            usage()
            error("Error: There was an extra sequential argument."
                  " There should only be source and destination and"
                  " options but you also said \"{}\".".format(arg))
            exit(1)
        prev_arg = arg
    # head_root = head_path
    max_source_ratio = options.get("max_source_ratio")
    if head_path is None:
        error("You must specify two directories.")
        exit(1)
    error("* checking only: {}".format(checkDotTypes))
    if len(options['excludes']) > 0:
        error("* excluding directory names: {}".format(options['excludes']))
    else:
        error("* excluding no directory names")
    results = showDiffRatioForImages(base_path, head_path, max_source_ratio=max_source_ratio, skipDirNames=options['excludes'])


if __name__ == "__main__":
    main()

