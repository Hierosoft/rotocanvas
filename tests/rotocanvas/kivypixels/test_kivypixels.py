#!/usr/bin/env python
import unittest
# import sys

from rotocanvas.kivypixels import KPImage  # , load_image


class KivyPixelsTest(unittest.TestCase):
    def test_blit_copy_with_bo(self):
        print("  tests:")
        size = (128, 128)
        src_img = KPImage(size)
        dst_img = KPImage(size)
        print("blit_copy_with_bo 32-bit...")
        print("  src_img: " + str(src_img.get_dict(data_enable=False)))
        print("  dst_img: " + str(dst_img.get_dict(data_enable=False)))
        dst_img.blit_copy_with_bo(
            src_img.data,
            src_img.stride,
            src_img.byteDepth,
            src_img.size,
            src_img.bOffset,
            src_img.gOffset,
            src_img.rOffset,
            src_img.aOffset
        )
        print("blit_copy_with_bo grayscale...")
        src_img = KPImage(size, byteDepth=1)
        dst_img = KPImage(size, byteDepth=1)
        print("  src_img: " + str(src_img.get_dict(data_enable=False)))
        print("  dst_img: " + str(dst_img.get_dict(data_enable=False)))
        dst_img.blit_copy_with_bo(
            src_img.data,
            src_img.stride,
            src_img.byteDepth,
            src_img.size,
            src_img.bOffset,
            src_img.gOffset,
            src_img.rOffset,
            src_img.aOffset
        )
        print("All tests passed.")


if __name__ == "__main__":
    print("Error: You must run this from the repo directory via:")
    print("python3 -m nose")
