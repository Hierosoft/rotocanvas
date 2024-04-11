#!/usr/bin/env python3
'''
Recursively show a checklist of image paths in two given directories
where any of the following apply:
- The aspect ratio differs.
- The destination file is new (doesn't exist in the source).
- The source or destination can't be read by PIL.

Example:
cd ~/minetest/games
{cmd} ../bucket_game-200527 bucket_game | grep -v narrower | grep -v "[Ss]creenshot"
{cmd} ../bucket_game-200527 bucket_game --max-source-ratio .5 --exclude projects --exclude src --exclude etc --exclude 3d_armor --exclude signs_lib | grep -v narrower | grep -v "[Ss]creenshot"
'''
# ^ where {cmd} is diffimagesratio if you did "pip install rotocanvas"
#   (See instances of __doc__ below for how to display docstring above)

import sys
import os
# from PIL import ImageDraw
# import json

from channeltinkerpil import diff_images_by_path
from channeltinker import (
    echo1,
    platformCmds,
    safePathParam,
)

checkDotTypes = [
    ".png",
    ".jpg",
    ".bmp",
]
# ^ see also typeExtensions['image/raster'] in mtanalyze/ffcmd.py


def usage():
    echo1(__doc__.format(cmd=os.path.basename(sys.argv[0])))
    echo1("")


def firstDifferentSubdirs(path1, path2):
    '''
    In reverse, find the first different directory names, such as
    (person1, person2) if "/home/person1/Documents" and
    "/home/person2/Documents" are specified. If no directory name
    differs, return (None, None).
    '''
    parts1 = path1.split(os.path.sep)
    parts2 = path2.split(os.path.sep)
    # if len(parts1) != len(parts2)
    part1I = len(parts1) - 1
    part2I = len(parts2) - 1
    while (part1I >= 0) and (part2I >= 0):
        if parts1[part1I] != parts2[part2I]:
            return (parts1[part1I], parts2[part2I])
        part1I -= 1
        part2I -= 1
    return (None, None)


