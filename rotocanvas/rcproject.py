#!/usr/bin/env python
import os
import sys
import json
import platform
from datetime import datetime

try:
    from rcsettings import settings
except ModuleNotFoundError:
    modules = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(modules)
    print("[rcproject] Using {} for modules.".format(modules))
    from rcsettings import settings

from rcsource import RCSource

class RCProject:
    PROFILE = None
    APPDATAS = None
    if platform.system() == "Windows":
        PROFILE = os.environ.get("USERPROFILE")
        APPDATAS = os.path.join(PROFILE, "AppData", "Local")
    else:
        PROFILE = os.environ.get("HOME")
        APPDATAS = os.path.join(PROFILE, ".config")
    RC_APPDATA = None
    if APPDATAS is not None:
        RC_APPDATA = os.path.join(APPDATAS, "rotocanvas")
    VIDEOS = os.path.join(PROFILE, "Videos")
    if not os.path.isdir(VIDEOS):
        if os.path.isdir(PROFILE):
            VIDEOS = PROFILE

    def __init__(self):
        """
        Use a list of models (pb file paths in self.models) along with
        OpenCV to upscale images at multiple quality levels.

        Sequential arguments:
        vidPath -- the video file
        fpsStr -- the framerate in string format to avoid floating point
            accuracy issues (may be fractional such as 30000/10001 or
            60000/1001)

        Keyword arguments:
        extensions -- Specify image extensions to try (only applies if
                      vidPath is a directory). If None, use the default
                      list (RCProject.extensions).
        """

        self._startTime = datetime.now()
        self.timestamp_fmt = "%Y-%m-%d %H..%M..%S"
        ts = datetime.strftime(self._startTime, self.timestamp_fmt)
        self._name = "Untitled_{}.rotocanvas".format(ts)
        self._dir = RCProject.VIDEOS
        self._meta = {}
        self._videos = {}


    def addVideo(self, vidPath, fpsStr):
        """
        Add an RCSource
        (vidPath becomes the key in the self._videos dict).

        Sequential arguments:
        vidPath - the path to the video file (or directory if image
                  sequence)
        fpsStr - the frames per second as a string

        Returns:
        error string or None
        """
        old = self._videos.get(vidPath)
        if old is not None:
            vp = vidPath
            return "There is already a video loaded as \"\"".format(vp)
        self._videos[vidPath] = RCSource(vidPath, fpsStr)
        return None


    def stop(self):
        return "Not Yet Implemented"

    def open(self, path):
        self.path = path
        with open(self.path, 'r') as ins:
            self._meta = json.load(ins)

    def save(self):
        if self._name is None:
            return "You have not set a path."
        with open(self.path, 'w') as outs:
            json.dump(self._meta, outs, indent=2, sort_keys=True)
        print("[rcproject.py] Saved \"{}\"".format(self.path))

    @property
    def path(self):
        return os.path.join(self._dir, self._name)

    @path.setter
    def path(self, value):
        self._dir = os.path.split(value)[0]
        self._name = os.path.split(value)[1]

    @path.deleter
    def path(self):
        """ called via: del object.name """
        raise RuntimeError("You can't delete path.")
        # del self._name

