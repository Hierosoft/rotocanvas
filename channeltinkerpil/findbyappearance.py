#!/usr/bin/env python3

import sys
import os

# from channeltinkerpil import diff_images
try:
    from channeltinker import (
        echo1,
        echo3,
        echo4,
        diff_images,
    )
except ModuleNotFoundError as ex:
    sys.stderr.write("{}\n\n".format(ex))
    sys.stderr.flush()
    sys.stderr.write("You have to run setup to get the findbyapperance"
                     " command.\n\n")
    sys.stderr.flush()
    sys.exit(1)

from PIL import Image, ImageFile
import PIL


ImageFile.LOAD_TRUNCATED_IMAGES = True
# ^ Avoids issue #14 (GIMP images with
#   "Raw profile type exif"), and image is displayed
#   (often image isn't really broken,
#   such as if saved with GIMP)


results = []


def populateVisuallySimilar(imagePath, dirPath, limit=10,
                            image=None, skipDifferentSize=True,
                            extensions=['.png', '.jpg', '.bmp' '.jpeg']):
    '''
    Recursively get a list of metadata of images that are visually
    similar to the image file at imagePath. Directories or files
    starting with "." will be ignored. The most similar will be
    first in the list.

    Requires the following globals:
    results (list[dict]): a blank list that will become a list of
        dictionaries where each dictionary has 'mean_diff' and 'path'.
        The list will contain the most similar images.

    Args:
        limit (int, optional): Limit the number of closest matches to
            include in results.
        image (Union(Image,ChannelTinkerInterface), optional): This is
            used for caching purposes. If it is present, then imagePath
            will be ignored and image will be used instead.
    '''
    global results
    if results is None:
        results = []

    if image is None:
        try:
            image = Image.open(imagePath)
            echo1("* loaded \"{}\"".format(imagePath))
        except PIL.UnidentifiedImageError as ex:
            echo1("* Error opening {}.format(imagePath)")
            # Do not continue, because the base image is
            # necessary.
            raise ex
    checkedAny = False
    baseDir = os.path.dirname(imagePath)
    isInBaseDir = False
    if baseDir == dirPath:
        isInBaseDir = True
        echo4("* checking {}"
              "".format(dirPath))

    for sub in os.listdir(dirPath):
        subPath = os.path.join(dirPath, sub)
        if sub.startswith("."):
            continue
        if os.path.isdir(subPath):
            populateVisuallySimilar(
                imagePath,
                subPath,
                limit=limit,
                image=image,
            )
            continue
        ext = os.path.splitext(sub)[1]
        if ext.lower() not in extensions:
            if subPath == imagePath:
                echo1("* Error: skipped ext for self: {}".format(ext))
            elif os.path.dirname(imagePath) == dirPath:
                echo3("* INFO: {}'s ext is not in {}"
                      "".format(sub, extensions))
            continue
        if isInBaseDir:
            echo4("  * checking {}".format(sub))
        head = None
        try:
            head = Image.open(subPath)
        except PIL.UnidentifiedImageError as ex:
            echo1("* Error opening {}: {}".format(imagePath, ex))
            continue
        w = max(image.size[0], head.size[0])
        h = max(image.size[1], head.size[1])
        if skipDifferentSize:
            if image.size[0] != head.size[0]:
                continue
            if image.size[1] != head.size[1]:
                continue
        else:
            raise NotImplementedError("skipDifferentSize must be True"
                                      " because resizing isn't"
                                      " implemented in"
                                      " populateVisuallySimilar.")
        diff_size = w, h
        diffMeta = diff_images(image, head, diff_size=diff_size)
        if not checkedAny:
            echo3("* checked image(s) in {}".format(dirPath))
        checkedAny = True
        err = diffMeta.get('error')
        if err is not None:
            echo1("  * {}: {}".format(subPath, err))
        mean_diff = diffMeta['mean_diff']
        newResult = {
            'mean_diff': mean_diff,
            'path': subPath,
        }
        if subPath == imagePath:
            if mean_diff != 0:
                echo1("  * WARNING: mean_diff for self is {}"
                      " (should be 0)!".format(mean_diff))
            else:
                echo1("  * found self (not a genuine match): {}"
                      "".format(diffMeta))
        # The difference is less than the item at this index in results:
        ltI = -1
        for i in range(len(results)):
            if mean_diff < results[i]['mean_diff']:
                ltI = i
                break
        if ltI > -1:
            results.insert(ltI, newResult)
            if len(results) > limit:
                results = results[:limit]
        elif len(results) < limit:
            results.append(newResult)


def main():
    if len(sys.argv) < 3:
        raise ValueError("You must specify a file and a directory.")
    # [0] is the command.
    imagePath = sys.argv[1]
    if not os.path.isfile(imagePath):
        raise ValueError("The first argument must be an image path.")
    dirPath = sys.argv[2]
    if not os.path.isdir(dirPath):
        raise ValueError("The second argument must be a directory.")
    imagePath = os.path.realpath(imagePath)
    dirPath = os.path.realpath(dirPath)
    # results = []  # passing it to populateVisuallySimilar doesn't work
    # for some reason. The results list ends up being bigger than limit
    # but not having the closest matches :huh?:.
    global results
    echo1("* using imagePath: \"{}\"".format(imagePath))
    echo1("  * in: \"{}\"".format(os.path.dirname(imagePath)))
    populateVisuallySimilar(
        imagePath,
        dirPath,
    )
    if len(results) > 0:
        echo1("* The most similar images are shown first:")
        for result in results:
            print("{}".format(result))
    else:
        echo1("* No images were found in the destination, so no"
              " comparisons were made.")


if __name__ == "__main__":
    main()
