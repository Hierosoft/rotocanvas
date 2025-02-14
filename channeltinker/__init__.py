#!/usr/bin/env python
"""
This module provides image and pixel manipulation that does not depend
on a specific library.
"""
from __future__ import print_function
from __future__ import division
import json
import os
import math
try:
    import numpy as np
except ImportError:
    import channeltinker.nonumpy as np
import sys
import platform

_draw_square_dump = None
_square_dump_name = "draw_square_dump.json"
last_square_dump_path = ""

configs_dir = None

def set_configs_dir(path):
    global configs_dir
    configs_dir = path
    if not os.path.isdir(configs_dir):
        os.makedirs(configs_dir)

name_fmt0 = "{}-{}-vs-{}.png"
name_fmt1 = "diffimage {}.png"
name_fmt2 = "diffimage {} vs. {}.png"
verbosity = False
print("channeltinker: Loading", file=sys.stderr)

if sys.version_info.major >= 3:
    from logging import getLogger
    logger = getLogger(__name__)
else:
    class Logger():
        def error(message):
            print("[channeltinker] Error: {}".format(message),
                  file=sys.stderr)

        def warning(message):
            print("[channeltinker] Warning: {}".format(message),
                  file=sys.stderr)

    logger = Logger()

def safePathParam(path):
    if "'" in path:
        return "'" + path.replace("'", "\\'") + "'"
    quotableChars = " \""
    for quotableChar in quotableChars:
        if quotableChar in path:
            return "'" + path + "'"
    return path


platformCmds = {
    'cp': 'cp',
    'mv': 'mv',
    'rm': 'rm',
}
if platform.system() == "Windows":
    platformCmds = {
        'cp': 'copy',
        'mv': 'move',
        'rm': 'del',
    }
    # TODO: Redefine safePathParam if necessary.


def emit_cast(value):
    return "{}({})".format(type(value).__name__, repr(value))


class ChannelTinkerProgressInterface:

    def progress_update(self, factor):
        """
        Set the progress value, from 0.0 to 1.0.
        """
        raise NotImplementedError("The ChannelTinkerProgressInterface"
                                  " implementation must implement"
                                  " progress_update.")

    def set_status(self, msg):
        """
        Set the progress text (such as gimp.progress_init(msg))
        """
        raise NotImplementedError("The ChannelTinkerProgressInterface"
                                  " implementation must implement"
                                  " set_status.")

    def show_message(self, msg):
        """
        Show a dialog box, or other delay with message
        (such as pdb.gimp_message(msg))
        """
        raise NotImplementedError("The ChannelTinkerProgressInterface"
                                  " implementation must implement"
                                  " show_message.")


# (The @property decorator is always available in Python 3, since every
# class descends from Object but must be explicit for compatibility
# with Python 2).
class ChannelTinkerInterface(object):
    """Abstract superclass for non-PIL images.
    If you do not provide a PIL image to various functions in this
    library, you can implement ChannelTinkerInterface and provide an
    object based on your own implementation instead.
    """

    @property
    def size(self):
        """
        This property will be accessed like: w, h = cti.size or using
        cti.size[0] or cti.size[1] individually.
        """
        raise NotImplementedError("The ChannelTinkerInterface"
                                  " implementation must implement size as"
                                  " a @property.")

    def getpixel(self, pos):
        raise NotImplementedError("The ChannelTinkerInterface"
                                  " implementation must implement"
                                  " getpixel.")

    def putpixel(self, pos, color):
        raise NotImplementedError("The ChannelTinkerInterface"
                                  " implementation must implement"
                                  " putpixel.")

    def getbands(self):
        """
        Get a tuple that specifies the channel order as
        characters, such as ('R', 'G', 'B', 'A') (or tuple('L') for
        grayscale).
        """
        # Probably deprecated in Gegl (just use color.set_rgba?)
        raise NotImplementedError("The ChannelTinkerInterface"
                                  " implementation must implement"
                                  " getbands.")


_echo_fn = None


def _echo(*msg, **kwargs):
    print(*msg, file=sys.stderr, **kwargs)


_echo_fn = _echo


# Mimic logging module:
# - debug(), info(), warning(), error() and critical()
# - default WARNING
# - CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10


def echo0(*msg, **kwargs):
    """Send msg + newline to stderr
    (or send msg without anything extra to a callback you previously
    specified via set_echo).
    # Formerly error
    """
    _echo_fn(*msg, **kwargs)


def echo1(*msg, **kwargs):
    if verbosity < 1:
        return False
    _echo_fn(*msg, **kwargs)
    return True


def echo2(*msg, **kwargs):
    if verbosity < 2:
        return False
    _echo_fn(*msg, **kwargs)
    return True


def echo3(*msg, **kwargs):
    if verbosity < 3:
        return False
    _echo_fn(*msg, **kwargs)
    return True


def echo4(*msg, **kwargs):
    if verbosity < 4:
        return False
    _echo_fn(*msg, **kwargs)
    return True


