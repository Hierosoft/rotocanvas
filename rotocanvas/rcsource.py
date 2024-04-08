#!/usr/bin/env python
import os
import sys
import subprocess
import shutil
import time
myName = "rcsource.py"
try:
    from rcsettings import settings
except ModuleNotFoundError:
    modules = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(modules)
    print("[rcsource] Using {} for modules.".format(modules))
    from rcsettings import settings

from ffmpegtime import FFMPEGTime
from util import splitframename
from util import get_frame_name
opencv_enabled = False
try:
    import cv2
    opencv_enabled = True
except ImportError:
    whereMsg = ""
    how = [
        ":"
        "python3 -m venv opencvenv",
        "source ./opencvenv/bin/activate",
        "pip install --upgrade pip setuptools wheel",
        "pip install opencv-python",
        "pip install opencv-contrib-python  # dnn_superres etc",
        "#(you still need the binary version of opencv on your system)",
    ]
    tryPath = "/home/owner/Videos/Demo_Reel/media/opencvenv/bin/python3"
    if os.path.isfile(tryPath):
        whereMsg = " such as running via \"{}\"".format(tryPath)
    else:
        whereMsg = " such as you can create via" + "\n    ".join(how)
    sys.stderr.write("WARNING: To use OpenCV you must install OpenCV"
                     " for Python or use a venv with OpenCV{}.\n"
                     "".format(whereMsg))
    # exit(1)


