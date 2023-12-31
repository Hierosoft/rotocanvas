#!/usr/bin/env python3

import os
import platform
from unittest import TestCase

from channeltinkerpil.diffimage import diff_image_files_and_gen

class TestChanneltinkerpil(TestCase):
    def test_diffimagewriting(self):
        tempDir = "/tmp"
        if platform.system() == "Windows":
            tempDir = os.environ['TEMP']
        tmpPngName = "test_channeltinkerpil-tmp.png"
        tempPngPath = os.path.join(tempDir, tmpPngName)

        myDir = os.path.dirname(os.path.abspath(__file__))
        dataPath = os.path.join(myDir, "data")
        basePath = os.path.join(dataPath, "test_diff_base.png")
        headPath = os.path.join(dataPath, "test_diff_head.png")

        diff = diff_image_files_and_gen(basePath, headPath, tempPngPath)
        print("* wrote: {}".format(tempPngPath))
        assert diff['same'] is False
        os.remove(tempPngPath)
        print("* removed: {}".format(tempPngPath))

        print("All tests passed.")