def set_echo(callback):
    """Set the echo callback
    If at any time an error or other message occurs anywhere in the
    module, the module will either send (*args, **kwargs) to callback or
    raise an exception.
    """
    global _echo_fn
    _echo_fn = callback


def quadrant_of_pos(pos, axis=None, inverse_cartesian=False):
    if axis is not None:
        old_pos = pos
        pos = []
        for i in range(len(old_pos)):
            pos.append(old_pos[i]-axis[i])
    if pos[0] < 0:
        if ((pos[1] * -1) if inverse_cartesian else pos[1]) < 0:
            return 2  # 3rd
        else:
            return 1  # 2nd
    else:  # right side
        if ((pos[1] * -1) if inverse_cartesian else pos[1]) < 0:
            return 3  # 4th
        else:
            return 0  # 1st


def convert_depth(color, channel_count, c_max=1.0):
    """Convert any color to a 0-255 color.
    Args:
        c_max (Union[float,int]): If color is a float or list of floats
            to this image, this is the value that is 100%. Otherwise,
            this argument is ignored.

    Returns:
        tuple(int): Color where each value is between 0 and 255
            (regardless of input x_max).
    """
    list_like = None
    # Perform duck typing:
    try:
        tmp_len = len(color)
        try:
            tmp_lower = color.lower()
            list_like = False
        except AttributeError:
            # AttributeError: 'list' object has no attribute 'lower'
            list_like = True
    except TypeError:
        # object of type 'int' has no len()
        list_like = False

    if list_like:
        # list, tuple, RGB (gimp color), or other
        if isinstance(color[0], float):
            new_color = []
            for v in color:
                new_color.append(convert_depth(v, 1, c_max=c_max)[0])
            color = tuple(color)
        elif not isinstance(color, tuple):
            color = tuple(color)
    elif isinstance(color, int):
        color = tuple([color])
    elif isinstance(color, float):
        if color > c_max:
            color = c_max
        elif color < 0.0:
            color = 0.0
        prev_color = color
        color = tuple([int(round((color/c_max) * 255))])
        # logger.warning("converting {} to"
        #       " {}".format(prev_color, color))

    p_len = channel_count
    new_color = None
    if p_len > len(color):
        new_color = [i for i in color]
        while len(new_color) < p_len:
            new_color.append(255)
        # logger.warning("expanding {} to"
        #       " {}".format(color, new_color))
    elif p_len < len(color):
        if (p_len == 1) and (len(color) >= 3):
            # FIXME: assumes not indexed
            v = float(color[0] + color[1] + color[2]) / 3.0
            prev_color = color
            color = tuple([int(round(v))])
            # logger.warning("shrinking {} to"
            #       " {}".format(prev_color, color))
        else:
            new_color = []
            for i in range(p_len):
                new_color.append(color[i])
            # logger.warning("expanding {} to"
            #       " {}".format(color, new_color))
    if new_color is not None:
        color = tuple(new_color)
    return color


def square_gen(pos, rad, enable_np=True):
    left = pos[0] - rad
    right = pos[0] + rad
    top = pos[1] - rad
    bottom = pos[1] + rad
    x = left
    y = top
    v_count = left - right + 1
    h_count = bottom - (top + 1)
    ender = v_count * 2 + h_count * 2
    ss_U = 0
    ss_D = 1
    ss_L = 2
    ss_R = 3
    d = ss_R
    while True:
        if enable_np:
            yield np.array((x, y), dtype=np.float64)
        else:
            yield (x, y)
        # Do not use `elif` below:
        # Each case MUST fall through to next case, or a square with 0
        # radius will be larger than 1 pixel, and possibly other
        # positions out of range will generate.
        if d == ss_R:
            x += 1
            if x > right:
                x = right
                d = ss_D
        if d == ss_D:
            y += 1
            if y > bottom:
                y = bottom
                d = ss_L
        if d == ss_L:
            x -= 1
            if x < left:
                x = left
                d = ss_U
        if d == ss_U:
            y -= 1
            if y < top:
                y = top
                break


def distance_squared_to(p1, p2):
    return sum((a - b) ** 2 for a, b in zip(p1, p2))


def fdist(a_pt, b_pt):
    if not (isinstance(a_pt, (list, tuple, np.array)) and isinstance(b_pt, (list, tuple, np.array))):
        raise TypeError("Both points must be lists")
    if len(a_pt) != len(b_pt):
        raise ValueError("Points must have the same dimension")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(a_pt, b_pt)))


def idist(p1, p2):
    return fdist(p1, p2)
    if len(p1) != len(p2):
        raise ValueError("Length mismatch for {} and {}"
                         .format(p1, p2))
    if len(p1) == 2:
        return math.sqrt((float(p2[0]) - float(p1[0]))**2
                          + (float(p2[1]) - float(p1[1]))**2)
    raise NotImplementedError("{}D points".format(len(p1)))


def profile_name():
    # INFO: expanduser("~") is cross-platform
    return os.path.split(os.path.expanduser("~"))[-1]


