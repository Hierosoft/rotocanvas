#!/usr/bin/env python
import os
import sys

_opencv_tip = None


class RCSettings:
    def __init__(self):
        modulePath = os.path.dirname(os.path.realpath(__file__))
        repoPath = os.path.dirname(modulePath)
        reposPath = os.path.dirname(repoPath)  # repos
        parentPath = os.path.dirname(reposPath)  # even higher up
        self.thisPython = "python"
        self._enable_opencv = False
        tryLocal = "/home/owner/Videos/Demo_Reel/media/"
        if os.path.isdir(os.path.join(parentPath, "opencvenv")):
            self.thisPython = os.path.join(reposPath, "opencvenv",
                                           "bin", "python")
            # print("Using python in virtual env for opencv: {}"
            # #     "".format(self.thisPython))
            self._enable_opencv = True
        elif os.path.isdir(os.path.join(tryLocal, "opencvenv")):
            self.thisPython = os.path.join(tryLocal, "opencvenv",
                                           "bin", "python")
            # print("Using python in virtual env for opencv: {}"
            # #     "".format(self.thisPython))
            self._enable_opencv = True
        else:
            try:
                import cv2
                self._enable_opencv = True
            except ImportError:
                print("Warning: No opencv")
        self.modulePath = os.path.join(
            os.path.dirname(os.path.realpath(__file__))
        )
        self.thisSRPy = os.path.join(
            self.modulePath,
            "super_res_image_save.py"
        )
        if not os.path.isfile(self.thisSRPy):
            print("WARNING: Missing {}".format(self.thisSRPy))
        self.thisScalePy = os.path.join(
            self.modulePath,
            "fix_ratio.py"
        )
        self.thisFFMpeg = "ffmpeg"
        tryDirs = []
        tryDirs.append(os.path.join("..", "..", "models"))
        tryDirs.append("/home/owner/Videos/Demo_Reel/media/"
                       "super-resolution/models/")
        self.scalingModelsDir = None
        for tryDir in tryDirs:
            if os.path.isdir(tryDir):
                self.scalingModelsDir = os.path.realpath(tryDir)
        if self.scalingModelsDir is None:
            self.scalingModelsDir = os.path.realpath("models")
            if not os.path.isdir(self.scalingModelsDir):
                print("WARNING: {} wasn't present, place them there or"
                      " in {}".format(tryDir, self.scalingModelsDir))
        self.scalingModels = []
        tryModels = [["EDSR_x4.pb", 4], ["ESPCN_x4.pb", 4],
                     ["FSRCNN_x3.pb", 3], ["LapSRN_x8.pb", 8]]
        for tryModel in tryModels:
            tryPath = os.path.join(self.scalingModelsDir, tryModel[0])
            if os.path.isfile(tryPath):
                self.scalingModels.append([tryPath, tryModel[1]])
                print("- found scaling model: {}".format(tryModel[0]))
        if len(self.scalingModels) < 1:
            modelNames = [model[0] for model in tryModels]
            print("WARNING: 0 models were found in {} (tried {})"
                  "".format(self.scalingModelsDir, modelNames))
        # The above correspond to the following commands
        # where
        # PY=./opencvenv/python
        # CMD=super_res_image.py
        # $PY $CMD --model models/EDSR_x4.pb --image examples/adrian.png
        # $PY $CMD --model models/ESPCN_x4.pb --image \
        #   examples/butterfly.png
        # $PY $CMD --model models/FSRCNN_x3.pb --image \
        #   examples/jurassic_park.png
        # $PY $CMD --model models/LapSRN_x8.pb --image \
        #   examples/zebra.png

    def addModel(self, path):
        if not os.path.isfile(path):
            raise ValueError("The path for addModel isn't a file or"
                             " doesn't exist: {}".format(path))
        self.scalingModels.append(path)

    def assertOpenCV(self):
        if not self._enable_opencv:
            if not os.path.isfile(self.thisPython):
                raise RuntimeError(_opencv_tip)


settings = RCSettings()

_opencv_tip = ("You must first install opencv-python available to {}"
               " or in a virtual environment"
               " at {}".format(sys.executable, settings.thisPython))
