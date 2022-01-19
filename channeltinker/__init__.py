#!/usr/bin/env python
"""
This module provides image and pixel manipulation that does not depend
on a specific library.
"""
import os
import math
import sys
import platform

name_fmt0 = "{}-{}-vs-{}.png"
name_fmt1 = "diffimage {}.png"
name_fmt2 = "diffimage {} vs. {}.png"
verbose = False


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
    """
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
        raise NotImplementedError("The ChannelTinkerInterface"
                                  " implementation must implement"
                                  " getbands.")




_error_func = None


def _error(msg):
    sys.stderr.write("{}\n".format(msg))
    sys.stderr.flush()

_error_func = _error

def error(msg):
    """
    Send msg + newline to stderr (or send msg without anything extra
    to a callback you previously specified via set_error_func).
    """
    _error_func(msg)

def debug(msg):
    if verbose:
        error(msg)

def set_error_func(callback):
    """
    Set the error callback. If at any time an error occurs anywhere in
    the module, the module will either send a string to callback or
    raise an exception.
    """
    global _error_func
    _error_func = callback


def convert_depth(color, channel_count, c_max=1.0):
    """
    Keyword arguments:
    c_max -- If color is a float or list of floats to this image,
        this is the value that is 100%. Otherwise, this argument is
        ignored.

    Returns:
    Always get a tuple with numbers between 0 and 255.
    """
    listlike = None
    # Perform duck typing:
    try:
        tmp_len = len(color)
        try:
            tmp_lower = color.lower()
            listlike = False
        except AttributeError:
            # AttributeError: 'list' object has no attribute 'lower'
            listlike = True
    except TypeError:
        # object of type 'int' has no len()
        listlike = False

    if listlike:
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
        # print(msg_prefix + "WARNING: converting {} to"
        #       " {}".format(prev_color, color))

    p_len = channel_count
    new_color = None
    if p_len > len(color):
        new_color = [i for i in color]
        while len(new_color) < p_len:
            new_color.append(255)
        # print(msg_prefix + "WARNING: expanding {} to"
        #       " {}".format(color, new_color))
    elif p_len < len(color):
        if (p_len == 1) and (len(color) >=3):
            # FIXME: assumes not indexed
            v = float(color[0] + color[1] + color[2]) / 3.0
            prev_color = color
            color = tuple([int(round(v))])
            # print(msg_prefix + "WARNING: shrinking {} to"
            #       " {}".format(prev_color, color))
        else:
            new_color = []
            for i in range(p_len):
                new_color.append(color[i])
            # print(msg_prefix + "WARNING: expanding {} to"
            #       " {}".format(color, new_color))
    if new_color is not None:
        color = tuple(new_color)
    return color


def square_gen(pos, rad):
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
        yield (x,y)
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


def fdist(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


def idist(pos1, pos2):
    fpos1 = [float(i) for i in pos1]
    fpos2 = [float(i) for i in pos2]
    return fdist(fpos1, fpos2)


def profile_name():
    # INFO: expanduser("~") is cross-platform
    return os.path.split(os.path.expanduser("~"))[-1]


def get_drive_name(path):
    drive_name = None
    mount_parents = ["/mnt", "/run/media/" + profile_name(), "/media",
                     "/amnt", "/auto",  # typical custom fstab parents
                     "/Volumes"] # macOS
    for parent in mount_parents:
        if path.startswith(parent):
            slash = "/"
            if "\\" in parent:
                slash = "\\"
            offset = 1
            if parent[-1] == slash:
                offset = 0
            drive_rel = path[len(parent)+offset:]
            drive_parts = drive_rel.split(slash)
            drive_name = drive_parts[0]
            break
    return drive_name


def generate_diff_name(base_path, head_path, file_name=None):
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
            diff_name = name_fmt2.format(base_name+" (in "+base_drive,
                                         "in "+head_drive+")")
        elif base_drive is not None:
            diff_name = name_fmt1.format(
                "(base in "+base_drive+" vs "+head_name
            )
        elif head_drive is not None:
            diff_name = name_fmt1.format(
                base_name+" (vs one in "+head_drive+")"
            )
        else:
            base_l, base_r = os.path.split(base_path)
            head_l, head_r = os.path.split(head_path)
            while True:
                error("* building name from {} vs {}...".format(
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
                        "(a further up "+base_name+" vs in "+head_r+")"
                    )
                    break
                elif head_r == "":
                    diff_name = name_fmt1.format(
                        base_name+" (vs one further up)"
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
    """
    Compare two colors. In most cases, when the color start with
    [r, g, b], the defaults are fine.

    If you want to compare all 3 colors, and the
    color does not start with [r, g, b], then you should set
    base_indices and head_indices. For example, if color starts with
    alpha, you should set: base_indices=[1,2,3], head_indices=[1,2,3]
    (which skips 0, which would be alpha in that case).

    Returns a difference value from -1.0 to 1.0, where 0.0 is the same
    (negative if base is brighter)

    Keyword arguments:
    enable_convert -- If True, convert color if length differs (even if
        base_indices and head_indices are set).
    c_max -- The color format's 100% value for a channel (only used
        if color conversion occurs).
    base_indices -- If not None, it is a list of channel indices
        to compare (only these channels will be checked). If None,
        sequential indices are used.
    head_indices -- If not None, it is a list of channel indices
        to compare (only these channels will be checked). If None,
        sequential indices are used.
    max_count -- Only ever count this many channels, unless base_indices
        and head_indices are both set to a higher value, in which case,
        max_count does not do anything.

    Returns either the difference from -1.0 to 1.0
    enable_real_diff -- If True, 0.0 will only occur if all checked
        channels are exactly the same. If False, return 0.0 may occur
        if colors have the same brightness but a different color.

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
    return diff / float(len(base_indices)*c_max)