def get_drive_name(path):
    drive_name = None
    mount_parents = ["/mnt", "/run/media/" + profile_name(), "/media",
                     "/amnt", "/auto",  # typical custom fstab parents
                     "/Volumes"]  # macOS
    for parent in mount_parents:
        if path.startswith(parent):
            slash = "/"
            if "\\" in parent:
                slash = "\\"
            offset = 1
            if parent[-1] == slash:
                offset = 0
            drive_rel = path[len(parent) + offset:]
            drive_parts = drive_rel.split(slash)
            drive_name = drive_parts[0]
            break
    return drive_name


def generate_diff_name(base_path, head_path, file_name=None):
    """Generate a filename for saving a diff visualization."""
    if file_name is None:
        if os.path.isfile(base_path):
            file_name = os.path.split(base_path)[-1]
    if file_name is None:
        file_name = "diffimage"
    base_name = os.path.split(base_path)[-1]
    head_name = os.path.split(head_path)[-1]
    diff_name = name_fmt0.format(file_name, base_name, head_name)
    if (base_name == head_name):
        base_drive = get_drive_name(base_name)
        head_drive = get_drive_name(head_name)
        if (base_drive is not None) and (head_drive is not None):
            diff_name = name_fmt2.format(base_name + " (in " + base_drive,
                                         "in " + head_drive + ")")
        elif base_drive is not None:
            diff_name = name_fmt1.format(
                "(base in " + base_drive + " vs " + head_name
            )
        elif head_drive is not None:
            diff_name = name_fmt1.format(
                base_name + " (vs one in " + head_drive + ")"
            )
        else:
            base_l, base_r = os.path.split(base_path)
            head_l, head_r = os.path.split(head_path)
            while True:
                echo1("* building name from {} vs {}...".format(
                    (base_l, base_r), (head_l, head_r)
                ))
                if (base_l == "") and (head_l == ""):
                    diff_name = name_fmt2.format("(both further up)",
                                                 head_r)
                    break
                elif (base_r == "") and (head_r == ""):
                    break
                elif base_r == "":
                    diff_name = name_fmt2.format(
                        "(a further up " + base_name + " vs in " + head_r + ")"
                    )
                    break
                elif head_r == "":
                    diff_name = name_fmt1.format(
                        base_name + " (vs one further up)"
                    )
                    break
                elif base_r != head_r:
                    # such as "default_furnace_front_active.png-
                    # bucket_game-200527-vs-bucket_game.png"
                    diff_name = name_fmt0.format(
                        file_name,
                        base_r,
                        head_r
                    )
                    break
                base_l, base_r = os.path.split(base_l)
                head_l, head_r = os.path.split(head_l)

    return diff_name


def diff_color(base_color, head_color, enable_convert=False,
               c_max=255, base_indices=None, head_indices=None,
               enable_real_diff=True, max_count=3):
    """Compare two colors.
    In most cases, when the color start with [r, g, b], the defaults are
    fine.

    If you want to compare all 3 colors, and the
    color does not start with [r, g, b], then you should set
    base_indices and head_indices. For example, if color starts with
    alpha, you should set: base_indices=[1,2,3], head_indices=[1,2,3]
    (which skips 0, which would be alpha in that case).

    Returns a difference value from -1.0 to 1.0, where 0.0 is the same
    (negative if base is brighter)

    Args:
        base_color (tuple[Union[int,float]]): Original color.
        head_color (tuple[Union[int,float]]): Color to compare to
            base_color.
        enable_convert (bool, optional): If True, convert color if
            length differs (even if base_indices and head_indices are
            set).
        c_max (Union[float,int], optional): The color format's 100%
            value for a channel (only used if color conversion occurs).
        base_indices (tuple[int], optional): If not None, it is a list
            of channel indices to compare (only these channels will be
            checked). If None, sequential indices are used.
        head_indices (tuple[int], optional): If not None, it is a list
            of channel indices to compare (only these channels will be
            checked). If None, sequential indices are used.
        max_count (int, optional) Only ever count this many channels,
            unless base_indices and head_indices are both set to a
            higher value, in which case, max_count does not do anything.
        enable_real_diff (bool, optional): If True, 0.0 will only occur
            if all checked channels are exactly the same. If False,
            return 0.0 may occur if colors have the same brightness but
            a different color.


    Returns:
        float: the difference from -1.0 to 1.0

    Raises:
        IndexError if different length and not enable_convert or
            any value from base_indices or head_indices is out of range.
        ValueError if  base_indices and head_indices are both set but the
            length differs.
    """
    try:
        if len(base_color) != len(head_color):
            if enable_convert:
                if len(base_color) > len(head_color):
                    head_color = convert_depth(head_color, len(base_color),
                                               c_max=float(c_max))
                else:
                    base_color = convert_depth(base_color, len(head_color),
                                               c_max=float(c_max))
            else:
                raise ValueError("The channel counts do not match, and"
                                 " enable_convert is False.")
    except TypeError as ex:
        # TypeError: object of type 'int' has no len()
        print("base: {}, head {}".format(base_color, head_color))
        raise ex
    base_indices_msg = "from parameter"
    head_indices_msg = "from parameter"
    if base_indices is None:
        base_indices = [i for i in range(min(len(base_color), max_count))]
        base_indices_msg = "generated"
    if head_indices is None:
        head_indices = [i for i in range(min(len(head_color), max_count))]
        head_indices_msg = "generated"
    if len(base_indices) != len(head_indices):
        raise ValueError(
            "The base_indices length ({}, {}) does not match the"
            " head_indices length ({}, {})".format(len(base_indices),
                                                   base_indices_msg,
                                                   len(head_indices),
                                                   head_indices_msg)
        )
    # max_diff = 255 * max(len(base_color), len(head_color))
    diff = 0.0
    if enable_real_diff:
        for ii in range(len(base_indices)):
            i = base_indices[ii]
            base_v = base_color[i]
            head_v = head_color[i]
            if base_v != head_v:
                diff += abs(float(base_v) - float(head_v))
    else:
        for ii in range(len(base_indices)):
            i = base_indices[ii]
            base_v = base_color[i]
            head_v = head_color[i]
            if base_v != head_v:
                diff += float(base_v) - float(head_v)
    return diff / float(len(base_indices) * c_max)


