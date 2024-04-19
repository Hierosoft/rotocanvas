#!/usr/bin/env python
import unittest
# import sys

from rotocanvas import (
    no_enclosures,
    DEFAULT_ENCLOSURES,
)


class ModuleTest(unittest.TestCase):
    def test_no_enclosures(self):
        pairs = DEFAULT_ENCLOSURES
        good_strings = [
            "A",
            "abcd",
            'ab"cd',
            "ab)cd",
        ]
        # enclosed_strings = {}
        for original in good_strings:
            # enclosed_strings[original] = []
            for pair in pairs:
                enclosed = (
                    pair[0]
                    + original.replace(pair[1], '\\' + pair[1])
                    + pair[1]
                )
                # enclosed_strings[original].append(enclosed)
                self.assertEqual(no_enclosures(enclosed), original)


if __name__ == "__main__":
    print("Error: You must run this from the repo directory via:")
    print("python3 -m nose")
