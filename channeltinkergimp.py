#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Channel-level and pixel-level features for GIMP.
- Remove Halo:
  For each pixel where the alpha is below the threshold, get a new color
  using the nearest opaque pixel.
"""
from __future__ import print_function
from __future__ import division
import gettext
import sys
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GLib
from gi.repository import GObject
gi.require_version('Gegl', '0.4')  # See https://github.com/GNOME/gimp/blob/095727b0746262bc1cf30e1f1994f81288280edc/plug-ins/python/foggify.py#L22C1-L23C1
from gi.repository import Gegl

# print("channeltinkergimp: Loading channeltinker...")

from channeltinker import (
    ChannelTinkerInterface,
    ChannelTinkerProgressInterface,
    draw_circle_from_center,
    emit_cast,
    extend,
    draw_square_from_center,
)

print("channeltinkergimp: Registering features...")

# See <https://gitlab.com/-/snippets/2227657/raw/main/ex1.py>
# Set-up localization for your plug-in with your own text domain.
# This is complementary to the gimp_plug_in_set_translation_domain()
# which is only useful for the menu entries inside GIMP interface,
# whereas the below calls are used for localization within the plug-in.
textdomain = 'gimp30-std-plug-ins'
gettext.bindtextdomain(textdomain, Gimp.locale_directory())
# gettext.bind_textdomain_codeset(textdomain, 'UTF-8') # not in gettext using GIMP 3.0 RC2
print("gettext version: {}".format(gettext.__doc__))
gettext.textdomain(textdomain)
_ = gettext.gettext
def N_(message): return message

class GimpCTPI(ChannelTinkerProgressInterface):
    def __init__(self):
        # self.progress = Gimp.Progress.new()
        pass

    def progress_update(self, factor):
        Gimp.progress_update(factor)

    def set_status(self, text):
        Gimp.progress_set_text(text)
        # Show

    def show_message(self, text):
        Gimp.message(text)


class GimpCTI(ChannelTinkerInterface):

    @property
    def size(self):
        return self._size

    def __init__(self, image, drawable=None):
        self.image = image
        if drawable is None:
            drawable = image.get_active_drawable()
        self.drawable = drawable
        # Image has no attribute width in GIMP 3.0 (Gegl-based)
        w = self.drawable.get_width()
        h = self.drawable.get_height()
        self._size = (w, h)
        self._bands = None
        self._p_len = None  # For caching, not exposed

    def getbands(self):
        """Generates _p_len, so probably not necessary anymore"""
        if self._bands is not None:
            return self._bands
        pos = (0, 0)
        color = self.drawable.get_pixel(pos[0], pos[1])
        # ^ returns Color object, formerly tuple of p_len, pixel
        # Handle bands and pixel length logic
        # raise NotImplementedError("dir(color): {}".format(dir(color)))
        # ^ get_data, get_bytes, replace_data, get_rgba, get_rgba_with_space etc. and set methods.
        # r, g, b, a = color.get_rgba_with_space(Babl.format("R'G'B'A double"))
        format = color.get_format()  # Babl.Object has no public members
        # raise NotImplementedError("format: {}".format(emit_cast(format)))
        # if p_len == 1:
        #     self._bands = ('L',)  # Luma
        # else:
        #     self._bands = tuple("RGBA??????????"[:p_len])
        # self._p_len = len(self._bands)
        return self._bands

    def getPixelType(self):
        return type(self.getpixel((0, 0))[0])

    def getpixel(self, pos):
        color = self.drawable.get_pixel(pos[0], pos[1])
        r, g, b, a = color.get_rgba()
        return (r, g, b, a)

    def putpixel(self, pos, rgba):
        # if self._p_len is None:
        #     self._p_len = len(self.getbands())  # Generates _p_len
        if isinstance(rgba[0], int):
            # hex_singles_str = (
            #     "#"
            #     + format(rgba[0] // 16, 'x')
            #     + format(rgba[1] // 16, 'x')
            #     + format(rgba[2] // 16, 'x')
            #     + format(rgba[3] // 16, 'x')
            # )
            hex_pairs_str = (
                "#"
                + format(rgba[0], '02x')
                + format(rgba[1], '02x')
                + format(rgba[2], '02x')
                + format(rgba[3], '02x')
            )
            color = Gegl.Color.new(hex_pairs_str)
        else:
            color = Gegl.Color.new("#FFFF")
            color.set_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        self.drawable.set_pixel(pos[0], pos[1], color)
        # color = self.drawable.get_pixel(pos[0], pos[1])
        # if len(color) == 4:
        #     color.set_rgba(color[0], color[1], color[2], color[3])
        # elif len(color) == 3:
        #     color.set_rgba(color[0], color[1], color[2], 255)
        # elif len(color) == 1:
        #     color.set_rgba(color[0], color[0], color[0], 255)
        # self.drawable.set_pixel(pos[0], pos[1], color)

# Gegl.init(None)

class ChannelTinker(Gimp.PlugIn):
    __gtype_name__ = "ChannelTinker"
    # See https://github.com/UserUnknownFactor/GIMP3-ML/blob/f53dee1f92052b57de78b03ba3ffd0ad5ff4309c/gimpml/plugins/filterfolder/filterfolder.py#L206
    @GObject.Property(type=Gimp.RunMode,
                      default=Gimp.RunMode.NONINTERACTIVE,
                      nick="Run mode", blurb="The run mode")
    def run_mode(self):
        """Read-write integer property."""
        return self.runmode

    @run_mode.setter
    def run_mode(self, runmode):
        self.runmode = runmode

    def do_set_i18n(self, procname):
        return False, 'gimp30-python', None


    def do_query_procedures(self):
        # See https://gitlab.com/-/snippets/2227657/raw/main/ex1.py
        # Localization for the menu entries. It has to be called in the
        # query function only.
        # self.set_translation_domain(textdomain, Gio.file_new_for_path(Gimp.locale_directory()))
        # ^ Does not exist

        return [
            'channeltinker-remove-halo',
            'channeltinker-centered-square',
            'channeltinker-centered-circle',
        ]

    # def do_register(self):
    #     """Register both plugins in GIMP."""
    #     self.register_remove_halo()
    #     self.register_centered_square()
    #     self.register_centered_circle()

    def do_create_procedure(self, name):
        # procedure = Gimp.ImageProcedure.new(
        #     self,
        #     "channeltinker-DEBUG",
        #     Gimp.PDBProcType.PLUGIN,
        #     self.run,
        #     None,
        # )
        Gegl.init(None)
        self.black = Gegl.Color.new("black")
        self.black.set_rgba(0, 0, 0, 1)

        # raise NotImplementedError(dir(procedure))
        if name == "channeltinker-remove-halo":
            return self.register_remove_halo(name)
        if name == "channeltinker-centered-square":
            return self.register_centered_square(name)
        if name == "channeltinker-centered-circle":
            return self.register_centered_circle(name)
        raise NameError("channeltinkergimp: Unknown feature {}".format(name))

    def register_remove_halo(self, name):
        """Registers 'Remove Halo' in GIMP."""
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None,
        )
        procedure.set_image_types("*")  # "*" for all, or "RGB*, GRAY*" for limited
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
        procedure.set_menu_label("Remove Halo")
        procedure.set_documentation(
            "Remove alpha transparency halos",
            "For each pixel where the alpha is below the threshold, "
            "get a new color using the nearest opaque pixel.",
            "Jake Gustafson"
        )
        procedure.set_attribution("Jake Gustafson", "Jake Gustafson", "2020")
        procedure.add_menu_path("<Image>/Colors/Channel Tinker")

        # Arguments (replacing PF_* types)
        # apparently args are (name, caption [can have underscore for hotkey], tip, min, max, default, flags)
        procedure.add_int_argument("minimum", "Minimum alpha to fix (normally 1)", "Minimum alpha to fix (normally 1)", 0, 254, 1, GObject.ParamFlags.READWRITE)
        procedure.add_int_argument("maximum", "Maximum to discard (254 unless less damaged)", "Maximum to discard (254 unless less damaged)", 1, 254, 254, GObject.ParamFlags.READWRITE)
        procedure.add_int_argument("good_minimum", "Get nearby >= this (usually max discard +1)", "Get nearby >= this (usually max discard +1)", 1, 255, 255, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("make_opaque", "Make the fixed parts opaque", "Make the fixed parts opaque", False, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("enable_threshold", "Apply the threshold below to the image", "Apply the threshold below to the image", False, GObject.ParamFlags.READWRITE)
        procedure.add_int_argument("threshold", "Minimum alpha to set to 255", "Minimum alpha to set to 255", 0, 254, 128, GObject.ParamFlags.READWRITE)

        return procedure

    def register_centered_square(self, name):
        """Registers 'Draw Centered Square' in GIMP."""
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None,
        )
        procedure.set_image_types("*")  # "*" for all, or "RGB*, GRAY*" for limited
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
        procedure.set_menu_label("Draw Centered Square")
        procedure.set_documentation(
            "Draw a centered square on the selected layer.",
            "Draws a square centered in the image with a specified radius, color, "
            "and optional fill.",
            "Jake Gustafson"
        )
        procedure.set_attribution("Jake Gustafson", "Jake Gustafson", "2020")
        procedure.add_menu_path("<Image>/Colors/Channel Tinker")

        procedure.add_int_argument("radius", "Radius", "Radius", 0, 9999, 15, GObject.ParamFlags.READWRITE)
        procedure.add_color_argument("color", "Color", "Color", True, self.black, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("filled", "Filled", "Filled", False, GObject.ParamFlags.READWRITE)

        return procedure

    def register_centered_circle(self, name):
        """Registers 'Draw Centered Circle' in GIMP."""
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None,
        )
        procedure.set_image_types("*")  # "*" for all, or "RGB*, GRAY*" for limited
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
        procedure.set_menu_label("Draw Centered Circle")
        procedure.set_documentation(
            "Draw a centered circle on the selected layer.",
            "Draws a circle centered in the image with a specified radius, color, "
            "and optional fill.",
            "Jake Gustafson"
        )
        procedure.set_attribution("Jake Gustafson", "Jake Gustafson", "2020")
        procedure.add_menu_path("<Image>/Colors/Channel Tinker")

        procedure.add_int_argument("radius", "Radius", "Radius", 0, 9999, 15, GObject.ParamFlags.READWRITE)
        procedure.add_color_argument("color", "Color", "Color", True, self.black, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("filled", "Filled", "Filled", False, GObject.ParamFlags.READWRITE)

        return procedure

    # def run(self, procedure, run_mode, image, drawable, config, data):
    # def run(self, procedure, run_mode, config):
    # def run(self, procedure, run_mode, image, layer, config, data): # See https://github.com/isabella232/gimp-plugins/blob/28e6d3c80b145c56d572aabc7c7bca026fbdda80/3.0/blobi.py#L93 or https://github.com/intel/openvino-ai-plugins-gimp/blob/3d28a256c43798c0aac6ca164e60f1af5d1fc853/gimpopenvino/plugins/stable_diffusion_ov/stable_diffusion_ov.py#L304
    def run(self, procedure, run_mode, image, drawables, config, run_data):  # See https://gitlab.gnome.org/GNOME/gimp/-/blame/master/extensions/goat-exercises/goat-exercise-py3.py#L57
        # n_drawables: See https://gitlab.com/-/snippets/2227657/raw/main/ex1.py
        """Run the correct function based on procedure name."""
        if len(drawables) != 1:
            msg = _("Procedure '{}' only works with one drawable.").format(
                procedure.get_name())
            error = GLib.Error.new_literal(Gimp.PlugIn.error_quark(), msg, 0)
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, error)
        else:
            drawable = drawables[0]

        if run_mode == Gimp.RunMode.INTERACTIVE:
            # See https://github.com/GNOME/gimp/blob/095727b0746262bc1cf30e1f1994f81288280edc/plug-ins/python/foggify.py#L33
            GimpUi.init(procedure.get_name())
            dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
            dialog.fill(None)
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
            else:
                dialog.destroy()
        if procedure.get_name() == "channeltinker-remove-halo":
            self.ct_remove_layer_halo(
                image, drawable,
                config.get_property('minimum'),
                config.get_property('maximum'),
                config.get_property('good_minimum'),
                config.get_property('make_opaque'),
                config.get_property('enable_threshold'),
                config.get_property('threshold'),
            )
        elif procedure.get_name() == "channeltinker-centered-square":
            self.ct_draw_centered_square(
                image, drawable,
                config.get_property('radius'),
                config.get_property('color'),
                config.get_property('filled'),
            )
        elif procedure.get_name() == "channeltinker-centered-circle":
            self.ct_draw_centered_circle(
                image, drawable,
                config.get_property('radius'),
                config.get_property('color'),
                config.get_property('filled'),
            )
        Gimp.context_pop()
        # return procedure, Gimp.PDBStatusType.SUCCESS, []
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
        # return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

    def ct_remove_layer_halo(self, image, drawable, minimum, maximum,
                             good_minimum, make_opaque, enable_threshold,
                             threshold):
        """Removes halos from an image by modifying transparent pixels."""
        image.undo_group_start()
        Gimp.context_push()
        Gimp.progress_init("This may take a while...")

        # Create instances of the required helper classes
        cti = GimpCTI(image, drawable=drawable)
        ctpi = GimpCTPI()

        # Apply the halo removal algorithm
        results = extend(
            cti, minimum=minimum, maximum=maximum, make_opaque=make_opaque,
            good_minimum=good_minimum, enable_threshold=enable_threshold,
            threshold=threshold, ctpi=ctpi,
        )
        error = results.get('error')
        if error:
            Gimp.message(error)

        # Update the drawable after modification
        drawable.update(0, 0, drawable.get_width(), drawable.get_height())
        Gimp.displays_flush()

        Gimp.context_pop()
        image.undo_group_end()

    def ct_draw_centered_square(self, image, drawable, radius, color, filled):
        """Draws a centered square on the drawable layer using GIMP 3 API."""

        image.undo_group_start()
        Gimp.context_push()
        Gimp.progress_set_text("Drawing centered square...")
        Gimp.progress_update(0.0)

        w, h = drawable.get_width(), drawable.get_height()
        x, y = w // 2, h // 2  # Center of image

        expand_right = False  # TODO: implement this
        expand_down = False  # TODO: implement this
        post_msg = ""

        if w % 2 == 0:
            expand_right = True
            post_msg = "horizontally"
        if h % 2 == 0:
            expand_down = True
            if post_msg:
                post_msg += " or "
            post_msg += "vertically"

        if post_msg:
            msg = ("The image has an even number of pixels, so the current"
                   " drawing function cannot draw exactly centered "
                   "{}.".format(post_msg))
            Gimp.message(msg)
        # Create selection (x, y, width, height, feather, antialias)
        # NOTE: drawable has get_selection and is_selection
        # CHANNEL_OP_REPLACE = 0  # formerly imported from gimpfu
        # image.select_rectangle(CHANNEL_OP_REPLACE, x - radius, y - radius, radius * 2, radius * 2)

        Gimp.progress_update(0.5)
        # if filled:
        #     drawable.fill(Gimp.FillType.FOREGROUND)
        # else:
        #     drawable.stroke_selection()

        # image.get_selection().none()  # Deselect selection
        # print("image.channels: {}".format())  # doesn't exist anymore
        # print("image.base_type: {}".format())
        cti = GimpCTI(image, drawable=drawable)
        draw_square_from_center(cti, (x, y), radius, color=color,
                                filled=filled)

        Gimp.displays_flush()

        Gimp.progress_update(1.0)
        Gimp.context_pop()
        image.undo_group_end()

    def ct_draw_centered_circle(self, image, drawable, radius, color, filled):
        """Draw a centered circle on the given drawable."""

        image.undo_group_start()
        Gimp.context_push()
        # Image has no attribute width in GIMP 3.0 (Gegl-based)
        w = drawable.get_width()
        h = drawable.get_height()
        x = w // 2
        y = h // 2

        expand_right = False  # TODO: implement this
        expand_down = False  # TODO: implement this
        post_msg = ""

        if w % 2 == 0:
            expand_right = True
            post_msg = "horizontally"
        if h % 2 == 0:
            expand_down = True
            if post_msg:
                post_msg += " or "
            post_msg += "vertically"

        if post_msg:
            msg = ("The image has an even number of pixels, so the current"
                   " drawing function cannot draw exactly centered "
                   f"{post_msg}.")
            Gimp.message(msg)

        # exists, x1, y1, x2, y2 = drawable.get_selection_bounds()  # Uncomment if needed
        cti = GimpCTI(image, drawable=drawable)
        draw_circle_from_center(cti, (x, y), radius, color=color, filled=filled)

        drawable.update(0, 0, drawable.get_width(), drawable.get_height())
        Gimp.displays_flush()

        Gimp.context_pop()
        image.undo_group_end()


Gimp.main(ChannelTinker.__gtype__, sys.argv)