def diff_images(base, head, diff_size, diff=None,
                nochange_color=(0, 0, 0, 255),
                enable_variance=True, c_max=255, max_count=4,
                base_indices=(0, 1, 2, 3), head_indices=(0, 1, 2, 3),
                clear_in_stats=False):
    """Compare two images, and return a dict with information.

    If diff is not None, it must also be an image, and it will be
    changed. Only parts will be changed where base and head differ.
    Grayscale will always be used the amount of difference.

    The base and head images are converted to true color using the PIL
    convert function (always 32-bit so that channel counts match) of the
    image object. If convert isn't called, the getpixel function gets a
    palette index for indexed images. The channel count must match for
    getpixel as well.

    Args:
        base (Union(Image,ChannelTinkerInterface)): This is the first
            image for the difference operation.
        head (Union(Image,ChannelTinkerInterface)): This is the second
            image for the difference operation.
        diff_size (tuple[int]): For the purpose of not assuming assuming
            how to get the image size, you must provide the canvas size.
            You must set it to (max(base.width, head.width),
            max(base.height, head.height)) The diff_size is used for the
            area to search for differences, so it is necessary even if
            diff is None and no diff will be generated.
        nochange_color (tuple, optional): If not using RGBA, set this to
            a tuple of the length of a color. Assume this is the
            background color (This is never drawn, but if set, then it
            will not be used for anything else unless this is gray).
        enable_variance (float, optional): set the actual absolute color
            difference
        c_max (Union(float, int), optional): Pixels in the image can go
            up to this value.
        max_count (int), optional: only compare this number of channels.
        base_indices (list[int], optional): only compare these channels
            from head (length must match either that of head_indices, or
            if that is None, then match the head channel count.
        head_indices (list[int], optional): only compare these channels
            from head (length must match either that of base_indices, or
            if that is None, then match the base channel count.
        clear_in_stats (bool, optional): Whether to use transparent
            pixels when calculating statistics such as diff_mean.
    """
    base = base.convert(mode='RGBA')
    head = head.convert(mode='RGBA')
    # Convert indexed images so getpixel doesn't return an index
    # (diff_color expects a tuple).
    results = {}
    results['same'] = None
    results['base'] = {}
    results['base']['size'] = base.size
    results['base']['ratio'] = float(base.size[0]) / float(base.size[1])
    results['head'] = {}
    results['head']['size'] = base.size
    results['head']['ratio'] = float(head.size[0]) / float(head.size[1])
    total_diff = 0
    total_count = 0

    w, h = diff_size
    add_color = (0, c_max, 0, c_max)  # green (expanded part if any)
    del_color = (c_max, 0, 0, c_max)  # red (cropped part if any)
    pix_len = len(nochange_color)
    if isinstance(nochange_color, str):
        raise ValueError("You provided a string for nochange_color but"
                         " a tuple or tuple-like number collection is"
                         " required.")
    if not isinstance(nochange_color, tuple):
        nochange_color = tuple(nochange_color)
    for c in nochange_color:
        if not isinstance(c, type(c_max)):
            raise ValueError("The type of c_max and nochange_color"
                             " members does not match. You must set"
                             " both to float or to int, etc.")
    if pix_len != 4:
        if pix_len == 1:
            add_color = tuple([c_max])
            del_color = tuple([c_max])
        elif pix_len <= 4:
            add_color = convert_depth(add_color, pix_len, c_max=c_max)
            del_color = convert_depth(del_color, pix_len, c_max=c_max)

    if add_color == nochange_color:
        # choose an unused color (cast value to type of c_max):
        tmp_color = (0, type(c_max)(c_max / 2), 0, c_max)  # dark green
        if tmp_color == nochange_color:
            tmp_color = (c_max, c_max, 0, 0, c_max)  # yellow
            add_color = convert_depth(tmp_color, pix_len, c_max=c_max)
        else:
            add_color = convert_depth(tmp_color, pix_len, c_max=c_max)
    if del_color == nochange_color:
        # choose an unused color (cast value to type of c_max)
        tmp_color = (type(c_max)(c_max / 2), 0, 0, c_max)  # dark red
        if tmp_color == nochange_color:
            tmp_color = (c_max, 0, c_max, 0, c_max)  # magenta
            del_color = convert_depth(tmp_color, pix_len, c_max=c_max)
        else:
            del_color = convert_depth(tmp_color, pix_len, c_max=c_max)

    for y in range(h):
        for x in range(w):
            pos = (x, y)
            color = nochange_color
            if (x >= base.size[0]) or (y >= base.size[1]):
                color = add_color
                total_diff += 1.0
                total_count += 1
            elif (x >= head.size[0]) or (y >= head.size[1]):
                color = del_color
                total_diff += 1.0
                total_count += 1
            else:
                try:
                    base_color = base.getpixel(pos)
                    head_color = head.getpixel(pos)
                except IndexError as ex:
                    echo1("base.size: {}".format(base.size))
                    echo1("head.size: {}".format(head.size))
                    echo1("pos: {}".format(pos))
                    raise ex
                d = diff_color(base_color, head_color, c_max=c_max,
                               max_count=max_count)
                base_a = c_max
                head_a = c_max
                if pix_len > 3:
                    base_a = base_color[3]
                    head_a = head_color[3]
                if clear_in_stats:
                    if (base_a > 0) and (head_a > 0):
                        total_diff += math.fabs(d)
                        total_count += 1
                    else:
                        total_diff += 1.0
                        total_count += 1
                else:
                    if (base_a > 0) and (head_a > 0):
                        total_diff += math.fabs(d)
                        total_count += 1
                    elif (base_a > 0) or (head_a > 0):
                        total_diff += 1.0
                        total_count += 1
                    # Else don't even count it toward total or weight.
                if d != 0.0:
                    # color = (c_max, c_max, c_max, c_max)
                    this_len = min(pix_len, 3)
                    color = [type(c_max)(c_max * d) for i in range(this_len)]
                    for i in range(pix_len - this_len):
                        color.append(c_max)
                    color = tuple(color)

            if color != nochange_color:
                results['same'] = False
                if diff is not None:
                    diff.putpixel(pos, color)
            else:
                if results['same'] is None:
                    results['same'] = True
    if total_count <= 0:
        results['error'] = "WARNING: There were no pixels."
    else:
        results['mean_diff'] = float(total_diff) / float(total_count)
    return results