def showDiffRatioForImages(base_path, head_path, root=None, indent="",
                           max_source_ratio=None, skipDirNames=[],
                           patchify=False, oldResults=None):
    '''Show images added or where ratio changed
    (but not images that were removed, because base_path isn't
    traversed, only checked for existing files and directories parallel
    to head_path).

    ^ When adding new args, pass them onto BOTH recursive calls!

    Args:
        root (str): This part is always removed from head_path before
            displaying it.
        max_source_ratio (float): only show items where the source ratio
            is less than or equal to this number.
        skipDirNames (list[str]): exclude these directory names.
        patchify (bool): Write commands to implement the change(s) to
            results['prepatch_commands'] and/or
            results['patch_commands'].
        oldResults (dict): Existing dict for combining results
            (if not None, used and modified for return).

    Returns:
        dict: Info about differences, such as:
            - 'wider_images' (list[str]): paths
            - 'narrower_images' (list[str]): paths
            - 'prepatch_commands' (list[str]): preliminary bash commands
              to merge head
            - 'patch_commands' (list[str]): final bash commands to merge
              head
    '''
    if max_source_ratio is not None:
        max_source_ratio = float(max_source_ratio)
    # if not os.path.isdir(base_path):
    #     raise ValueError("The base_path must be a directory.")
    results = oldResults
    if results is None:
        results = {
            'wider_images': [],
            'narrower_images': [],
            'prepatch_commands': [],
            'patch_commands': [],
        }
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
            results = showDiffRatioForImages(
                baseSubPath,
                headSubPath,
                root=root,
                indent=newindent,
                max_source_ratio=max_source_ratio,
                skipDirNames=skipDirNames,
                patchify=patchify,
                oldResults=results,
            )
        else:
            changed = False
            extLower = os.path.splitext(sub)[1].lower()
            if extLower not in checkDotTypes:
                continue
            if os.path.isfile(baseSubPath):
                if (os.path.realpath(baseSubPath)
                        == os.path.realpath(headSubPath)):
                    raise ValueError("head and base are same file")
                # imgResults = None
                # if os.path.isfile(headSubPath):
                imgResults = diff_images_by_path(baseSubPath, headSubPath)
                # else:
                #     print(indent+"- [ ] doesn't exist: {}"
                #           .format(headSubPath))
                # if not imgResults:
                #     changed = True
                #     pass
                if imgResults['head'].get('error') is not None:
                    print(indent+"- [ ] unreadable: {}".format(headSubPath))
                    # caller should show the real 'error'
                elif imgResults['base'].get('error') is not None:
                    print(indent+"- [ ] unreadable in previous version: {}"
                          .format(headSubPath))
                    # caller should show the real 'error'
                elif imgResults['head']['ratio'] > imgResults['base']['ratio']:
                    if ((max_source_ratio is not None)
                            and (imgResults['base']['ratio']
                                 > max_source_ratio)):
                        continue
                    print(indent+"- [ ] wider:      {}"
                          "".format(headSubPath))
                    changed = True
                elif imgResults['head']['ratio'] < imgResults['base']['ratio']:
                    if ((max_source_ratio is not None)
                            and (imgResults['base']['ratio']
                                 > max_source_ratio)):
                        continue
                    print(indent+"- [ ] narrower:   {}".format(headSubPath))
                    changed = True
                if changed:
                    if patchify:
                        modsFlagMinus1 = os.path.sep + "mods" + os.path.sep
                        baseI = baseSubPath.find(modsFlagMinus1)
                        headI = headSubPath.find(modsFlagMinus1)
                        if (baseI < 0) or (headI < 0):
                            echo1('Error: there is no /mods/ in the'
                                  ' path (base="{}", head="{}")'
                                  ''.format(baseSubPath, headSubPath))
                            continue
                        baseI += 1  # go past os.path.sep
                        headI += 1  # go past os.path.sep
                        baseRel = baseSubPath[baseI]
                        baseRelSafe = safePathParam(baseRel)
                        prepatchCmd = "prepatch"
                        prepatchCmd += " " + baseRelSafe
                        diffNames = firstDifferentSubdirs(baseSubPath,
                                                          headSubPath)
                        prepatchName = "{}-vs-{}".format(diffNames[0],
                                                         diffNames[1])
                        prepatchCmd += " " + prepatchName
                        results['prepatch_commands'].append(prepatchCmd)
                        patchCmd = platformCmds['cp']
                        patchCmd += " " + safePathParam(headSubPath)
                        # ^ Put head FIRST so it is kept (patch base)!
                        patchCmd += " " + safePathParam(baseSubPath)
                        results['patch_commands'].append(patchCmd)

            else:
                print(indent+"- [ ] +new file:  {}".format(headSubPath))
    return results


def main():
    base_path = None
    head_path = None
    prev_arg = None
    options = {}
    options['excludes'] = []
    boolNames = ["patchify"]
    option_name = None
    for arg in sys.argv:
        if prev_arg is None:
            prev_arg = arg
            continue
        if arg.startswith("--"):
            argName = arg[2:]
            if arg == "--max-source-ratio":
                option_name = "max_source_ratio"
            elif arg == "--exclude":
                option_name = "excludes"
            elif argName in boolNames:
                options[argName] = True
            else:
                usage()
                echo1("Error: Unknown option: {}".format(arg))
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
            echo1("Error: There was an extra sequential argument."
                  " There should only be source and destination and"
                  " options but you also said \"{}\".".format(arg))
            exit(1)
        prev_arg = arg
    # head_root = head_path
    if head_path is None:
        echo1("You must specify two directories.")
        exit(1)
        # Checking base_path isn't necessary since it is set first.
    base_path = os.path.realpath(base_path)
    head_path = os.path.realpath(head_path)
    echo1("* checking only: {}".format(checkDotTypes))
    if len(options['excludes']) > 0:
        echo1("* excluding directory names: {}".format(options['excludes']))
    else:
        echo1("* excluding no directory names")
    results = showDiffRatioForImages(
        base_path,
        head_path,
        max_source_ratio=options.get("max_source_ratio"),
        skipDirNames=options.get('excludes'),
        patchify=options.get('patchify'),
    )
    if options.get('patchify'):
        print("")
        print("# Prepatch commands (gather files from base)")
        for prepatchCmd in results['prepatch_commands']:
            print(prepatchCmd)

        print("# Patch commands (overwrite base with head)")
        for patchCmd in results['patch_commands']:
            print(patchCmd)


if __name__ == "__main__":
    main()
