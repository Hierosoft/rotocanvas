#!/usr/bin/env python3

import unittest
import sys
from rotocanvas.timestamp import (
    srtTsToDelta,
    deltaToSrtTs,
)

from rotocanvas import (
    prerr,
)

class TestTimestampConversionSRT(unittest.TestCase):
    def testGetsSameString(self):
        sys.stderr.write("..testing timestamp.py..")
        # INFO: print will show nothing during nose tests unless a
        # failure occurs.
        oldStr = "04:32:21,341"
        delta = srtTsToDelta(oldStr)
        newStr = deltaToSrtTs(delta)
        print("* converted {} to delta and got {}"
              "".format(oldStr, delta))
        print("* converted delta back to SRT format and got {}"
              "".format(newStr))
        self.assertEqual(oldStr, newStr)
        print("All tests passed.")
