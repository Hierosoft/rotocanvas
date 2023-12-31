#!/usr/bin/env python
import sys
import os
import platform
# formerly needed param: "/home/owner/Videos/Demo_Reel/media/
# Demo_Reel_2000_clip-Rebel_Assault_IX-318x468_2.05x_1280x960_alq-
# 1.0.1_jpg/"
# pyrotocanvas is from https://github.com/poikilos/pyrotocanvas
# Below attempts to find it in %USERPROFILE%/git, %USERPROFILE%/GitHub
# (or same with $HOME if not Windows):

profile = None  # or RCProject.PROFILE
reposNames = ["git", "GitHub"]
if platform.system() == "Windows":
    profile = os.environ["USERPROFILE"]
else:
    profile = os.environ["HOME"]

print("profile: {}".format(profile))

if os.path.exists("../pyrotocanvas"):
    sys.path.append("..")
else:
    for reposName in reposNames:
        reposDir = os.path.join(profile, reposName)
        tryModules = os.path.join(reposDir, "pyrotocanvas")
        if os.path.exists(tryModules):
            sys.path.append(tryModules)
            # ^ yes, the repo dir, because the module is under the
            # repo it is not the repo itself in a pip repo. See:
            # <https://pip.pypa.io/en/stable/development/architecture/
            # anatomy/>
            print("Using modules dir: {}".format(reposDir))
            break

from pyrotocanvas.ffmpegtime import FFMPEGTime
# from pyrotocanvas.rcproject import RCProject
from pyrotocanvas.rcsource import RCSource
# from pyrotocanvas.rcsettings import settings

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
        onlyFrames = ra9Frames60fps,
        outFmt="jpg",
        organizeMode=2,
    )