def convert_channel(value, new_type, name=None):
    if isinstance(value, new_type):
        return value
    if name is None:
        name = ""
    else:
        name = " " + name
    if new_type is int:
        if isinstance(value, float):
            return int(round(value * 255))
        else:
            raise TypeError(
                "Unknown{} type {}"
                .format(name, emit_cast(value)))
    elif new_type is float:
        if isinstance(value, int):
            return float(value / 255)
        else:
            raise TypeError(
                "Unknown{} type {}"
                .format(name, emit_cast(value)))
    else:
        raise TypeError(
            "Unknown pixel type {}"
            .format(emit_cast(new_type)))


def find_opaque_pos(cti, center, good_minimum=1.0, max_rad=None,
                    w=None, h=None):
    """Find the position of an opaque pixel within the image.
    Args:
        cti (Union(Image,ChannelTinkerInterface)): Original image.
        center (tuple(float)) This location, or the closest location to
            it meeting criteria, is the search target.
        good_minimum (int, optional) (0 to 1.0) If the pixel's alpha is
            this or higher, get it (the closest in location to center).
    """
    int_mode = False
    max_a = -1
    px_type = cti.getPixelType()
    # if not isinstance(good_minimum, px_type):
    #     good_minimum = convert_channel(good_minimum, px_type,
    #                                    name="good_minimum")
    if int_mode:
        if float(good_minimum) != float(int(good_minimum)):
            # indicates range is 0 to 1.0 (Use 0 to 255 in int_mode)
            raise NotImplementedError(
                "In int mode, but got good_minimum={}"
                .format(emit_cast(good_minimum)))
    else:
        assert255 = convert_channel(255, px_type, "assert255")
        assert assert255 == 1.0, "convert(255)={} expected 1".format(assert255)
        if px_type is not float:
            raise NotImplementedError(
                "Everything except UI should be float as of GIMP 3.0 (Gegl),"
                " but got px_type {}".format(px_type))
        if not isinstance(good_minimum, float):
            raise NotImplementedError(
                "Everything except UI should be float as of GIMP 3.0 (Gegl),"
                " but got good_minimum={}".format(emit_cast(good_minimum)))
        if good_minimum > 1.0:
            raise NotImplementedError(
                "Everything except UI should be float (0 to 1.0)"
                " as of GIMP 3.0 (Gegl), but got good_minimum={}"
                .format(emit_cast(good_minimum)))
    circular = True
    # ^ True fails for some reason (try it in
    #   draw_square to see the problem).
    if good_minimum < 0:
        good_minimum = 0
    epsilon = sys.float_info.epsilon
    rad = 0
    if w is None:
        if h is None:
            w, h = cti.size
        else:
            w, tmp_h = cti.size
    if h is None:
        if w is None:
            w, h = cti.size
        else:
            tmp_w, h = cti.size
    if max_rad is None:
        max_rad = 0
        side_distances = [
            abs(0 - center[0]),
            abs(w - center[0]),
            abs(0 - center[1]),
            abs(h - center[1]),
        ]
        for dist in side_distances:
            if dist > max_rad:
                max_rad = dist
    # print("find_opaque_pos(...,{},...) # max_rad:{}".format(center,
    #                                                         max_rad))
    positions = []
    rad_f = 0.0
    for rad in range(0, max_rad + 1):
        # print("  rad: {}".format(rad))
        rad_f = float(rad) + epsilon + 1.0
        # left = center[0] - rad
        # right = center[0] + rad
        # top = center[1] - rad
        # bottom = center[1] + rad
        positions += square_gen(center, rad)
        # NOTE: only positions in rad_f are used below

    sorted_positions = sorted(positions, key=lambda p: idist(p, center))
    rad_f_squared = rad_f ** 2
    for pos in sorted_positions:
        x, y = pos
        if y < 0:
            continue
        if y >= h:
            continue
        if x < 0:
            continue
        if x >= w:
            continue
        dist = idist(center, pos)
        dist_sq = distance_squared_to(center, pos)
        # if (not circular) or (dist <= rad_f):
        if (not circular) or (dist_sq <= rad_f_squared):
            # limit to circle if circular
            # print("  navigating square {} ({} <="
            #       " {})".format(pos, dist, rad))
            pixel = cti.getpixel(pos)
            if pixel[3] > max_a:
                max_a = pixel[3]
                if max_a > 1.0:
                    raise NotImplementedError(
                        "Everything except UI should be float (0 to 1)"
                        " as of GIMP 3.0 (Gegl) but got {}".format(pixel))
            if pixel[3] >= good_minimum:
                return pos
        else:
            # print("  navigating square {} SKIPPED ({} > "
            #       "{})".format(pos, dist, rad))
            pass
    logger.warning("find_opaque_pos max_a={} (too low)".format(max_a))
    return None


