#!/usr/bin/env python
"""
The window is based on <https://python-textbok.readthedocs.io/en/latest
/Introduction_to_GUI_Programming.html>.
You must add a variable called DFL_PATH to your system to use this
program (the value must be the path to the directory containing
_internal--_internal will be added automatically when necessary so
don't include that part).
"""
from __future__ import print_function
import sys
import os
if sys.version_info.major >= 3:
    import tkinter as tk
    from tkinter import ttk
else:  # Python 2
    import Tkinter as tk
    import ttk

if sys.version_info.major < 3:
    ModuleNotFoundError = ImportError

enableDLM = False

# try:
from rotocanvas.dfl import DLMItem
from rotocanvas.dfl import DLM
enableDLM = True
'''
except ModuleNotFoundError:
    MODULE_DIRS = ["C:\\Users\\Owner\\GitHub\\rotocanvas\\rotocanvas"]
    for modules in MODULE_DIRS:
        if os.path.isdir(modules):
            sys.path.append(modules)
            break
    if modules is None:
        print("You do not have rotocanvas in the path nor in any of"
              " the following known locations: {}".format(MODULE_DIRS))
    else:
        print("[choose_dfl_dst] * using {} for modules."
              "".format(modules))
        from dfl import DLMItem
        from dfl import DLM
        enableDLM = True
'''


class GridButton(tk.Button):
    def __init__(self, parent, row, column, *args, **kwargs):
        ttk.Button.__init__(self, parent, *args, **kwargs)
        # ^ From question <https://stackoverflow.com/questions/46625259/
        #   tkinter-subclassing-button-with-additional-arguments)
        self.row = row
        self.column = column
        pass


