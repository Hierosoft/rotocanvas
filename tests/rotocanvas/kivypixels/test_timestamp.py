#!/usr/bin/env python3

import unittest
# import sys
from rotocanvas.timestamp import (
    srtTsToDelta,
    deltaToSrtTs,
    frame_to_ffmpeg_timecode,
)

from rotocanvas import (
    echo0,
    set_verbosity,
)


class TestTimestampConversionSRT(unittest.TestCase):
    def testGetsSameString(self):
        # sys.stderr.write("..testing timestamp.py..")
        echo0("testing timestamp.py...\n")
        # INFO: print will show nothing during nose tests unless a
        # failure occurs.
        oldStr = "04:32:21,341"
        delta = srtTsToDelta(oldStr)
        newStr = deltaToSrtTs(delta)
        echo0("* converted {} to delta and got {}"
              "".format(oldStr, delta))
        echo0("* converted delta back to SRT format and got {}"
              "".format(newStr))
        self.assertEqual(oldStr, newStr)
        echo0("All tests passed.")

    def testFFMPEGTimecode(self):
        echo0("testing frame_to_ffmpeg_timecode...")
        set_verbosity(2)
        self.assertEqual(frame_to_ffmpeg_timecode(11, 10), "0:0:1:150")
        # ^ 150 obtained using SpeedCrunch:
        '''
        1/10
        = 0.1

        ans/2
        = 0.05

        ans*1000
        = 50

        11*(1/10)
        = 1.1

        ans+(1/10/2)
        = 1.15

        .15*1000
        = 150
        '''
        set_verbosity(1)
        self.assertEqual(frame_to_ffmpeg_timecode(0, 60), "0:0:0:008")
        # ^ 8 obtained using SpeedCrunch:
        '''
        1/60
        = 0.01666666666666666667

        ans/2
        = 0.00833333333333333333

        ans*1000
        = 8.33333333333333333333

        round(ans)
        = 8
        '''