def save_draw_square_dump():
    global last_square_dump_path
    if _draw_square_dump is None:
        raise RuntimeError(
            "There is no square drawn yet."
            " Call draw_square_from_center first."
        )
    if not configs_dir:
        try_path = os.path.expanduser("~/git/rotocanvas")
        if os.path.isdir(try_path):
            set_configs_dir(try_path)
    path = _square_dump_name
    if configs_dir:
        path = os.path.join(configs_dir, _square_dump_name)
    elif last_square_dump_path:
        path = last_square_dump_path
    with open(path, "w") as stream:
        json.dump(_draw_square_dump, stream)
    last_square_dump_path = os.path.realpath(path)
    print("Saved {}".format(repr(last_square_dump_path)))


def draw_square_from_center(cti, center, rad, color=None, filled=False,
                            circular=False, dump=False):
    """Draw a square centered within the image.
    Args:
        cti (Union(Image,ChannelTinkerInterface)): Original image.
    """
    global _draw_square_dump
    _draw_square_dump = {}
    # Get any available pixel, to get p_len:
    # p_len = len(cti.getbands())
    # pixel = cti.getpixel(0, 0)
    # color = convert_depth(color, p_len)
    # new_channels = p_len  # must match dest, else ExecutionError in GIMP 2.0
    new_channels = 4
    w, h = cti.size
    if color is None:
        if new_channels == 1:
            color = (0)
        elif new_channels == 2:
            color = (0, 255)
        elif new_channels == 3:
            color = (0, 0, 0)
        elif new_channels == 4:
            color = (0, 0, 0, 255)
        else:
            color = [255 for i in range(new_channels)]
    radii = None
    epsilon = sys.float_info.epsilon
    radii = [rad] if not filled else list(range(0, rad + 1))
    diag = math.sqrt(2.0)  # one diagonal (don't miss edge of circle)
    # print("using diagonal pixel measurement: {}".format(diag))
    # print("using epsilon: {}".format(epsilon)) ~2.220446049250313e-16
    diag_offset = math.sqrt(2) / 2
    # cart_quad_mid_vec2s = (  # cartesian
    #     np.array([diag_offset, diag_offset], dtype=np.float64),
    #     np.array([-diag_offset, diag_offset], dtype=np.float64),
    #     np.array([-diag_offset, -diag_offset], dtype=np.float64),
    #     np.array([diag_offset, -diag_offset], dtype=np.float64),
    # )
    quadrant_mid_vec2s = (  # inverse cartesian
        np.array([diag_offset, -diag_offset], dtype=np.float64),
        np.array([-diag_offset, -diag_offset], dtype=np.float64),
        np.array([-diag_offset, diag_offset], dtype=np.float64),
        np.array([diag_offset, diag_offset], dtype=np.float64),
    )
    center = np.array(center)
    print("using radii={}".format(radii))
    # rad_f_squared = float(rad) ** 2
    c_x = float(center[0])
    c_y = float(center[1])
    largest_rad = float(rad)
    for rad in radii:
        # rad_f = float(rad) + epsilon + diag * 2  # +1px diagonal for coverage
        for pos in square_gen(center, rad):
            x, y = pos
            if x < 0 or y < 0 or x >= w or y >= h:
                continue
            rad_f = largest_rad + .5
            # q_i = quadrant_of_pos(pos-center)
            # quad_mid_vec2 = quadrant_mid_vec2s[q_i]
            # diagonality = \
            #     max(0, np.dot(quad_mid_vec2, (pos - center)) - 0.5) * 2.0
            # rad_f = float(largest_rad) + epsilon + diag * diagonality
            # rad_f = float(rad) + diag_offset
            # rad_f_squared = float(rad**2) + diag_offset**2
            # # ^ only add diagonal offset of pixel *here* (not sqrt(2) always)
            # dist = idist(center, pos)
            # # dist_sq = distance_squared_to(center, pos)
            # dist2 = math.sqrt((pos[0]-center[0])**2 + (pos[1]-center[1])**2)
            # manhattan_dist = abs(pos[0] - center[0]) + abs(pos[1] - center[1])
            # # print(pos, "-", center, "=", pos-center, "idist", round(dist, 3), "distance", round(dist2, 3))
            # # print("  navigating square {} ({} <= {})".format(pos, dist,
            # #                                                  rad))
            # # dist = math.dist(center, pos)
            # used = 1
            # # if (not circular) or (dist_sq <= rad_f_squared):
            # dist = 0
            dist = math.sqrt((x - c_x)**2 + (y - c_y)**2)
            if circular:
                if dist > rad_f:
                    if dump:
                        _draw_square_dump['{},{}'.format(pos[0], pos[1])] = dist
                    continue
            # if (not circular) or (dist <= rad_f):
            #     used = dist / rad_f
            cti.putpixel((x, y), color)
            if dump:
                _draw_square_dump['{},{}'.format(pos[0], pos[1])] = dist
    if dump:
        save_draw_square_dump()