class DFLGUI:
    def __init__(self, master, dflPath):
        self.master = master
        self.master.geometry("500x500")
        self.storageItems = {}
        self.labItems = {}
        self.meta = {}
        self.topRows = 0
        self.cols = {}
        self.dlm = None
        self.greeting = "DLM is enabled."
        # try:
        if enableDLM:
            self.dlm = DLM(dflPath)
        errors = self.dlm.popErrors()
        if len(errors) > 0:
            self.dlm = None
            self.greeting = " ".join(errors)
        # except NameError:
        # ^ hides too many errors
        else:
             self.greeting = "Close & add rotocanvas to your path."
        ZONE_STORAGE = 'storage'
        ZONE_LAB = 'lab'
        if self.dlm is not None:
            ZONE_STORAGE = DLM.ZONE_STORAGE
            ZONE_LAB = DLM.ZONE_LAB
        self.whichs = [ZONE_STORAGE, ZONE_LAB]
        for i in range(len(self.whichs)):
            self.cols[self.whichs[i]] = i
        self.meta[ZONE_STORAGE] = self.storageItems
        self.meta[ZONE_LAB] = self.labItems
        master.title("DLM GUI")
        self.label = tk.Label(master, text=self.greeting)
        # self.label.pack()
        self.label.grid()
        self.topRows = 1

        self.rows = [self.topRows, self.topRows]
        if self.dlm is not None:
            zone = DLM.ZONE_LAB
            role = DLM.ROLE_DST
            self.forceAddBtn("B1", zone, role)
            self.forceAddBtn("B2", zone, role)
            zone = DLM.ZONE_STORAGE
            self.forceAddBtn("A1", zone, role)
            self.forceAddBtn("A2", zone, role)
            self.forceAddBtn("A2", zone, role)

            # self.close_button = tk.Button(master, text="Close",
            # command=master.quit)
            # self.close_button.pack()

    def addPath(self, path, role=None):
        """
        Args:
            role (str): You must set role unless the item
        """
        if self.dlm is None:
            return None
        name = os.path.split(path)[1]
        row = self.rows[column]
        params = {}
        params["dlm"] = self.dlm
        params["command"] = "open"
        params["role"] = role
        params["path"] = path
        item = GridButton(self.master, row, column, text=name,
                          command=lambda: self.open(params))
        zone = DLM.ZONE_STORAGE
        if item.isInLab():
            zone = DLM.ZONE_LAB
        self.removeBtn(path, zone)
        self.meta[zone][path] = item
        item.column = column
        item.row = row
        # item.pack(side=tk.LEFT)
        item.grid(column=column, row=item.row)
        self.rows[column] += 1
        print("isInLab to lab: {}".format(item.isInLab()))
        return item

    def getRoles(self):
        if self.dlm is not None:
            return DLM.getRoles()
        return ['src', 'dst']

    def open(self, params):
        """Add the role's items to the lab.
        """
        path = params.get("path")
        role = params.get("role")
        print("role: {}".format(role))
        if path is None:
            raise ValueError("You must specify a path.")
        if role is None:
            raise ValueError("You must specify a role.")
        roles = self.getRoles()
        if role not in roles:
            raise ValueError("{} is not a role (must be {})"
                             "".format(role, roles))
        print("Use {}: {}".format(role, path))
        item = params.get('item')
        zone = params.get('zone')

        if item is not None:
            print("item.path: {}".format(item.path))
            if self.dlm is not None:
                pass
                # TODO: call workspace (needs new function to move
                # an item to another workspace)
                # self.dlm.choose_param(role, path)
        else:
            print("item: {}".format(item))
        self.removeBtn(path, zone)

    def getZones(self):
        if self.dlm is not None:
            return DLM.getZones()
        return ['storage', 'lab']

    def _buttonAt(self, row, column):
        for k, v in self.meta[self.whichs[column]].items():
            if v.column != column:
                continue
            if v.row == row:
                return v

    def removeBtn(self, path, zone):
        if zone not in self.getZones():
            raise ValueError("{} is not a zone (should be any of: {}]"
                             "".format(zone, self.getZones()))
        item = self.meta[zone].get(path)
        if item is not None:
            # print("* removing old button for \"{}\"".format(path))
            # item.pack_forget()
            item.grid_remove()
            column = item.column
            if item.row + 1 < self.rows[column]:
                print("In column {}".format(column))
                for r in range(item.row + 1, self.rows[column]):
                    nextRcf = self._buttonAt(r, column)
                    if nextRcf is None:
                        # print("  there is no row {}".format(r))
                        continue
                    newRow = r - 1
                    # print("  moving {} to {}".format(r, newRow))
                    nextRcf.grid_forget()
                    nextRcf.grid(row=newRow, column=column)
                    nextRcf.row = newRow
            self.rows[column] -= 1
            del self.meta[zone][path]

    def close(self, path):
        """Remove the role's items from the lab.
        """
        print("Closing \"{}\"...".format(path))
        raise NotImplementedError("close is not implemented")

    def forceAddBtn(self, path, zone, role):
        """Add the button without workspace sanity checks.
        """
        if zone not in self.getZones():
            raise ValueError("{} is not a zone (should be any of: {}]"
                             "".format(zone, self.getZones()))
        column = self.cols[zone]

        self.removeBtn(path, zone)
        name = os.path.split(path)[1]
        row = self.rows[column]
        params = {}
        params["dlm"] = self.dlm
        params["role"] = role
        params["zone"] = zone
        params["path"] = path
        if self.dlm is not None:
            if self.dlm.isInLab(path):
                params["command"] = "close"
                item = GridButton(self.master, row, column, text=name,
                                  command=lambda: self.close(params))
            else:
                params["command"] = "open"
                item = GridButton(self.master, row, column, text=name,
                                  command=lambda: self.open(params))
        else:
            item = GridButton(self.master, row, column,
                              command=lambda: self.open(params))
        self.meta[zone][path] = item
        item.column = column
        item.row = row
        # item.pack(side=tk.LEFT)
        item.grid(column=column, row=item.row)
        self.rows[column] += 1
        return item


if __name__ == "__main__":
    dflPath = None
    dflPath = os.environ.get("DFL_PATH")
    if dflPath is not None:
        intl = os.path.join(dflPath, "_internal")

        print("You set DFL_PATH to \"{}\"".format(dflPath))
        if not os.path.isdir(dflPath):
            print("...but it doesn't exist.")
        elif not os.path.isdir(intl):
            print("...but it doesn't contain _internal")
    if len(sys.argv) > 1:
        dflPath = sys.argv[1]
    if dflPath is None:
        print("WARNING: You must specify a path to use DLM.")
    root = tk.Tk()
    gui = DFLGUI(root, dflPath)
    root.mainloop()
