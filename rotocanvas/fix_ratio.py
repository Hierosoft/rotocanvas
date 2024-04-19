#!/usr/bin/env python
from __future__ import print_function
import sys
import argparse
try:
    import cv2
except ImportError:
    sys.stderr.write("You must install OpenCV for Python or run this"
                     " using a venv with OpenCV.\n")
    exit(1)


def resize(inPath, outPath, ratioPart0, ratioPart1, preserveDim):
    """Resize the image and fit it within a width or height.

    Args:
        inPath (str): The source image path.
        outPath (str): Image path to create/overwrite.
        ratioPart0 (Union[int,float]): Numerator (for width)
        ratioPart1 (Union[int,float]): Denominator (for height)
        preserveDim (int): Set this to 0 if you want to keep the
            width the same when enforcing the ratio. To keep the height
            the same, set it to 1.

    Raises:
        ValueError: If dimension isn't x or y (0 or 1).
    """
    # See <https://www.tutorialkart.com/opencv/python/
    # opencv-python-resize-image/>
    # img = cv2.imread(originalPath, cv2.IMREAD_UNCHANGED)
    # print('Original Dimensions: ', img.shape)
    img = cv2.imread(inPath, cv2.IMREAD_UNCHANGED)
    size = [float(img.shape[1]), float(img.shape[0])]  # row,col order
    if str(preserveDim) == "0":
        size[1] = size[0] * (float(ratioPart1) / float(ratioPart0))
    elif str(preserveDim) == "1":
        size[0] = size[1] * (float(ratioPart0) / float(ratioPart1))
    else:
        raise ValueError("preserveDim must be 0 or 1 since there"
                         " are only 2 dimensions in an image.")
    width = round(size[0])
    height = round(size[1])
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    # "Pi Zero doesn’t like the inter flag set to cv2.INTER_AREA. If
    # you change it to cv2.INTER_LINEAR it should work."
    # -Adrian Rosebrock
    #  https://www.pyimagesearch.com/2018/09/19/pip-install-opencv/
    #  November 10, 2018.
    # cv2.imshow("Image Forced to {}:{} Ratio"
    #            "".format(ratioPart0, ratioPart1), resized)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    cv2.imwrite(outPath, resized)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
                    help="path to image")
    ap.add_argument("-o", "--output", required=True,
                    help=("path to output image after scaling"))
    ap.add_argument("-r0", "--ratio0", required=True,
                    help=("ratio numerator"))
    ap.add_argument("-r1", "--ratio1", required=True,
                    help=("ratio denominator"))
    ap.add_argument("-p", "--preserve-dimension", required=True,
                    help=("which dimension to keep (0 for w, 1 for h)"))
    args = vars(ap.parse_args())
    resize(args["input"], args["output"], args["ratio0"],
           args["ratio1"], args["preserve_dimension"])


if __name__ == "__main__":
    main()
