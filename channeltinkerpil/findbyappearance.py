#!/usr/bin/env python3

import sys
import os

# from channeltinkerpil import diff_images
try:
    from channeltinker import (
        error,
        diff_images,
    )
except ModuleNotFoundError as ex:
    sys.stderr.write("{}\n\n".format(ex))
    sys.stderr.flush()
    sys.stderr.write("You have to run setup to get the findbyapperance"
                     " command.\n\n")
    sys.stderr.flush()
    sys.exit(1)

from PIL import Image
import PIL


def populateVisuallySimilar(results, imagePath, dirPath, limit=10,
                            image=None, skipDifferentSize=True,
                            extensions=['.png', '.jpg', '.bmp' '.jpeg']):
    '''
    Recursively get a list of metadata of images that are visually
    similar to the image file at imagePath. Directories or files
    starting with "." will be ignored. The most similar will be
    first in the list.

    Sequential arguments:
    results -- a blank list that will become a list of dictionaries
        where each dictionary has 'mean_diff' and 'path'. The list will
        contain the most similar images.

    Keyword arguments:
    limit -- Limit the number of closest matches to include in results.
    image -- This is used for caching purposes. If it is present, then
        imagePath will be ignored and image will be used instead.
    '''
    for sub in os.listdir(dirPath):
        subPath = os.path.join(dirPath, sub)
        if sub.startswith("."):
            continue
        if os.path.isdir(subPath):
            populateVisuallySimilar(
                results,
                imagePath,
                subPath,
                limit=limit,
                image=image,
            )
            continue
        ext = os.path.splitext(sub)[1]
        if ext.lower() not in extensions:
            continue
        if image is None:
            try:
                image = Image.open(imagePath)
            except PIL.UnidentifiedImageError as ex:
                error("* Error opening {}.format(imagePath)")
                # Do not continue, because the base image is necessary.
                raise ex
        head = None
        try:
            head = Image.open(subPath)
        except PIL.UnidentifiedImageError as ex:
            error("* Error opening {}: {}".format(imagePath, ex))
            return
        w = max(image.size[0], head.size[0])
        h = max(image.size[1], head.size[1])
        if skipDifferentSize:
            if image.size[0] != head.size[0]:
                return
            if image.size[1] != head.size[1]:
                return
        else:
            raise NotImplementedError("skipDifferentSize must be True"
                                      " because resizing isn't"
                                      " implemented in"
                                      " populateVisuallySimilar.")
        diff_size = w, h
        diffMeta = diff_images(image, head, diff_size=diff_size)
        mean_diff = diffMeta['mean_diff']
        newResult = {
            'mean_diff': mean_diff,
            'path': subPath,
        }
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
    dirPath = os.path.realpath(dirPath)
    results = []
    populateVisuallySimilar(
        results,
        imagePath,
        dirPath,
    )
    print("* The most similar images are shown first:")
    for result in results:
        print("{}".format(result))


if __name__ == "__main__":
    main()
