import os

from collections import OrderedDict

REPO_DIR = os.path.dirname(os.path.realpath(__file__))
TESTS_DIR = os.path.join(REPO_DIR, "tests")
TESTS_DATA_DIR = os.path.join(TESTS_DIR, "data")

image_group_dirs = OrderedDict()
image_group_dirs['pil-compatible'] = \
    os.path.join(TESTS_DATA_DIR, "pil-compatible")
image_group_dirs['pil-incompatible'] = \
    os.path.join(TESTS_DATA_DIR, "pil-incompatible")
image_groups = OrderedDict()
for key, parent in image_group_dirs.items():
    image_groups[key] = []
    for sub in os.listdir(parent):
        sub_path = os.path.join(parent, sub)
        if not os.path.isfile(sub_path):
            continue
        image_groups[key].append(sub_path)
