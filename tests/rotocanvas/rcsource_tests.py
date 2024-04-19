#!/usr/bin/env python
import sys
import os
import platform
# formerly needed param: "/home/owner/Videos/Demo_Reel/media/
# Demo_Reel_2000_clip-Rebel_Assault_IX-318x468_2.05x_1280x960_alq-
# 1.0.1_jpg/"
# rotocanvas is from https://github.com/Poikilos/rotocanvas
# Below attempts to find it in %USERPROFILE%/git, %USERPROFILE%/GitHub
# (or same with $HOME if not Windows):

profile = None  # or RCProject.PROFILE
reposNames = ["git", "GitHub"]
if platform.system() == "Windows":
    profile = os.environ["USERPROFILE"]
else:
    profile = os.environ["HOME"]

print("profile: {}".format(profile))

if os.path.exists("../rotocanvas/__init__.py"):
    sys.path.append(os.path.realpath(".."))
else:
    for reposName in reposNames:
        reposDir = os.path.join(profile, reposName)
        tryModules = os.path.join(reposDir, "rotocanvas")
        if os.path.exists(tryModules):
            sys.path.append(tryModules)
            # ^ yes, the repo dir, because the module is under the
            # repo it is not the repo itself in a pip repo. See:
            # <https://pip.pypa.io/en/stable/development/architecture/
            # anatomy/>
            print("Using modules dir: {}".format(reposDir))
            break

from rotocanvas.ffmpegtime import FFMPEGTime  # noqa: E402
from rotocanvas.rcproject import RCProject  # noqa: E402
from rotocanvas.rcsource import RCSource  # noqa: E402
# from rotocanvas.rcsettings import settings

ra9Times = ["00:00:14", "00:00:41", "00:00:55", "00:02:20",
            "00:00:58.5", "00:02:35"]
ra9Frames60fps = [839, 2457, 3296, 3506, 8391, 9290]
job = 3
if job == 1:
    inPath = os.path.join("data", "Demo_Reel_2000_clip-RA9-318x468.mp4")
    video = RCProject(os.path.realpath(inPath), "60000/1001")
    video.superResolutionAI(
        onlyTimes=ra9Times,
        outFmt="jpg",
        forceRatio=(612, 468),
        preserveDim=0,
        organizeMode=2,
    )
elif job == 2:
    inPath = os.path.join("data", "Demo_Reel_2000_clip-RA9-612x468.mp4")
    video = RCSource(os.path.realpath(inPath), "60000/1001")
    video.superResolutionAI(
        onlyTimes=ra9Times,
        outFmt="jpg",
        organizeMode=2,
    )
elif job == 3:
    inPath = os.path.join(
        "data",
        "upscaling-tests",
        "Demo_Reel_2000_clip-RA9-612x468-nearest-50%_jpg",
        "originals",
        "000839.jpg"
    )
    video = RCSource(os.path.realpath(inPath), "60000/1001")
    video.superResolutionAI(
        onlyFrames=ra9Frames60fps,
        outFmt="jpg",
        organizeMode=2,
    )