def diff_images(base, head, diff_size, diff=None,
                nochange_color=(0,0,0,255),
                enable_variance=True, c_max=255, max_count=4,
                base_indices=(0,1,2,3), head_indices=(0,1,2,3),
                clear_in_stats=False):
    """
    Compare two images, and return a dict with information.

    If diff is not None, it must also be an image, and it will be
    changed. Only parts will be changed where base and head differ.
    Grayscale will always be used the amount of difference.

    The base and head images are converted to true color using the PIL
    convert function (always 32-bit so that channel counts match) of
    the image object. If convert isn't called, the getpixel function
    gets a palette index for indexed images. The channel count must
    match for getpixel as well.

    Sequential arguments:
    base -- This is the first image for the difference operation.
        Provide either a PIL image or an implementation of
        ChannelTinkerInterface.
    head -- This is the second image for the difference operation.
        Provide either a PIL image or an implementation of
        ChannelTinkerInterface.
    diff_size -- For the purpose of not assuming assuming how to get the
        image size, you must provide the canvas size. You must set it
        to (max(base.width, head.width), max(base.height, head.height))
        The diff_size is used for the area to search for differences,
        so it is necessary even if diff is None and no diff will be
        generated.

    Keyword arguments:
    nochange_color -- If not using RGBA, set this to a tuple of the
        length of a color. Assume this is the background color
        (This is never drawn, but if set, then it will not be used for
        anything else unless this is gray).
    enable_variance -- set the actual absolute color difference
    c_max -- Pixels in the image can go up to this value.
    max_count -- only compare this number of channels.
    base_indices -- only compare these channels from head (length must
                    match either that of head_indices, or if that is
                    None, then match the head channel count.
    head_indices -- only compare these channels from head (length must
                    match either that of base_indices, or if that is
                    None, then match the base channel count.
    clear_in_stats -- Whether to use transparent pixels when calculating
        statistics such as diff_mean.
    """
    base = base.convert(mode='RGBA')
    head = head.convert(mode='RGBA')
    # Convert indexed images so getpixel doesn't return an index
    # (diff_color expects a tuple).
    results = {}
    results["same"] = None
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
        tmp_color = (0, type(c_max)(c_max/2), 0, c_max)  # dark green
        if tmp_color == nochange_color:
            tmp_color = (c_max, c_max, 0, 0, c_max)  # yellow
            add_color = convert_depth(tmp_color, pix_len, c_max=c_max)
        else:
            add_color = convert_depth(tmp_color, pix_len, c_max=c_max)
    if del_color == nochange_color:
        # choose an unused color (cast value to type of c_max)
        tmp_color = (type(c_max)(c_max/2), 0, 0, c_max)  # dark red
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
                    error("base.size: {}".format(base.size))
                    error("head.size: {}".format(head.size))
                    error("pos: {}".format(pos))
                    raise ex
                d = diff_color(base_color, head_color, c_max=c_max,
                               max_count=max_count)
                base_a = c_max
                head_a = c_max
                if pix_len > 3:
                    base_a = base_color[3]
                    head_a = head_color[3]
                if clear_in_stats:
                    if (base_a > 0) and (head_a>0):
                        total_diff += math.fabs(d)
                        total_count += 1
                    else:
                        total_diff += 1.0
                        total_count += 1
                else:
                    if (base_a > 0) and (head_a>0):
                        total_diff += math.fabs(d)
                        total_count += 1
                    elif (base_a > 0) or (head_a>0):
                        total_diff += 1.0
                        total_count += 1
                    # Else don't even count it toward total or weight.
                if d != 0.0:
                    # color = (c_max, c_max, c_max, c_max)
                    this_len = min(pix_len, 3)
                    color = [type(c_max)(c_max*d) for i in range(this_len)]
                    for i in range(pix_len - this_len):
                        color.append(c_max)
                    color = tuple(color)

            if color != nochange_color:
                results["same"] = False
                if diff is not None:
                    diff.putpixel(pos, color)
            else:
                if results["same"] is None:
                    results["same"] = True
    if total_count <= 0:
        results['error'] = "WARNING: There were no pixels."
    else:
        results['mean_diff'] = float(total_diff) / float(total_count)
    return results


