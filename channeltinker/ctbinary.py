from __future__ import print_function

import sys

try:
    import puremagic  # pure python implementation of magic
except ImportError:
    print("If apt is available, try:", file=sys.stderr)
    print("  sudo apt install python3-puremagic", file=sys.stderr)
    print("Otherwise 'pip install puremagic'  # preferably in a Python venv",
          file=sys.stderr)
    raise

textchars = \
    bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})


def is_binary_string(bytes_):
    bool(bytes_.translate(None, textchars))


def is_binary_file(path):
    with open(path, 'rb') as stream:
        return is_binary_string(stream.read(1024))


def is_image_file(path):
    result = puremagic.magic_file(path)[0]
    # ^ Each entry is a PureMagicWithConfidence object.
    # ^ highest confidence match is first, so take 0.
    # print("match_info={}({})"
    #       "".format(type(result).__name__, result))
    # ^ attributes (using a PNG as an example):
    #   - byte_match=b'\x89PNG\r\n\x1a\n'
    #   - offset=0,
    #   - extension='.png'
    #   - mime_type="image/png"
    #   - name="Portable Network Graphics file"
    #   - confidence=0.9
    if result.mime_type.startswith("image"):
        return True
    return False
