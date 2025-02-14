#!/usr/bin/env python
from __future__ import print_function
import copy
# import decimal
# import math
import json
import os
import shutil
import puremagic
import sys

# from decimal import Decimal
import locale as lc
from logging import getLogger

if sys.version_info.major >= 3:
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import (
        askopenfilename,
        asksaveasfilename,
    )
    import tkinter.messagebox as messagebox
else:  # Python 2
    import Tkinter as tk  # type: ignore
    import ttk  # type: ignore
    from tkFileDialog import (  # type: ignore
        askopenfilename,
        asksaveasfilename,
    )
    import tkMessageBox as messagebox

ENABLE_PIL = False
try:
    import PIL
    from PIL import ImageTk, Image
    ENABLE_PIL = True
except ImportError:
    pass

ENABLE_AV = False
try:
    import av
    ENABLE_AV = True
    from rotocanvas import rc_av
except ImportError:
    rc_av = None

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.dirname(MODULE_DIR)

if __name__ == "__main__":
    sys.path.insert(0, REPO_DIR)

from rotocanvas import (
    sysdirs,
    make_real,
)

from rotocanvas.morelogging import formatted_ex
from rotocanvas.rcproject import RCProject  # noqa: E402
from rotocanvas.moremimetypes import (
    # dot_ext_mimetype,
    path_mimetype,
)

DEFAULT_SETTINGS = {
    'recent_paths': [],
}

logger = getLogger(__name__)


class DataField(tk.StringVar):
    def __init__(self, *args):
        tk.StringVar.__init__(self, *args)
        self.widget = None
        self.label = None
        self.unit_label = None
        self.cast_fn = None
        self.caption = None


class NewFileFrame(ttk.Frame):
    """New File Dialog

    Args:
        parent (ttk.Widget): _description_
        setting_types (OrderedDict): Fields to request.
        callback (Callable[dict]): Function to receive fields:
            - 'cancel' (bool, optional): True if cancelled.
            - 'error' (str, optional): Not None if failed.
            - 'width' (int): User-specified width.
            - 'height' (int): User-specified width.
            - 'unit' (str): Reserved (normally "px")
    """
    def __init__(self, parent, setting_types, callback, **kwargs):
        self.setting_types = setting_types
        self.localeResult = lc.setlocale(lc.LC_ALL, "")
        ttk.Frame.__init__(self, parent, **kwargs)
        self.title = "Create"
        if self.localeResult == "C":
            lc.setlocale(lc.LC_ALL, "en_US")
        # example: moneyStr = lc.currency(amount, grouping=True)
        self.parent = parent
        self.root = self.parent
        if hasattr(self.parent, 'root'):
            self.root = self.parent.root

        self.callback = callback
        # region must exist before _gui runs
        self.fields = {}
        self.label_c = 0
        self.field_c = 1
        self.field_colspan = 2
        self.unit_c = 3
        # endregion must exist before _gui runs
        self._gui(self)

    def get(self, key):
        # field = self.fields.get(key)
        field = self.fields[key]
        return field.get()

    def get_dict(self):
        results = {}
        for key, field in self.fields.items():
            value = field.get()
            error = None
            setting_type = self.setting_types[key]
            if not value or not value.strip():
                raise ValueError("{} must not be blank."
                                 .format(field.caption))
            try:
                value = setting_type['cast_fn'](value)
            except ValueError:
                if field.setting_type['cast_fn'] is int:
                    error = "{} must be a number.".format(field.caption)
            minimum = setting_type.get('min')
            maximum = setting_type.get('max')
            min_msg = minimum if (minimum is not None) else "any"
            max_msg = maximum if (maximum is not None) else "any"
            range_msg = "{} must be from {} to {}".format(
                field.caption, min_msg, max_msg)
            if maximum is not None:
                if value > maximum:
                    raise ValueError(range_msg)
            if minimum is not None:
                if value < minimum:
                    raise ValueError(range_msg)
            if error:
                raise ValueError(error)
            results[key] = value
        return results

    def _add_field(self, key, caption=None, unit=None, cast_fn=str):
        if caption is None:
            caption = key
        if not key:
            raise KeyError("blank key={}".format(repr(key)))
        row = len(self.fields)
        field = DataField(self.root)
        field.caption = caption
        if not cast_fn:
            cast_fn = str
        field.cast_fn = cast_fn
        field.label = ttk.Label(self.container, text=caption)
        field.label.grid(column=self.label_c, row=row)
        field.widget = ttk.Entry(self.container, textvariable=field)
        field.widget.grid(
            column=self.field_c,
            row=row,
            columnspan=self.field_colspan,
        )
        if unit is not None:
            field.unit_label = ttk.Label(self.container, text=unit)
            field.unit_label.grid(column=self.unit_c, row=row)
        self.fields[key] = field

    def _gui(self, container):
        self.container = container
        if self.fields:
            raise RuntimeError("NewFileFrame already initialized.")
        self.fields = {}
        for key, field in self.setting_types.items():
            self._add_field(key, caption=field.get('caption'),
                            unit=field.get('unit'),
                            cast_fn=field.get('cast_fn'))
        row = len(self.fields)
        self._ok_button = ttk.Button(self.container, text="Create", command=self.ok_clicked)
        self._ok_button.grid(column=1, row=row)
        self._cancel_button = ttk.Button(self.container, text="Cancel", command=self.cancel_clicked)
        self._cancel_button.grid(column=2, row=row)

    def ok_clicked(self):
        if not self.callback:
            raise ValueError("callback was not set.")
        results = {}
        try:
            results = self.get_dict()
        except ValueError as ex:
            messagebox.showerror("Error", str(ex))
            results['error'] = str(ex)
        self.callback(results)

    def cancel_clicked(self):
        if not self.callback:
            raise ValueError("callback was not set.")
        results = {}
        results['cancel'] = True
        self.callback(results)

if __name__ == "__main__":
    print("Oops, you ran the {} module.".format(os.path.split(__file__)[1]))