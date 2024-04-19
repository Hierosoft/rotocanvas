#!/usr/bin/env python
from __future__ import print_function
import sys
import traceback
import copy

verbose_enable = False


def get_dict_deepcopy(old_dict):
    '''Get a deepcopy if the param is a dict.
    The purpose of this is to make an "even deeper" deepcopy. I don't
    recall why this might be necessary. However, it can also convert
    a non-dict dict-like object to a dict.

    This is from parsing.py in github.com/poikilos/pycodetool, but
    modified for Python 2 compatibility.

    Returns:
        dict: A copy, or if not dict then return None (degrade
            silently!)
    '''
    new_dict = None
    if isinstance(old_dict, dict):
        new_dict = {}
        for this_key in old_dict.keys():
            new_dict[this_key] = copy.deepcopy(old_dict[this_key])
    return new_dict


def view_traceback():
    ex_type, ex, tb = sys.exc_info()
    print("{}: {}:".format(ex_type, ex))
    traceback.print_tb(tb)
    del tb
    print("")


def get_by_name(object_list, needle):  # formerly find_by_name
    result = None
    for i in range(0, len(object_list)):
        try:
            if object_list[i].name == needle:
                result = object_list[i]
                break
        except AttributeError as ex:
            print("Could not finish get_by_name:" + str(ex))
            view_traceback()
    return result


def get_index_by_name(object_list, needle):
    result = -1
    for i in range(0, len(object_list)):
        try:
            if object_list[i].name == needle:
                result = i
                break
        except AttributeError as ex:
            print("Could not finish get_by_name:" + str(ex))
            view_traceback()
    return result