def draw_circle_from_center(cti, center, rad, color=None, filled=False):
    """Draw a centered circle
    (Simplifies calling draw_square_from_center with circular=True)

    Args:
        cti (Union(Image,ChannelTinkerInterface)): Original image.
    """
    return draw_square_from_center(cti, center, rad, color=color,
                                   filled=filled, circular=True)


def extend(cti, minimum=1, maximum=254,
           make_opaque=False, good_minimum=255, enable_threshold=False,
           threshold=128, ctpi=None):
    """Fix missing or incorrect bleed color on an image with alpha.
    Extrapolate the color of semi-transparent pixels by changing each to
    a nearby opaque one's color (outpainting ~2px doesn't require a
    generative "AI" model...hurumph).

    Args:
        cti (Union(Image,ChannelTinkerInterface)): Original image.
        minimum (int, optional): (0 to 255) Only edit pixels with at
            least this for alpha.
        maximum (int, optional): (0 to 254) Only edit pixels with at
            most this for alpha.
        make_opaque (bool, optional): Make the pixel within the range
            opaque. This is normally for preparing to convert images to
            indexed color, such as Minetest wield_image.
        ctpi (ChannelTinkerProgressInterface, optional): To update a
            progress bar or similar progress feature, provide an
            implementation of ChannelTinkerProgressInterface.
    """

    if maximum < 0:
        maximum = 0
    if minimum < 0:
        minimum = 0
    if maximum > 254:
        maximum = 254

    px_type = cti.getPixelType()
    if px_type is float:
        assert255 = convert_channel(255, px_type, "assert255")
        assert assert255 == 1.0, "convert(255)={} expected 1".format(assert255)
    else:
        raise NotImplementedError(
            "Everything except UI should be float as of GIMP 3.0 (Gegl),"
            " but extend got px_type {}".format(px_type))

    if not isinstance(minimum, px_type):
        minimum = convert_channel(minimum, px_type, name="minimum")
    if not isinstance(good_minimum, px_type):
        good_minimum = convert_channel(good_minimum, px_type,
                                       name="good_minimum")
    else:
        logger.warning(
            "good_minimum is already {}: {}"
            .format(px_type, emit_cast(good_minimum)))
    if not isinstance(maximum, px_type):
        maximum = convert_channel(maximum, px_type, name="maximum")
    if not isinstance(threshold, px_type):
        threshold = convert_channel(threshold, px_type, name="threshold")
    if px_type is float:
        if minimum > 1.0:
            raise NotImplementedError(
                "Everything except UI should be float as of GIMP 3.0 (Gegl),"
                " but got minimum={}".format(emit_cast(minimum)))

    w, h = cti.size

    # print("Size: {}".format((w, h)))
    px_count = w * h
    total_f = float(px_count)
    count_f = 0.0
    # ok = True
    n_pix = None
    msg = None
    max_a = -1.0
    error_counts = {}
    formatted_errors = {}
    def collect_error(msg_fmt, *values):
        if msg_fmt not in error_counts:
            error_counts[msg_fmt] = 1
        else:
            error_counts[msg_fmt] += 1
        formatted_errors[msg_fmt] = (
            msg_fmt.format(*values)
            + " ({} occurrence(s))".format(error_counts[msg_fmt])
        )
        return formatted_errors[msg_fmt]
    done_ratio = 0.0
    for y in range(h):
        # if not ok:
        #     break
        for x in range(w):
            used_th = False
            # if count_f is None:
            count_f = float(y) * float(w) + float(x)
            # print("checking {}".format(cti.getpixel((x, y))))
            # p_len = len(cti.getbands())
            pixel = cti.getpixel((x, y))
            if (pixel[3] >= minimum) and (pixel[3] <= maximum):
                # if all([p == q for p, q in zip(pixel,
                #                                color_to_edit)]):
                pos = (x, y)
                # print("Looking for pixel near {}...".format(pos))
                opaque_pos = find_opaque_pos(cti, (x, y), w=w, h=h,
                                             good_minimum=good_minimum)
                if opaque_pos is not None:
                    if opaque_pos == pos:
                        msg_fmt = (
                            "Uh oh, got own pos when checking"
                            " for better color than"
                            " {} (a>={})..."
                        )
                        msg_values = [pixel, good_minimum]
                        msg = collect_error(msg_fmt, msg_values)

                        if msg is None:  # only show 1 messagebox
                            echo1(msg)
                            if ctpi is not None:
                                pass
                                # commented since 'error' return shown anyway:
                                # ctpi.show_message(msg)
                                # ctpi.progress_update(0.0)
                                # ctpi.progress_update(done_ratio)
                            # ok = False
                        if ctpi is not None:
                            ctpi.set_status(msg)
                    else:
                        n_pix = cti.getpixel(opaque_pos)
                        # p_len = len(cti.getbands())
                        if n_pix != pixel:
                            if make_opaque:
                                # n_pix = (n_pix[0], n_pix[1],
                                #              n_pix[2], 255)
                                # Keep alpha from good pixel instead of
                                # using 255.
                                pass
                            else:
                                n_pix = (n_pix[0], n_pix[1],
                                         n_pix[2], pixel[3])
                            if enable_threshold:
                                if pixel[3] > threshold:
                                    n_pix = (n_pix[0], n_pix[1],
                                             n_pix[2], 255)
                                else:
                                    n_pix = (n_pix[0], n_pix[1],
                                             n_pix[2], 0)
                                used_th = True

                            # print("Changing pixel at {} from {} to "
                            #       "{}".format((x, y), pixel, n_pix))
                            # print("Changing pixel at {} using color from"
                            #       " {}".format((x, y), opaque_pos))
                            cti.putpixel((x, y), n_pix)
                        else:
                            # if msg is None:  # only show 1 messagebox
                            # msg = ("Uh oh, got own {} color {} at {} when"
                            #        " checking for color at better pos"
                            #        " than {}...".format(pixel, n_pix,
                            #                             opaque_pos, pos))
                            # print(msg)
                            # if ctpi is not None:
                            #     ctpi.show_message(msg)
                            #     ctpi.set_status(msg)
                            #     ctpi.progress_update(count_f / total_f)
                            # count_f = None
                            # time.sleep(10)
                            # return {'error': msg}
                            # continue
                            pass
                else:
                    if msg is None:  # only show 1 messagebox
                        msg = ("Uh oh, the image has no pixels at or"
                               " above the minimum good alpha.")
                        print(msg)
                        if ctpi is not None:
                            ctpi.show_message(msg)
                    if not enable_threshold:
                        return {'error': msg}
            if enable_threshold and not used_th:
                if pixel[3] > threshold:
                    n_pix = (pixel[0], pixel[1], pixel[2], 255)
                else:
                    n_pix = (pixel[0], pixel[1], pixel[2], 0)
                cti.putpixel((x, y), n_pix)
            if count_f is not None:
                # count_f += 1.0
                if ctpi is not None:
                    ctpi.progress_update((count_f + 1.0) / total_f)
                    # ^ + 1 since pixel 0 is done when count_f is 0
            # if ctpi:
            #     done_ratio = (y*w + (x+1)) / total_f
            #     ctpi.progress_update(done_ratio)
        # if ctpi:
        #     done_ratio = y / (h - 1)
        #     ctpi.progress_update(done_ratio)
    if formatted_errors:
        msg = str(formatted_errors.values())
    return {
        'error': msg,
    }