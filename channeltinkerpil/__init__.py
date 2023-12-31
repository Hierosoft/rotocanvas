#!/usr/bin/env python
import os

from channeltinker import diff_images
from PIL import Image
import PIL
from channeltinker import (
    error,
    debug,
)


def gen_diff_image(base, head, diff_path=None):
    """Compare two PIL-compatible image objects visually.

    Args:
        diff_path (str): If not None, then save a graphical representation of
            the difference: black is same, closer to white differs (if images
            are different sizes, red is deleted, green is added).

    Returns:
        dict: Various differences between the images if any:
            {"same": false,
            "base": {
                "size": [16, 128],
                "ratio": 0.125 },
            "head": {
                "size": [16,128],
                "ratio": 1.0  },
            "diff": {
                "path": "/home/user/minetest/diffimage.png in {b} vs in {h}" }
            }

            Where {b} is the base image (usually the master file if known)
            filename and {h} is the head filename.
    """
    w = max(base.size[0], head.size[0])
    h = max(base.size[1], head.size[1])
    diff_size = w, h
    debug("* base size: {}".format(base.size))
    debug("* head size: {}".format(head.size))
    diff = None
    # draw = None
    nochange_color = (0, 0, 0, 255)
    if diff_path is not None:
        diff = Image.new('RGBA', diff_size, nochange_color)
        # error("* generated diff image in memory")
        # draw = ImageDraw.Draw(diff)
        error("* diff size: {}".format(diff.size))
    debug("Checking {} zone...".format(diff_size))
    result = diff_images(base, head, diff_size, diff=diff,
                         nochange_color=nochange_color)
    if diff_path is not None:
        diff_path = os.path.abspath(diff_path)
        diff.save(diff_path)
        result['diff'] = {}
        result['diff']['path'] = diff_path
        error("* saved \"{}\"".format(diff_path))
    return result


def diff_images_by_path(base_path, head_path, diff_path=None):
    """Compare two images. See gen_diff_image for further info.
    """
    result = None
    try:
        base = Image.open(base_path)
    except PIL.UnidentifiedImageError:
        result = {
            'base': {
                'error': "UnidentifiedImageError"
            },
            'head': {
            },  # It must be a dict to prevent a key error.
        }
    try:
        head = Image.open(head_path)
    except PIL.UnidentifiedImageError:
        result2 = {
            'base': {
            },  # It must be a dict to prevent a key error.
            'head': {
                'error': "UnidentifiedImageError"
            }
        }
        if result is None:
            result = result2
        else:
            result['head'] = result2['head']
    if result is not None:
        # Return an error.
        return result
    return gen_diff_image(base, head, diff_path=diff_path)

