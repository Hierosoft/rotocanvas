#!/usr/bin/env python3
from __future__ import print_function
import math
import os
import platform
import sys
import unittest
from unittest import TestCase

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TEST_DATA_DIR = os.path.join(TESTS_DIR, "data")

if __name__ == "__main__":
    # ^ dirname twice since nested (tests/*/*.py)
    REPO_DIR = os.path.dirname(TESTS_DIR)
    flag_file = os.path.join(REPO_DIR, "channeltinker", "__init__.py")
    if os.path.isfile(flag_file):
        sys.path.insert(0, REPO_DIR)
    else:
        pass
        # raise FileNotFoundError(flag_file)
else:
    print("__name__={}".format(__name__))

import channeltinker

print("[test_channeltinkerpil] using {}".format(REPO_DIR))
print("[test_channeltinkerpil] using {}".format(channeltinker.__file__))

class TestChannelTinker(unittest.TestCase):
    def test_dist_functions(self):
        print("testing idist")
        self.dist(channeltinker.idist)
        print("testing fdist")
        self.dist(channeltinker.fdist)

    def dist(self, idist):
        self.assertAlmostEqual(idist((-8, 99), (8, 99)), 16)
        self.assertAlmostEqual(idist((-8, -99), (8, -99)), 16)
        self.assertAlmostEqual(idist((-1, -1), (1, 1)), math.sqrt(2) * 2)
        self.assertAlmostEqual(idist((-10, -10), (10, 10)), math.sqrt(2) * 20)
        self.assertAlmostEqual(idist((-10, 10), (10, -10)), math.sqrt(2) * 20)
        pos0 = (0, 0)
        diagonals = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        for diagonal in diagonals:
            self.assertAlmostEqual(math.sqrt(2.0), idist(pos0, diagonal))
            self.assertAlmostEqual(math.sqrt(2.0), idist(diagonal, pos0))

        start_points = []
        end_points = []
        move_factor = 70
        for diagonal in diagonals:
            start_points.append((pos0[0]+diagonal[0]*move_factor, pos0[1]+diagonal[1]*move_factor))
            end_points.append((diagonal[0]+diagonal[0]*move_factor, diagonal[1]+diagonal[1]*move_factor))
        for i in range(len(start_points)):
            print("[{}] testing idist({}, {})".format(i, start_points[i], end_points[i]))
            self.assertAlmostEqual(math.sqrt(2.0), idist(start_points[i], end_points[i]))
            print("[{}] testing idist({}, {})".format(i, end_points[i], start_points[i]))
            self.assertAlmostEqual(math.sqrt(2.0), idist(end_points[i], start_points[i]))

        start_points = []
        end_points = []
        scale_factor = 2
        for diagonal in diagonals:
            start_points.append((pos0[0]+diagonal[0], pos0[1]+diagonal[1]))
            end_points.append((diagonal[0]+diagonal[0]*scale_factor, diagonal[1]+diagonal[1]*scale_factor))

        for i in range(len(start_points)):
            self.assertAlmostEqual(math.sqrt(2.0) * scale_factor, idist(start_points[i], end_points[i]))
            self.assertAlmostEqual(math.sqrt(2.0) * scale_factor, idist(end_points[i], start_points[i]))

        self.assertAlmostEqual(idist([-2, -3], [-5, -7]), 5.0)

        self.assertEqual(idist([2, 3], [2, 3]), 0.0)

        self.assertAlmostEqual(idist([1, 2, 3], [4, 5, 6]), math.sqrt(27))

        with self.assertRaises(TypeError):
            idist(123, [1, 2])
        with self.assertRaises(TypeError):
            idist([1, 2], "not a list")

        with self.assertRaises(ValueError):
            idist([1, 2], [1, 2, 3])

    def test_convert_channel(self):
        result = channeltinker.convert_channel(1.0, int)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 255)

        result = channeltinker.convert_channel(1, float)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 1 / 255)

    def test_quadrant_of_pos(self):
        first = 0
        second = 1
        third = 2
        fourth = 3
        self.assertEqual(channeltinker.quadrant_of_pos((2, -1), inverse_cartesian=True), first)
        self.assertEqual(channeltinker.quadrant_of_pos((2, -1)), fourth)  # since inverse cartesian should be default

        self.assertEqual(channeltinker.quadrant_of_pos((-2, -1), inverse_cartesian=True), second)
        self.assertEqual(channeltinker.quadrant_of_pos((-2, -1)), third)  # since inverse cartesian should be default

        self.assertEqual(channeltinker.quadrant_of_pos((-2, 1), inverse_cartesian=True), third)
        self.assertEqual(channeltinker.quadrant_of_pos((-2, 1)), second)  # since inverse cartesian should be default

        self.assertEqual(channeltinker.quadrant_of_pos((2, 1), inverse_cartesian=True), fourth)
        self.assertEqual(channeltinker.quadrant_of_pos((2, 1)), first)  # since inverse cartesian should be default

if __name__ == "__main__":
    unittest.main()
