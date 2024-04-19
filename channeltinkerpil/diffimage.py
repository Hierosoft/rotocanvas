#!/usr/bin/env python3
'''
Compare two image files.
Part of rotocanvas.

Similar projects:
- [diffimg](https://github.com/sandsmark/diffimg): Displays difference
  as a color mask using Qt.
'''
from __future__ import print_function
import sys
# import os
# from PIL import ImageDraw
# import json

from channeltinkerpil import diff_images_by_path
from channeltinker import (
    generate_diff_name,
    echo1,
)


def diff_image_files_and_gen(base_path, head_path, diff_name=None):
    """Detect how much the two files differ and generate a diff image.

    To get the difference without generating and saving a diff image,
    see diff_images in channeltinkerpil.

    Args:
        base_path (str): Any image (usually original file).
        head_path (str): Any image (usually file of unknown status).
        diff_name (str, optional): Temp image to create that shows where
            the other two files differ. Defaults to generated name (See
            generate_diff_name).

    Returns:
        dict: differences between the two files:
            - 'mean_diff' (float): Average difference of all pixels.
            - 'path' (str): The image that was tested.
    """
    if diff_name is None:
        diff_name = generate_diff_name(base_path, head_path)
    results = diff_images_by_path(base_path, head_path,
                                  diff_path=diff_name)
    # print(json.dumps(results, indent=2))
    return results


def main_cli():
    if len(sys.argv) != 3:
        echo1("You must specify two files.")
        exit(1)
    results = diff_image_files_and_gen(sys.argv[1], sys.argv[2])
    print(results)


if __name__ == "__main__":
    main_cli()
