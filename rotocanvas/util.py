#!/usr/bin/env python
import sys
import os
import shutil
imageExtensions = ["png", "jpg", "jpe", "jpg", "bmp"]


def getEndsWithI(haystack, needles):
    ret = None
    for needle in needles:
        if haystack.lower().endswith(needle.lower()):
            return haystack[-len(needle):]

def set_extensions(lowerStrings):
    global imageExtensions
    imageExtensions = lowerStrings

def get_frame_name(prefix, i, minDigits, ext=None):
    """
    Get the filename in padded numbered notation.

    Sequential arguments:
    prefix -- the part before the numbers
    i -- the frame number
    minDigits -- the minimum number of zero-padded digits (0 for no pad)
    ext -- If not None, add a dot and extension to the name.
    """
    noExt = prefix + str(i).zfill(minDigits)
    if (ext is None) and (len(ext) > 0):
        return noExt
    else:
        return noExt + "." + ext


def splitframename(framePath):
    parent = os.path.split(framePath)[0]
    firstFrameName = os.path.split(framePath)[1]
    # print(parent)
    # print(firstFrameName)
    framePath = os.path.join(parent, firstFrameName)
    # if not os.path.isfile(framePath):
    #     raise ValueError("{} does not exist.".format(framePath))
    frameNoExt = os.path.splitext(firstFrameName)[0]
    dotExt = os.path.splitext(firstFrameName)[1]
    minDigits = 0
    digitPos = -1
    digitChars = "0123456789"
    while True:
        if abs(digitPos) > len(frameNoExt):
            break
        if frameNoExt[digitPos] not in digitChars:
            break
        minDigits += 1
        digitPos -= 1
    prefix = frameNoExt[:-minDigits]
    numberS = frameNoExt[-minDigits:]
    return prefix, numberS, dotExt


def get_frame_number(framePath, prefix=None, minDigits=None):
    frameName = os.path.split(framePath)[1]
    pr, numberS, dotExt = splitframename(frameName)
    md = len(numberS)
    if (prefix is None) or (minDigits is None):
        if prefix is None:
            prefix = pr
        if minDigits is None:
            minDigits = md

    # print("frameName: {}".format(frameName))
    frameNoExt = frameName[:len(prefix)+minDigits]
    # print("frameNoExt: {}".format(frameNoExt))
    # print("prefix: {}".format(prefix))
    # print("minDigits: {}".format(minDigits))
    ret = int(frameNoExt[-minDigits:])
    # print("ret: {}".format(ret))
    return ret


def divide_frames_in(parent, start, step):
    i = start
    # minDigits = 0
    global imageExtensions
    ext = None
    firstFramePath = None
    for sub in sorted(os.listdir(parent)):
        subPath = os.path.join(parent, sub)
        ext = getEndsWithI(sub, imageExtensions)
        if ext is not None:
            firstFramePath = subPath
            break
    if ext is None:
        print("There are no {} files in {}"
              "".format(imageExtensions, parent))
        return None
    # print("Detected {}".format(ext))
    # while True:
    #     numberS = str(i).zfill(padding)

    return divide_frames(firstFramePath, start, step)

def divide_frames(firstFramePath, start, step):
    """
    Move the specified frames.

    Sequential arguments:
    start - the first frame to keep
    step - how many frames to skip
    """
    prefix, numberS, dotExt = splitframename(firstFramePath)
    minDigits = len(numberS)
    # first = get_frame_number(firstFramePath, prefix=prefix,
    # minDigits=minDigits)
    first = int(numberS)
    parent, firstFrameName = os.path.split(firstFramePath)
    if start < first:
        raise ValueError("You specified the start as {} but the first"
                         " frame is {}: {}."
                         "".format(start, first, firstFrameName))
        return None

    frameNoExt = firstFrameName[:len(prefix)+minDigits]
    offPath = os.path.join(parent,
                           "start={},step={}".format(start, step))
    if not os.path.isdir(offPath):
        os.makedirs(offPath)
    i = start
    while True:
        frameName = get_frame_name(prefix, i, minDigits) + dotExt
        framePath = os.path.join(parent, frameName)
        if not os.path.isfile(framePath):
            print("- Done (no {})".format(frameName))
            break
        # print("{}: {}".format(i, frameName))
        destPath = os.path.join(offPath, frameName)
        # print("mv \"{}\" \"{}\"".format(framePath, destPath))
        shutil.move(framePath, destPath)
        i += step


def main(args):
    print("# You tried to run the module.")
    print("# Instead, import it as follows:")
    print("import pyrotocanvas.util")
    print("# or:")
    print("# from pyrotocanvas.util import *")


if __name__ == "__main__":
    main(sys.argv)
