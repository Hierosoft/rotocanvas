#!/usr/bin/env python
"""
For each pixel where the alpha is below the threshold, get a new color
using the nearest opaque pixel.
"""
from __future__ import print_function
# import math
# import sys
# from itertools import chain
# import time

from gimpfu import *  # by convention, import *
from channeltinker import (
    # convert_depth,
    # echo1,
    # idist,
    # find_opaque_pos,
    ChannelTinkerInterface,
    ChannelTinkerProgressInterface,
    draw_circle_from_center,
    extend,
    draw_square_from_center,
)


class GimpCTPI(ChannelTinkerProgressInterface):
    def progress_update(self, factor):
        gimp.progress_update(factor)

    def set_status(self, msg):
        gimp.progress_init(msg)

    def show_message(self, msg):
        pdb.gimp_message(msg)


class GimpCTI(ChannelTinkerInterface):

    @property
    def size(self):
        return self._size

    def __init__(self, image, drawable=None):
        self.image = image
        if drawable is None:
            drawable = pdb.gimp_image_active_drawable(image)
        self.drawable = drawable
        w = pdb.gimp_image_width(self.image)
        h = pdb.gimp_image_height(self.image)
        self._size = (w, h)
        self._bands = None
        self._p_len = None # for caching--not exposed

    def getbands(self):
        if self._bands is not None:
            return self._bands
        pos = (0, 0)
        p_len, pixel = pdb.gimp_drawable_get_pixel(self.drawable,
                                                   pos[0], pos[1])
        # TODO: return something more accurate if necessary.
        if p_len == 1:
            # See <https://stackoverflow.com/questions/52962969/
            # number-of-channels-in-pil-pillow-image>
            self._bands = tuple('L')  # Luma
            # TODO: handle 'P' (See <https://www.geeksforgeeks.org/
            #     pyhton-pil-getbands-method/>) [sic]
        else:
            self._bands = tuple("RGBA??????????"[:p_len])
        self._p_len = len(self._bands)
        return self._bands

    def getpixel(self, pos):
        p_len, pixel = pdb.gimp_drawable_get_pixel(self.drawable,
                                                   pos[0], pos[1])
        return pixel

    def putpixel(self, pos, color):
        if self._p_len is None:
            count = len(self.getbands())  # generates _p_len
        pdb.gimp_drawable_set_pixel(self.drawable, pos[0], pos[1],
                                    self._p_len, color)


def ct_draw_centered_circle(image, drawable, radius, color, filled):
    image.disable_undo()
    w = pdb.gimp_image_width(image)
    h = pdb.gimp_image_height(image)
    x = None
    y = None

    if w % 2 == 1:
        x = float(w) / 2.0
    else:
        x = w / 2
    if h % 2 == 1:
        y = float(h) / 2.0
    else:
        y = h / 2
    expand_right = False  # TODO: implement this
    expand_down = False  # TODO: implement this
    post_msg = ""
    if (w % 2 == 0):
        expand_right = True
        post_msg = "horizontally"
    if (h % 2 == 0):
        expand_down = True
        if len(post_msg) > 0:
            post_msg += " or "
        post_msg += "vertically"

    if len(post_msg) > 0:
        msg = ("The image is an even number of pixels, so the current"
               " drawing function cannot draw exactly centered"
               " " + post_msg + ".")
        pdb.gimp_message(msg)
    # exists, x1, y1, x2, y2 = \
    #     pdb.gimp_selection_bounds(self.image)
    cti = GimpCTI(image, drawable=drawable)
    draw_circle_from_center(cti, (x, y), radius,
                            color=color, filled=filled)
    pdb.gimp_drawable_update(drawable, 0, 0, drawable.width,
                             drawable.height)
    pdb.gimp_displays_flush()
    image.enable_undo()


def ct_draw_centered_square(image, drawable, radius, color, filled):
    image.disable_undo()
    w = pdb.gimp_image_width(image)
    h = pdb.gimp_image_height(image)
    x = w // 2
    y = h // 2
    expand_right = False  # TODO: implement this
    expand_down = False  # TODO: implement this
    post_msg = ""
    if (w % 2 == 0):
        expand_right = True
        post_msg = "horizontally"
    if (h % 2 == 0):
        expand_down = True
        if len(post_msg) > 0:
            post_msg += " or "
        post_msg += "vertically"

    if len(post_msg) > 0:
        msg = ("The image is an even number of pixels, so the current"
               " drawing function cannot draw exactly centered"
               " " + post_msg + ".")
        pdb.gimp_message(msg)

    print("image.channels: {}".format(image.channels))
    print("image.base_type: {}".format(image.channels))
    cti = GimpCTI(image, drawable=drawable)
    draw_square_from_center(cti, (x, y), radius, color=color,
                            filled=filled)
    pdb.gimp_drawable_update(drawable, 0, 0, drawable.width,
                             drawable.height)
    pdb.gimp_displays_flush()
    image.enable_undo()