msg_prefix = "[channel_tinker] "


def find_opaque_pos(cti, center, good_minimum=255, max_rad=None,
                    w=None, h=None):
    """
    Sequential arguments:
    cti -- Provide a PIL image or any implementation of
        ChannelTinkerInterface.
    center -- This location, or the closest location to it meeting
        criteria, is the search target.
    Keyword arguments:
    good_minimum -- (0 to 255) If the pixel's alpha is this or higher,
    get it (the closest in location to center).
    """
    circular = False
    # ^ True fails for some reason (try it in
    # draw_square to see the problem).
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
    for rad in range(0, max_rad + 1):
        # print("  rad: {}".format(rad))
        rad_f = float(rad) + epsilon + 1.0
        left = center[0] - rad
        right = center[0] + rad
        top = center[1] - rad
        bottom = center[1] + rad
        # For each side of the square, only use positions within the
        # circle:
        for pos in square_gen(center, rad):
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
            if (not circular) or (dist <= rad_f):
                # print("  navigating square {} ({} <="
                #       " {})".format(pos, dist, rad))
                pixel = cti.getpixel(pos)
                if pixel[3] >= good_minimum:
                    return pos
            else:
                # print("  navigating square {} SKIPPED ({} > "
                #       "{})".format(pos, dist, rad))
                pass
    return None


def draw_square_from_center(cti, center, rad, color=None, filled=False,
                            circular=False):
    """
    Sequential arguments:
    cti -- You must either provide a PIL image or implement
        ChannelTinkerInterface.
    """
    # Get any available pixel, to get p_len:
    p_len = len(cti.getbands())
    # pixel = cti.getpixel(0, 0)
    color = convert_depth(color, p_len)
    new_channels = p_len  # must match dest, else ExecutionError
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
    if filled:
        radii = []
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
        for rad in range(0, max_rad + 1):
            radii.append(rad)
    else:
        radii = [rad]
    diag = math.sqrt(2.0)
    # print("using diagonal pixel measurement: {}".format(diag))
    for rad in radii:
        rad_f = float(rad) + epsilon + diag*2
        for pos in square_gen(center, rad):
            dist = idist(center, pos)
            # print("  navigating square {} ({} <= {})".format(pos, dist,
            #                                                  rad))
            if (not circular) or (dist <= rad_f):
                x, y = pos
                if x < 0:
                    continue
                if y < 0:
                    continue
                if x >= w:
                    continue
                if y >= h:
                    continue
                cti.putpixel((x, y), color)


def draw_circle_from_center(cti, center, rad, color=None, filled=False):
    """
    Sequential arguments:
    cti -- You must either provide a PIL image or implement
        ChannelTinkerInterface.
    """
    return draw_square_from_center(cti, center, rad, color=color,
                                   filled=filled, circular=True)


def extend(cti, minimum=1, maximum=254,
           make_opaque=False, good_minimum=255, enable_threshold=False,
           threshold=128, ctpi=None):
    """
    Sequential arguments:
    cti -- You must either provide a PIL image or implement
        ChannelTinkerInterface.

    Keyword arguments:
    minimum -- (0 to 255) Only edit pixels with at least this for alpha.
    maximum -- (0 to 254) Only edit pixels with at most this for alpha.
    make_opaque -- Make the pixel within the range opaque. This is
        normally for preparing to convert images to indexed color, such as
        Minetest wield_image.
    ctpi -- To update a progress bar or similar progress feature,
        provide an implementation of ChannelTinkerProgressInterface.
    """
    if maximum < 0:
        maximum = 0
    if minimum < 0:
        minimum = 0
    if maximum > 254:
        maximum = 254
    w, h = cti.size

    # print("Size: {}".format((w, h)))
    total_f = float(w * h)
    count_f = 0.0
    # ok = True
    n_pix = None
    msg = None
    for y in range(h):
        # if not ok:
        #     break
        for x in range(w):
            used_th = False
            # if count_f is None:
            count_f = float(y) * float(w) + float(x)
            # print("checking {}".format(cti.getpixel((x, y))))
            p_len = len(cti.getbands())
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
                        if msg is None:  # only show 1 messagebox
                            msg = ("Uh oh, got own pos when checking"
                                   " for better color than"
                                   " {}...".format(pixel))
                            error(msg)
                            if cpti is not None:
                                ctpi.show_message(msg)
                                cpti.set_status(msg)
                                cpti.progress_update(0.0)
                            # ok = False
                    else:
                        n_pix = cti.getpixel(opaque_pos)
                        p_len = len(cti.getbands())
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
                            # return
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
                        return
            if enable_threshold and not used_th:
                if pixel[3] > threshold:
                    n_pix = (pixel[0], pixel[1], pixel[2], 255)
                else:
                    n_pix = (pixel[0], pixel[1], pixel[2], 0)
                cti.putpixel((x, y), n_pix)
            if count_f is not None:
                # count_f += 1.0
                if ctpi is not None:
                    ctpi.progress_update(count_f / total_f)