class RCSource:
    _defaultExtensions = ["jpg", "jpeg", "jpe", "png", "bmp"]
    ORGANIZE_MODEL_DIR = 0
    ORGANIZE_PREFIX = 1
    ORGANIZE_FRAME_NUM_DIR = 2

    def __init__(self, vidPath, fpsStr, extensions=None):
        if extensions is None:
            extensions = RCSource._defaultExtensions
        self._extensions = extensions
        lowerDotExts = ["."+ext.lower() for ext in extensions]
        dotExt = os.path.splitext(vidPath)[1]
        isImage = False
        self._ext = None
        if len(dotExt) > 0:
            self._ext = dotExt[1:]
            if self._ext in extensions:
                isImage = True
            else:
                print("[rcsource init] INFO: detected {} as video."
                      "".format(self._ext))
        else:
            print("[rcsource init] WARNING: no file extension.")
        # else leave it as None, so people don't end filename in .
        # accidentally (via: name + "." + self._ext)

        self._prefix = None  # NOT including path nor numbers nor ext
        self._first = None  # first frame number
        fullPath = os.path.realpath(vidPath)
        self._fileName = os.path.split(fullPath)[-1]
        self._dir = os.path.dirname(fullPath)
        self._minDigits = None
        if os.path.isdir(vidPath):
            raise ValueError("The path must be a file not a"
                             " directory.")
            # for sub in os.listdir(vidPath):
            # subPath = os.path.join(vidPath, sub)
            # if os.path.isfile(subPath):
        print("[rcsource init] _dir: {}".format(self._dir))
        print("[rcsource init] _fileName: {}".format(self._fileName))
        if isImage:
            self._prefix, numberS, de = splitframename(self._fileName)
            if de != dotExt:
                raise RuntimeError("splitframename got {} not {}"
                                   " for extension.".format(de, dotExt))
            self._minDigits = len(numberS)
            # first = get_frame_number(firstFramePath, prefix=prefix,
            # _minDigits=_minDigits)
            try:
                self._first = int(numberS)
            except ValueError:
                self._first = None
            print("[rcsource init] _prefix: {}".format(self._prefix))
            print("[rcsource init] _first: {}".format(self._first))
            print("[rcsource init] _ext: {}".format(self._ext))
            print("[rcsource init] _minDigits: {}"
                  "".format(self._minDigits))

        self._vidPathNoExt = os.path.splitext(vidPath)[0]
        self.fpsStr = fpsStr

    @property
    def vidPath(self):
        frame = self._first if self._first is not None else ""
        return self._vidPathNoExt + frame + self._ext

    def isImageSequence(self):
        if (self._first is None) and (self._ext in self._extensions):
            # single image
            return True
        return self._first is not None

    @property
    def fpsStrDecimal(self):
        if "/" in self.fpsStr:
            parts = self.fpsStr.split("/")
            if len(parts) != 2:
                raise ValueError("The fractional framerate must be in"
                                 "exactly two parts but is in {}: {}"
                                 "".format(len(parts), self.fpsStr))
            return float(parts[0]) / float(parts[1])

    def getAllFrameNumbers(self):
        if self._first is not None:
            raise NotImplementedError("getAllFrameNumbers is only"
                                      " implemented for single images")
        return [None]

    def getFrameName(self, thisFrame, minDigits):
        if self._first is None:
            # single image
            dotExt = ""
            if self._ext is not None:
                dotExt = "." + self._ext
            return os.path.split(self._vidPathNoExt)[1] + dotExt
        return get_frame_name(self._prefix, thisFrame,
                              minDigits, self._ext)

    def superResolutionAI(self, onlyTimes=None, forceRatio=None,
                          outFmt="jpg", qscale_v=2, minDigits=None,
                          preserveDim=1, organizeMode=0,
                          onlyFrames=None):
        """Perform AI super-resolution on all frames.
        Args:
            onlyFrames (Optional[list[str]]): If not None, extract only
                individual frames using this list of times (each time is
                for one frame). Each time must be a timecode string such
                as 00:02:35 or 00:02:35.345.
            forceRatio (Optional[tuple[int]]): If specified, this must
                be a 2 element tuple or list of numbers that together
                describe the final ratio.
            qscale_v (Optional[int]): This "-qscale:v" value for ffmpeg
                is only for JPEG. JPEG is 2-31 where 31 is worst quality
                according to llogan on
                <https://stackoverflow.com/questions/10225403/
                how-can-i-extract-a-good-quality-jpeg-image-from-a-video-
                file-with-ffmpeg> edited Sep 24 at 22:20.
            _minDigits (Optional[int]): This is the image sequence
                minimum digits (only for image output). This should take
                the length of the video. For example, a 4hr video has
                863136 frames at 59.96fps, so if the video is 4hrs then
                the _minDigits should be 6. If _minDigits is not None
                (such as if this is an image sequence, the default is
                self._minDigits.
            preserveDim (Optional[int]): Set this to 0 if you want to
                keep the width the same when enforcing the ratio. To
                keep the height the same, set it to 1.
            organizeMode (Optional[int]): If 1, put result files all in
                the same directory regardless of the AI upscaling model
                (prefix the filename with the algorithm instead). If 0,
                place results of each model in separate directories. If
                2, place all files of the same frame in the same
                directory. Pass a RCSource.ORGANIZE_* constant for
                clarity.
        """
        if minDigits is None:
            if self._minDigits is not None:
                minDigits = self._minDigits
        settings.assertOpenCV()
        dimNumbers = (0, 1)
        if preserveDim not in dimNumbers:
            raise RuntimeError("Only 0 (width) and 1 (height) are video"
                               " dimensions.")
        onlyOne = True

        if self.isImageSequence():
            thisFrame = self._first

        atList = None
        if onlyTimes is not None:
            # TIMES
            if self.isImageSequence():
                atList = onlyTimes
                onlyTimes = [self._first]
                onlyOne = True
            else:
                raise NotImplementedError("You must specify a time list"
                                          "unless you use an image.")
        elif onlyFrames is not None:
            # FRAMES
            atList = onlyFrames
        else:
            p = os.path.dirname(self.vidPath)
            lde = ["."+ext.lower() for ext in self._extensions]
            atList = []
            for sub in os.listdir(p):
                if not sub.startswith(self._prefix):
                    continue
                if sub.lower() not in lde:
                    continue
                pre, frameS, de = splitframename(sub)
                atList.append(int(frameS))
            # ENTIRE
            # TODO: make a new iterable (iterate frames in image list)
            if self.isImageSequence():
                # TODO: create onlyFrames based on times!
                if onlyFrames is not None:
                    onlyTimes = onlyFrames
                    raise NotImplementedError("A time list isn't"
                                              " implemented for images"
                                              ".")
                else:
                    atList = self.getAllFrameNumbers()
        # framesPath = os.path.join(self._dir)
        print("[sr] isImageSequence: {}".format(self.isImageSequence()))
        for atS in atList:
            timeStr = None
            if self.isImageSequence():
                thisFrame = atS
                outDir = os.path.join(self._dir, "scaled")
                if thisFrame is not None:
                    paddedNum = str(int(thisFrame)).zfill(minDigits)
                    outName = "{}{}.{}".format(self._prefix, paddedNum,
                                               outFmt)
                else:
                    outName = "{}.{}".format(
                        os.path.split(self._vidPathNoExt)[1],
                        outFmt
                    )

            else:
                timeStr = atS
                # tmpSuffix = timeStr.replace(":", "_")
                thisTime = FFMPEGTime(timeStr, self.fpsStrDecimal)
                thisFrame = thisTime.getFrameNumber()
                # vidNameNoExt = os.path.split(self._vidPathNoExt)[-1]
                # paddedNum = "{}-{}".format(vidNameNoExt, thisFrame)
                paddedNum = str(int(thisFrame)).zfill(minDigits)
                outDir = "{}_{}".format(self._vidPathNoExt, outFmt)
                outName = "{}.{}".format(paddedNum, outFmt)
            print("outName: {}".format(outName))
            outPath = os.path.join(outDir, outName)
            print("Frame number: {}".format(thisFrame))
            if not os.path.isdir(outDir):
                os.makedirs(outDir)

            if not self.isImageSequence():
                # print("paddedNum: {}".format(paddedNum))
                # print("outName: {}".format(outName))
                # print("outDir: {}".format(outDir))
                # print("outPath: {}".format(outPath))
                # exit(1)
                # See llogan's answer edited Dec 20 '14 at 2:08
                # answered Dec 19 '14 at 19:55
                # on https://stackoverflow.com/questions/27568254/how-to-extract-1-screenshot-for-a-video-with-ffmpeg-at-a-given-time  # noqa: E501
                # ffmpeg -ss $thisTimeCode -i "$vidPath" -vframes 1 -q:v 2 "$tmpImPath-$tmpSuffix.jpg"  # noqa: E501
                # ffmpeg -ss $thisTimeCode -i "$vidPath" -vframes 1 "$tmpImPath-$tmpSuffix.png"  # noqa: E501

                # extract by frame number:
                #   ffmpeg -i in.mp4 -vf select='eq(n\,100)+eq(n\,184)+eq(n\,213)'  # noqa: E501
                #     -vsync 0 frames%d.jpg
                cmdParts = [self.thisFFMpeg, "-y", "-i", self.vidPath, "-ss",
                            timeStr, "-vframes", "1"]
                oFLower = outFmt.lower()
                if (oFLower == "jpg") or (oFLower == "jpeg"):
                    cmdParts.append("-qscale:v")
                    cmdParts.append(str(qscale_v))
                cmdParts.append(outPath)
                subprocess.check_output(cmdParts)
                print('* wrote "{}"'.format(outPath))

                originalsDir = os.path.join(outDir, "originals")
                if not os.path.isdir(originalsDir):
                    os.makedirs(originalsDir)
                originalPath = os.path.join(originalsDir, outName)
                shutil.move(outPath, originalPath)
            else:
                frameName = self.getFrameName(thisFrame, minDigits)

                originalPath = os.path.join(self._dir, frameName)
            print("originalPath: {}".format(originalPath))
            print("outDir: {}".format(outDir))
            print("outPath: {}".format(outPath))
            if originalPath == outPath:
                raise RuntimeError("[{}] * failed to generate a"
                                   " different filename from the"
                                   " original.".format(myName))
            if not os.path.isfile(originalPath):
                raise ValueError("{} does not exist."
                                 "".format(originalPath))
            for model, multiplier in settings.scalingModels:
                mFileName = os.path.split(model)[-1]
                mName = os.path.splitext(mFileName)[0]
                mOutName = None
                mOutDir = None
                if organizeMode == 0:
                    # separate by model
                    mOutDir = os.path.join(outDir, mName)
                    mOutName = outName
                    mOutPath = os.path.join(mOutDir, mOutName)
                elif organizeMode == 1:
                    # keep in same directory and add prefix
                    mOutDir = outDir
                    # if mName[-1] in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                    mOutName = mName + "_" + outName
                    # else:
                    # mOutName = mName + outName
                    mOutPath = os.path.join(mOutDir, mOutName)
                elif organizeMode == 2:
                    # separate by frame number
                    mOutDir = os.path.join(outDir, paddedNum)
                    if not os.path.isdir(mOutDir):
                        os.makedirs(mOutDir)
                    mOutName = mName + "_" + outName
                    mOutPath = os.path.join(mOutDir, mOutName)
                else:
                    raise ValueError("organizeMode {} is not"
                                     "implemented."
                                     "".format(organizeMode))
                if not os.path.isdir(mOutDir):
                    os.makedirs(mOutDir)
                print("* upscaling as {}...".format(mOutPath))
                """
                srCmdParts = [settings.thisPython, settings.thisSRPy,
                              "--model",
                              model, "--image", originalPath,
                              "--output", mOutPath]
                subprocess.check_output(srCmdParts)
                """
                # extract the model name and model scale from the file path
                modelName = model.split(os.path.sep)[-1].split("_")[0].lower()
                modelScale = model.split("_x")[-1]
                modelScale = int(modelScale[:modelScale.find(".")])
                print("[INFO] loading super resolution model: {}"
                      "".format(model))
                print("[INFO] model name: {}".format(modelName))
                print("[INFO] model scale: {}".format(modelScale))
                sr = cv2.dnn_superres.DnnSuperResImpl_create()
                sr.readModel(model)
                sr.setModel(modelName, modelScale)
                image = cv2.imread(originalPath)
                outPath = mOutPath
                print("[INFO] w: {}, h: {}".format(image.shape[1],
                                                   image.shape[0]))
                start = time.time()
                upscaled = sr.upsample(image)
                end = time.time()
                print("[INFO] super resolution took {:.6f} seconds"
                      "".format(end - start))
                print("[INFO] w: {}, h: {}".format(upscaled.shape[1],
                      upscaled.shape[0]))
                sys.stderr.write('[{}] writing "{}"\n'.format(myName,
                                                              outPath))
                cv2.imwrite(outPath, upscaled)

                if forceRatio is not None:
                    print("  * downscaling to fix aspect ratio...")
                    aiTmpDir = os.path.join(mOutDir, "ai_tmp")
                    if not os.path.isdir(aiTmpDir):
                        os.makedirs(aiTmpDir)
                    aiTmpPath = os.path.join(aiTmpDir, mOutName)
                    shutil.move(mOutPath, aiTmpPath)
                    regularCmdParts = [settings.thisPython,
                                       settings.thisScalePy,
                                       "-i", aiTmpPath,
                                       "-o", mOutPath,
                                       "-r0", str(forceRatio[0]),
                                       "-r1", str(forceRatio[1]),
                                       "-p", str(preserveDim)]
                    print("Running: {}".format(" ".join(
                        regularCmdParts
                    )))
                    subprocess.check_output(regularCmdParts)
                    print('  * wrote "{}"'.format(mOutPath))