def ct_remove_layer_halo(image, drawable, minimum, maximum, good_minimum,
                         make_opaque, enable_threshold, threshold):
    image.disable_undo()
    gimp.progress_init("This may take a while...")
    # print("options: {}".format((str(image), str(drawable), str(minimum),
    #                            str(maximum), str(make_opaque),
    #                            str(good_minimum))))
    cti = GimpCTI(image, drawable=drawable)
    ctpi = GimpCTPI()
    extend(cti, minimum=minimum,
           maximum=maximum, make_opaque=make_opaque,
           good_minimum=good_minimum, enable_threshold=enable_threshold,
           threshold=threshold, ctpi=ctpi)
    # if image is None:
    #     image = gimp.image_list()[0]
    # if drawable is None:
    #     drawable = pdb.gimp_image_active_drawable(image)

    pdb.gimp_drawable_update(drawable, 0, 0, drawable.width,
                             drawable.height)
    pdb.gimp_displays_flush()
    # ^ update the image; still you must first do#
    # pdb.gimp_drawable_update(...)
    image.enable_undo()


max_tip = "Maximum to discard (254 unless less damaged)"
goot_min_tip = "get nearby >= this (usually max discard+1)."
m_o_tip = "Make the fixed parts opaque."
a_t_tip = "Apply the threshold below to the image."
t_tip = "Minimum alpha to set to 255"
# See "Python-fu sites" under "Developer Notes" in README.md
register(
    "python_fu_ct_remove_halo",
    "Remove Halo",  # short description
    "Remove alpha",  # long description
    "Jake Gustafson", "Jake Gustafson", "2020",
    "Remove Halo",  # menu item caption
    "RGBA",  # RGB* would mean with or without alpha.
    [
        (PF_IMAGE, "image", "Current image", None),
        (PF_DRAWABLE, "drawable", "Input layer", None),
        (PF_SPINNER, "minimum", "Minimum alpha to fix (normally 1)", 1,
         (0, 255, 1)),
        (PF_SPINNER, "maximum", max_tip, 254, (0, 255, 1)),
        (PF_SPINNER, "good_minimum", goot_min_tip, 255, (0, 255, 1)),
        (PF_TOGGLE, "make_opaque", m_o_tip, False),
        (PF_TOGGLE, "enable_threshold", a_t_tip, False),
        (PF_SPINNER, "threshold", t_tip, 128, (0, 255, 1))
    ],
    [],  # results
    ct_remove_layer_halo,
    menu="<Image>/Colors/Channel Tinker"
)

# register(
#     "python_fu_ct_centered_circle",
#     "Draw Centered Circle",
#     "Draw centered circle",
#     "Jake Gustafson", "Jake Gustafson", "2020",
#     "Draw Centered Circle",  # caption
#     "RGB*",  # RGB* would mean with or without alpha.
#     [
#         (PF_IMAGE, "image", "Current image", None),
#         (PF_DRAWABLE, "drawable", "Input layer", None),
#         (PF_INT,    "radius", "Radius", 15),
#         (PF_COLOR,  "color", "Color", (0, 0, 0)),
#         (PF_TOGGLE, "filled", "Filled", False),
#     ],
#     [], # results
#     ct_draw_centered_circle,
#     menu="<Image>/Colors/Channel Tinker"
# )

register(
    "python_fu_ct_centered_square",
    "Draw Centered Square",
    "Draw centered square",
    "Jake Gustafson", "Jake Gustafson", "2020",
    "Draw Centered Square",  # caption
    "RGB*",  # RGB* would mean with or without alpha.
    [
        (PF_IMAGE, "image", "Current image", None),
        (PF_DRAWABLE, "drawable", "Input layer", None),
        (PF_INT,    "radius", "Radius", 15),
        (PF_COLOR,  "color", "Color", (0, 0, 0)),
        (PF_TOGGLE, "filled", "Filled", False),
    ],
    [], # results
    ct_draw_centered_square,
    menu="<Image>/Colors/Channel Tinker"
)

main()
