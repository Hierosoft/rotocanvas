#!/usr/bin/env python3
from __future__ import print_function
import math
import os
import platform
import sys
import unittest
from unittest import TestCase
import numpy as np  # only used when *not* using GIMP mode (nonumpy)

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

from channeltinker import nonumpy as nn
# from channeltinker.nonumpy import array, dot, float64, linalg


def assertAllEqual(a_vec, b_vec):
    if len(a_vec) != len(b_vec):
        raise AssertionError("{} != {} (length mismatch)"
                             .format(a_vec, b_vec))
    for i in range(len(a_vec)):
        assert a_vec[i] == b_vec[i], "{}[{}] != {}[{}]".format(a_vec, i, b_vec, i)

class TestChannelTinker(unittest.TestCase):
    def test_array_and_norm(self):
        x_pos = 2
        y_pos = 2
        x_center = 1
        y_center = 1
        # Define pos and center as float NumPy vec2 arrays
        pos = np.array([x_pos, y_pos], dtype=np.float64)
        nn_pos = nn.array([x_pos, y_pos], dtype=nn.float64)

        assertAllEqual(pos, nn_pos)

        center = np.array([x_center, y_center], dtype=np.float64)
        nn_center = nn.array([x_center, y_center], dtype=np.float64)

        assertAllEqual(center, nn_center)

        # Create (1,1) vector and normalize it
        quadrant_diagonal_vec2 = np.array([1.0, 1.0], dtype=np.float64)
        nn_quadrant_diagonal_vec2 = nn.array([1.0, 1.0], dtype=np.float64)

        assertAllEqual(quadrant_diagonal_vec2, nn_quadrant_diagonal_vec2)
        print("quadrant_diagonal_vec2 {} / np.linalg.norm(quadrant_diagonal_vec2) {}"
              .format(quadrant_diagonal_vec2, np.linalg.norm(quadrant_diagonal_vec2)))
        print("nn_quadrant_diagonal_vec2 {} / linalg.norm(nn_quadrant_diagonal_vec2) {}"
              .format(nn_quadrant_diagonal_vec2, nn.linalg.norm(nn_quadrant_diagonal_vec2)))
        quadrant_diagonal_vec2 /= np.linalg.norm(quadrant_diagonal_vec2)  # Normalize
        nn_quadrant_diagonal_vec2 /= nn.linalg.norm(nn_quadrant_diagonal_vec2)  # Normalize

        assertAllEqual(quadrant_diagonal_vec2, nn_quadrant_diagonal_vec2)
        print("All tests passed.")

    def test_dot(self):
        right = (1, 0)
        up = (0, 1)
        left = (-1, 0)
        self.assertAlmostEqual(np.dot(right, up), nn.dot(right, up))
        self.assertAlmostEqual(nn.dot(right, up), 0)

        self.assertAlmostEqual(np.dot(right, right), nn.dot(right, right))
        self.assertAlmostEqual(nn.dot(right, right), 1)

        self.assertAlmostEqual(np.dot(right, left), nn.dot(right, left))
        self.assertAlmostEqual(nn.dot(right, left), -1)



if __name__ == "__main__":
    unittest.main()
