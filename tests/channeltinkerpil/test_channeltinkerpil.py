#!/usr/bin/env python3
from __future__ import print_function
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
    sys.path.insert(0, REPO_DIR)
    print("[test_channeltinkerpil] using {}".format(REPO_DIR))
else:
    print("__name__={}".format(__name__))

# from channeltinker import diff_images

from channeltinkerpil import diff_images_by_path  # noqa: E402
from channeltinkerpil.diffimage import diff_image_files_and_gen  # noqa: E402

from rotocanvas import sysdirs  # noqa: E402

diff_base = os.path.join(
    sysdirs['HOME'],
    "Nextcloud/www.etc/minetest.org/www/imgsite/backgrounds/bg_hard_rock.png"
)

# test_cmd_parts = [
#     "findbyappearance",
#     diff_base,
#     os.path.join(sysdirs['HOME'], "minetest/games/bucket_game"),
# ]

_pil_incompatible_dir = os.path.join(sysdirs['HOME'], "minetest", "games",
                                     "bucket_game")

_pil_incompatible_files = [
    # 'mods/codercore/bucket/projects/textures000/bucket_lava_crust.png',  # corrupt, ignore  # noqa: E501
    'mods/codercore/coderskins/textures/coderskins_not_avail.png',
    'mods/codercore/default/textures/default_ladder_wood.png',
    'mods/codercore/default/textures/default_lava_crust.png',
    'mods/codercore/default/textures/default_lava_crust_flowing_animated.png',
    'mods/codercore/default/textures/default_lava_crust_source_animated.png',
    'mods/coderfood/farming/textures/farming_orange.png',
    'mods/codermobs/codermobs/projects/textures000/codermobs_bom_mesh.png',
    'mods/codermobs/codermobs/projects/textures000/codermobs_chicken_egg.png',
    'mods/codermobs/codermobs/projects/textures000/codermobs_denny_mesh.png',
    'mods/codermobs/codermobs/projects/textures000/codermobs_hen_mesh.png',
    'mods/codermobs/codermobs/projects/textures000/codermobs_mdskeleton_mesh.png',  # noqa E501
    'mods/codermobs/codermobs/textures/codermobs_denny_mesh.png',
    'mods/codermobs/codermobs/textures/codermobs_mdskeleton_mesh.png',
    'mods/codermobs/mobs/projects/textures000/mobs_chicken_egg.png',
    'mods/codermobs/mobs/projects/textures000/mobs_chicken_egg_overlay.png',
]
for sub in _pil_incompatible_files:
    sub_path = os.path.join(_pil_incompatible_dir, sub)
    if os.path.isfile(sub_path):
        print("* found " + sub_path)

pil_incompatible_dir = os.path.join(TEST_DATA_DIR, "pil-incompatible")
pil_incompatible_files = [
    "coderskins_not_avail.png",
    "farming_orange.png",
]

_pil_compatible_dir = pil_incompatible_dir
_pil_compatible_files = [
    'mods/coderbuild/xdecor/projects/textures000/ench_ui.png',
    'mods/codercore/bones/projects/textures000/bones_bottom.png',
    'mods/codercore/bones/projects/textures000/bones_rear.png',
    'mods/codercore/bones/projects/textures000/bones_top.png',
    'mods/codercore/default/textures/default_chest_front.jpg',
    'mods/codercore/prestibags/textures/prestibags_red.jpg',
    'mods/codercore/default/textures/default_chest_lock.jpg',
    'mods/codermobs/petores/projects/textures000/ironstone.png',
    'mods/codermobs/codermobs/projects/textures000/codermobs_goat_brown.png',
    'mods/codercore/default/textures/default_chest_top.jpg',
]
pil_compatible_dir = os.path.join(TEST_DATA_DIR, "pil-compatible")


class TestChanneltinkerpil(TestCase):
    def test_diffimagewriting(self):
        tempDir = "/tmp"
        if platform.system() == "Windows":
            tempDir = os.environ['TEMP']
        tmpPngName = "test_channeltinkerpil-tmp.png"
        tempPngPath = os.path.join(tempDir, tmpPngName)

        myDir = os.path.dirname(os.path.abspath(__file__))
        dataPath = os.path.join(myDir, "data")
        basePath = os.path.join(dataPath, "test_diff_base.png")
        headPath = os.path.join(dataPath, "test_diff_head.png")

        diff = diff_image_files_and_gen(basePath, headPath, tempPngPath)
        print("* wrote: {}".format(tempPngPath))
        assert diff['same'] is False
        os.remove(tempPngPath)
        print("* removed: {}".format(tempPngPath))

        print("All tests passed.")

    def test_pil_compatible_png(self):
        """Test PIL-incompatible PNG files.
        (See issue #14)
        Whatever method that passes this test should be used by *all*:
        - findbyappearance
        - diffimage
        - diffimage-gui
        - imagepx
        """
        # found_compatible = 0
        found_incompatible = 0
        for sub in pil_incompatible_files:
            sub = sub.replace("/", os.path.sep)
            sub_path = os.path.join(pil_incompatible_dir, sub)
            if not os.path.isfile(sub_path):
                print('Warning: no "{}"'.format(sub_path))
                continue
            this_base = diff_base
            try_base = os.path.join(pil_compatible_dir, sub)
            if os.path.isfile(try_base):
                this_base = try_base
                print('detected "{}"'.format(try_base))
                diff = diff_images_by_path(diff_base, this_base,
                                           raise_exceptions=True)
            diff = diff_images_by_path(diff_base, sub_path,
                                       raise_exceptions=True)
            if diff.get('error'):
                raise Exception("{}:".format(sub_path) + diff['error'])
            if 'same' not in diff:
                # Should only be missing if exception was raised,
                #   so if this happens, the implementation is wrong.
                raise KeyError("Missing 'same' in {}".format(diff))
            assert diff['same'] is False
            found_incompatible += 1

        if found_incompatible < 1:
            raise FileNotFoundError(
                "Can't do test since no test files are present."
            )


if __name__ == "__main__":
    unittest.main()
