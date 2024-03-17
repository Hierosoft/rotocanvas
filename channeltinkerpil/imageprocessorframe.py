#!/usr/bin/env python3
# ImageProcessorX
# (c) 2021 Poikilos
# license: See license file.
'''
This processes a list of images. The list is basically a "playlist" for
images. The last column in the space-separated columns is considered as
the filename. If that is not a file, more columns to the left will be
appended until a file is found, otherwise the line is skipped.

Filenames can optionally be relative to the current working directory or
the list file.
'''

# import inspect
import os
import sys
import platform
# import math
import subprocess
import shlex
from pprint import pformat

print("executable: %s" % pformat(sys.executable))
print("os.path.realpath(executable): %s"
      % pformat(os.path.realpath(sys.executable)))
import site  # noqa E402
print("site-packages: %s" % pformat(site.getsitepackages()))

venv_error_fmt = ("Import failed though %s exists, so the virtual"
                  " environment appears to be broken. Recreate it"
                  " after installing tkinter. A symlink won't work.")
tkdephelp = "sudo apt-get install python3-tk"
dephelp = "sudo apt-get install python3-pil python3-pil.imagetk"
if sys.version_info.major >= 3:
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        for sitepackages in site.getsitepackages():
            try_sub = os.path.join(sitepackages, "tkinter")
            if os.path.isdir(try_sub):
                print(venv_error_fmt % try_sub,
                      file=sys.stderr)
            elif os.path.exists(try_sub):
                print("Error: %s exists but is not a directory"
                      "" % pformat(try_sub),
                      file=sys.stderr)
            else:
                print("Error: %s is not present" % pformat(try_sub),
                      file=sys.stderr)
        raise
else:  # Python 2
    import Tkinter as tk
    import ttk
    tkdephelp = "sudo apt-get install python-tk"
    dephelp = "sudo apt-get install python-imaging python-pil.imagetk"


try:
    import PIL
    from PIL import Image
except ModuleNotFoundError as ex:
    print("{}".format(ex))
    print()
    print("You must install ImageTk such as via:")
    print(dephelp)
    print()
    sys.exit(1)

try:
    from PIL import ImageTk
    # ^ Place this at the end (to avoid any conflicts/errors)
except ImportError as ex:
    print("{}".format(ex))
    print()
    print("You must install ImageTk such as via:")
    print(dephelp)
    print()
    sys.exit(1)

# from decimal import Decimal
# import decimal
# import locale as lc

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.dirname(MODULE_DIR)
if os.path.isdir(os.path.join(os.path.dirname(REPO_DIR), "rotocanvas")):
    # parent of rotocanvas is rotocanvas not sitepackages,
    # so allow using the nearby module even if not installed.
    sys.path.insert(0, REPO_DIR)

REPOS_DIR = os.path.dirname(REPO_DIR)
OTHER_REPO_DIR = os.path.join(REPOS_DIR, "EnlivenMinetest")


from rotocanvas import (  # noqa E402
    echo0,
    echo1,
    echo2,
    set_verbosity,
)

HOME = None
if platform.system == "Windows":
    HOME = os.environ['USERPROFILE']
else:
    HOME = os.environ['HOME']

HOME_BIN = os.path.join(HOME, ".local", "bin")

session = {}
playerIndex = 0

checkDotTypes = [
    ".png",
    ".jpg",
    ".bmp",
]

goodFlagRel = os.path.join("share", "pixmaps", "imageprocessorx.png")

myPath = os.path.split(os.path.abspath(__file__))[0]

prefix = os.environ.get("PREFIX")
if prefix is None:
    prefix = "."
if os.path.isfile(os.path.join(myPath, goodFlagRel)):
    # If running without installing, use the directory containing the
    # icon as the prefix.
    prefix = myPath

share = os.path.join(prefix, "share")
pixmaps = os.path.join(share, "pixmaps")


class MainFrame(ttk.Frame):
    ISSUE_DIR = 'Specify a main directory (not detected).'
    ISSUE_LIST = 'Specify a list or image file.'

    def __init__(self, parent):
        self.generated = False  # use generated metas only, not listPath
        # ^ Use mainSV.get() to get the directory for saving any output
        #   in this case.
        self.parent = parent  # tk root
        self.timedMsg = None
        self.prevMsg = None
        self.checkedSuffix = ".checked"
        self.pimages = None
        self.listPath = None
        self.metas = []
        self.nameSV = tk.StringVar()
        self.pathSV = tk.StringVar()
        self.mainSV = tk.StringVar()
        self.listSV = tk.StringVar()
        self.statusSV = tk.StringVar()
        self.markBV = tk.BooleanVar()

        # local dynamically-generated callback function:
        def on_marked_changed(tkVarID, param, event, var=self.markBV,
                              key='checked'):
            '''Keyword argument defaults force early binding
            (they come from the outer scope, not the call).
            '''
            # See also: anewcommit/anewcommit/gui_tkinter.py
            if self.metaI < 0:
                echo0("Error: self.metaI={} (can't set '{}')"
                      "".format(self.metaI, key))
            meta = self.metas[self.metaI]
            meta[key] = var.get()

        if sys.version_info.major >= 3:
            self.markBV.trace_add('write', on_marked_changed)
        else:
            self.markBV.trace('wu', on_marked_changed)
        ttk.Frame.__init__(self, parent)
        self.style = ttk.Style(parent)
        # print("{}".format(self.style.theme_names()))
        # ^ ('clam', 'alt', 'default', 'classic')
        self.style.theme_use('alt')
        # ^ Theme Checkbutton styles (check graphic):
        # 'classic', 'default': shading only
        # 'clam': x
        self.pack(fill=tk.BOTH, expand=True)
        self.menuBar = tk.Menu(parent)
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Save Filename List (Checked)",
                                  command=self.saveChecked)
        self.fileMenu.add_command(label="Open in Default Application",
                                  command=self.openInDefaultApplication)
        self.fileMenu.add_command(label="Open in Editor",
                                  command=self.openWith)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=quit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)
        parent.config(menu=self.menuBar)

        self.issues = [
            MainFrame.ISSUE_DIR,
            MainFrame.ISSUE_LIST,
        ]
        # self.columnconfigure(tuple(range(2)), weight=1)
        self.columnconfigure(1, weight=1)  # Make col 1 (2nd col) expand
        # Make col 1 (2nd col) expand: affects grid items with tk.W+tk.E
        # self.rowconfigure(tuple(range(10)), weight=1)
        # ^ rowconfigure with weight makes buttons stay spaced evenly
        row = 0
        # wide_width = 30
        statusLbl = ttk.Label(self, textvariable=self.statusSV)
        statusLbl.grid(column=0, row=row, sticky=tk.W+tk.E, columnspan=2)
        self.setStatus("Specify a main directory. Specify a file list.")
        row += 1
        mainLbl = ttk.Label(self, text="Main Directory:")
        mainLbl.grid(column=0, row=row, sticky=tk.E)
        mainEntry = ttk.Entry(self, width=25, textvariable=self.mainSV,
                              state="readonly")
        mainEntry.grid(column=1, columnspan=3, row=row, sticky=tk.W+tk.E)
        row += 1
        ttk.Label(self, text="List:").grid(column=0, row=row, sticky=tk.E)
        listEntry = ttk.Entry(self, width=25, textvariable=self.listSV,
                              state="readonly")
        listEntry.grid(column=1, columnspan=3, row=row, sticky=tk.W+tk.E)
        row += 1
        ttk.Label(self, text="Name:").grid(column=0, row=row, sticky=tk.E)
        nameEntry = ttk.Entry(self, width=25, textvariable=self.nameSV,
                              state="readonly")
        nameEntry.grid(column=1, columnspan=3, row=row, sticky=tk.W+tk.E)
        row += 1
        ttk.Label(self, text="Path:").grid(column=0, row=row, sticky=tk.E)
        self.pathEntry = ttk.Entry(self, width=25, textvariable=self.pathSV)
        self.pathEntry.grid(column=1, columnspan=3, row=row, sticky=tk.W+tk.E)
        row += 1
        self.prevBtn = ttk.Button(self, text="Previous", command=self.prevFile)
        self.prevBtn.grid(column=0, row=row, sticky=tk.E)
        self.nextBtn = ttk.Button(self, text="Next", command=self.nextFile)
        self.nextBtn.grid(column=2, row=row, sticky=tk.W)
        # row += 1
        self.markBtn = ttk.Checkbutton(self, onvalue=True, offvalue=False,
                                       variable=self.markBV)
        self.markBtn.grid(column=1, row=row)
        # exitBtn = ttk.Button(self, text="Exit", command=root.destroy)
        # exitBtn.grid(column=2, row=row, sticky=tk.W)
        row += 1
        self.image_row = row  # required by setImageCount
        #   (for grid_forget and re-adding to same place)
        self.imageLabels = None
        self.imageErrorVars = []
        # ^ self.imageErrorVars is expanded in setImageCount using count.
        self.setImageCount(1)
        for child in self.winfo_children():
            child.grid_configure(padx=6, pady=3)
        self.nextBtn['state'] = tk.DISABLED
        self.prevBtn['state'] = tk.DISABLED
        self.markBtn['state'] = tk.DISABLED
        # self.nameSV.set(money(session.getCurrentMoney(playerIndex)))

    def setImageCount(self, count):
        """Generate labels for the desired image count.

        Args:
            count (int): The number of image columns to show.
        """
        # if sys.version_info.major >= 3:
        #     caller_name = inspect.stack()[1].function
        # else:
        #     caller_name = inspect.stack()[1][3]
        # print("setImageCount({}) via {}".format(count, caller_name))
        if self.imageLabels:
            for label in self.imageLabels:
                label.grid_forget()
        self.imageLabels = []
        columnspan = 3 if count == 1 else 1
        # ^ Span all 3 columns if there is only one image.
        row = self.image_row
        for i in range(count):
            while i >= len(self.imageErrorVars):
                self.imageErrorVars.append(tk.StringVar())
            column = i if count != 1 else 0
            # ^ Use column 0 if there is only one image.
            label = ttk.Label(self, textvariable=self.imageErrorVars[i])
            # , text="..."
            label.grid(
                column=column,
                row=row,
                columnspan=columnspan,
            )
            self.imageLabels.append(label)

    def setStatus(self, msg):
        self.statusSV.set(msg)

    def timedMessage(self, msg, delay=2000):
        '''Show a message temporarily,
        then revert to the previous message
        unless the message changed.

        Args:
            delay (Optional[int]): Disappear after this many
                milliseconds.
        '''
        self.prevMsg = self.statusSV.get()
        self.timedMsg = msg
        self.statusSV.set(msg)
        self.parent.after(delay, self.revertTimedMessage)

    def revertTimedMessage(self):
        '''Only revert the message if the message is known.
        If the timed message was interrupted, leave the new message as
        is.
        '''
        if self.statusSV.get() == self.timedMsg:
            self.statusSV.set(self.prevMsg)

    def saveChecked(self):
        '''Save self.listPath with self.checkedSuffix
        added to the filename.
        '''
        if self.listPath is None:
            self.statusSV.set("Error: There is no filename")
            return
        if len(self.metas) < 1:
            self.statusSV.set("Error: There is no list loaded.")
            return
        parts = os.path.splitext(self.listPath)
        destPath = parts[0] + self.checkedSuffix + parts[1]
        destName = os.path.split(destPath)[1]
        self.timedMessage("Saved {}".format(destName))
        with open(destPath, 'w') as outs:
            for meta in self.metas:
                keep = meta.get('checked')
                name = meta.get('name')
                if name is None:
                    # Keep comments etc. (any line that isn't a file).
                    keep = True
                if not keep:
                    continue
                outs.write("{}\n".format(meta['line']))

    def setPath(self, path):
        echo1('* set path to "{}"'.format(path))
        self.removeIssue(MainFrame.ISSUE_DIR)
        self.mainSV.set(path)

    def removeIssue(self, msg):
        if msg in self.issues:
            self.issues.remove(msg)
        # print("self.issues: {}".format(self.issues))
        statusStr = ""
        space = ""
        for issueStr in self.issues:
            statusStr += space + issueStr
            space = " "
        self.statusSV.set(statusStr)

    def setList(self, path):
        self.removeIssue(MainFrame.ISSUE_LIST)
        self.listSV.set(path)

    def getBasePath(self):
        result = "."
        tmp = self.mainSV.get().strip()
        if len(tmp) > 0:
            result = tmp
        return result

    """
    def getFullPath(self, rel):
        '''
        Get a list item's absolute path using the base path (or ".").
        '''
        return os.path.join(self.getBasePath(), rel)

    """

    def getFullPath(self, relative_path):
        '''Get the absolute path based on the location of the list,
        otherwise return relative_path.
        '''
        # formerly getAbs
        # getBasePath gets the path containing the list file (or the
        #   directory which was used if the list was generated)
        path = relative_path
        list_path = self.getListPath()
        list_dir = os.path.dirname(list_path)
        try_path = os.path.join(list_dir, relative_path)
        if os.path.exists(try_path):
            path = os.path.realpath(try_path)  # remove ./ or other
        return path

    def loadList(self, path):
        self.listPath = path
        if len(self.mainSV.get().strip()) == "":
            self.setPath(os.path.dirname())
            echo0('* set base path to directory of list: "{}"'
                  ''.format(self.getBasePath()))
        else:
            echo1('* using base path "{}"'.format(self.getBasePath()))
        self.metas = []
        self.metaI = 0
        found = 0
        index = -1
        with open(path, 'r') as ins:
            for rawL in ins:
                index += 1  # Starts at -1, so +1 for 0
                isFound = False
                raw2 = rawL.rstrip()
                line = raw2.strip()
                if not line:
                    continue
                indent = ""
                if len(line) < len(raw2):
                    indent = raw2[len(raw2)-len(line):]
                parts = line.split(" ")
                cols = 1
                name = line[-1]
                while cols <= len(parts):
                    lastParts = parts[-cols:]
                    tryName = " ".join(lastParts)
                    # print("tryName: \"{}\"".format(tryName))
                    tryPath = self.getFullPath(tryName)
                    if os.path.isfile(tryPath):
                        self.metas.append({
                            'name': tryName,
                            'line': rawL.rstrip(),
                            'prefix': indent + " ".join(parts[:-cols])
                        })
                        found += 1
                        isFound = True
                        break
                    cols += 1
                if not isFound:
                    self.metas.append({
                        'line': rawL.rstrip(),
                    })
        # print("metas: {}".format(self.metas))

    def onFormLoaded(self):
        path = self.getListPath()
        if (len(path) < 1):
            self.generateList(os.getcwd())
        elif os.path.isdir(path):
            # self.listSV.set("")  # It isn't a listfile but a folder.
            # echo0("* generateList for \"{}\"...".format(path))
            # self.setPath(path)
            # ^ So relative paths don't use the current working
            #   directory as set by the previous call to setPath
            self.generateList(path)
        else:
            try:
                self.loadList(path)
            except UnicodeDecodeError as ex:
                echo0("* loading the list failed: {}".format(ex))
                echo0("  - generating a list instead...")
                self.generateList(path)  # auto-detects a file
        if len(self.metas) > 0:
            self.showCurrentImage()
            self.prevBtn['state'] = tk.DISABLED
            if len(self.metas) > 1:
                self.nextBtn['state'] = tk.NORMAL

    def generateList(self, path, indent=""):
        found = 0
        path = os.path.realpath(path)
        isFound = False
        self.metas = []
        self.metaI = 0
        self.generated = True
        if os.path.isdir(path):
            self.listSV.set("")  # It isn't a listfile but a folder.
            self.setPath(path)
            for sub in os.listdir(path):
                subPath = os.path.join(path, sub)
                if sub.startswith("."):
                    continue
                self.metas.append({
                    'name': subPath,
                    'line': None,
                    'prefix': indent,
                })
                found += 1
                isFound = True
            if isFound:
                # echo1("* set path: \"{}\"".format(path))
                self.setPath(path)
        elif os.path.isfile(path):
            self.listSV.set("")
            # ^ It isn't a listfile but a folder containing the
            #   specified image file.
            parent = os.path.dirname(path)
            self.generateList(parent)  # does call setPath if folder
            self.gotoPath(path)
            parent = os.path.dirname(path)
            return
        if found > 0:
            self.removeIssue(MainFrame.ISSUE_DIR)

    def gotoPath(self, path):
        for i in range(len(self.metas)):
            meta = self.metas[i]
            if meta.get('name') == path:
                self.metaI = i
                break

    def prevFile(self):
        self.metaI -= 1
        if self.metaI < 0:
            self.metaI = len(self.metas) - 1
        self.showCurrentImage()
        self.updateButtonStates()

    def _showImages(self):
        '''Show each image in self.pimages (or blank col for each None).

        This should be called only by loadImage, unless you set each
        self.imageErrorVars item correctly ("" if image, otherwise error
        message and the corresponding self.pimages item should be None
        in that and only that case)
        '''
        if len(self.pimages) != len(self.imageLabels):
            self.setImageCount(len(self.pimages))
        for index, pimage in enumerate(self.pimages):
            if pimage is None:
                self.imageLabels[index].configure(image='')
                # ^ Clear is '' not None in tk.
                continue
            self.imageLabels[index].configure(image=self.pimages[index])

    def loadImage(self, path):
        '''Show image(s) on the panel.

        Args:
            path (Union[str,list[str],tuple[str]]): Show an image or
                list of images. If not str, it is assumed to be an
                iterable.
        '''
        # See Apostolos' Apr 14 '18 at 16:20 answer edited Oct 26 '18 at
        # 8:40 on <https://stackoverflow.com/a/49833564>
        prefix = "loadImage"
        paths = [path] if isinstance(path, str) else path
        del path
        # count = len(paths)
        # if len(paths) != len(self.imageLabels):
        #     self.setImageCount(len(paths))
        index = -1
        self.pimages = []
        err = None
        for path in paths:
            _, name = os.path.split(path)
            index += 1
            echo1('loadImage "{}"'.format(path))
            try:
                echo1('- working directory: "{}"'.format(os.getcwd()))
                if not os.path.isfile(path):
                    raise FileNotFoundError(path)
                self.pimages.append(
                    ImageTk.PhotoImage(Image.open(path))
                )
                self.imageErrorVars[index].set("")
                # self.imageLabels[index].configure(image=self.pimages[index])
                # ^ Keep as attribute so it doesn't go out of scope
                #   (which would destroy the image).
                self.statusSV.set("")
                self.markBtn['state'] = tk.NORMAL
                echo1('- loaded.')
            except PIL.UnidentifiedImageError:
                # self.imageLabels[index].configure(image='')
                self.imageErrorVars[index].set("unreadable")
                err = "Error: unreadable image"
                self.statusSV.set(err)
                # return False, err
            except Exception as ex:
                err = 'Unhandled {}: "{}"'.format(type(ex).__name__, ex)
                self.imageErrorVars[index].set("failed")
                self.statusSV.set(err)
                # return False, err

            while index >= len(self.pimages):
                self.pimages.append(None)
                echo0(prefix+"Increased len(self.pimages) to {} since index is {}"
                      "".format(len(self.pimages), index))
            if len(paths) > 1:
                if index == 1:
                    # In case paths are (base, head, diff) or (base,
                    #   head) (by way of rotocanvas diffimage
                    #   convention, head should 2nd which is [1]), show
                    #   head (a WIP version of file) in case that
                    #   differs.
                    self.nameSV.set(os.path.split(path)[1])
                    self.pathSV.set(path)
                # else do not show base or diff path
                #   (normally diff is generated and not an actual file)
            else:
                self.nameSV.set(os.path.split(path)[1])
                self.pathSV.set(path)
            # self.imageLabels[index] = tk.Label(window, image=self.pimages[0]).pack()
        self._showImages()
        return err is None, err

    def hideImages(self):
        if self.imageLabels:
            for label in self.imageLabels:
                label.configure(image=None)

    def previewFolder(self, path):
        self.statusSV.set("(folder)")
        self.hideImages()
        self.markBtn['state'] = tk.NORMAL
        self.nameSV.set(os.path.split(path)[1])
        self.pathSV.set(path)

    def getListPath(self):
        return self.listSV.get().strip()

    def openInDefaultApplication(self):
        """Open the selected file in the default application.
        """
        # See https://stackoverflow.com/a/435669
        path = self.getCurrentFullPath()
        # import subprocess, os, platform
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(path)
        else:                                   # GNU/Linux-like
            subprocess.call(('xdg-open', path))

    def openWith(self, exe=None):
        if exe is None:
            exe = "gimp"
        path = self.getCurrentFullPath()
        if exe == "gimp":
            try_gimp = os.path.join(HOME_BIN, "gimp-flatpak.sh")
            if os.path.isfile(try_gimp):
                exe = try_gimp
        cmd_parts = (exe, path)
        echo0("Running: " + shlex.join(cmd_parts))
        subprocess.call(cmd_parts)

    def getCurrentFullPath(self):
        meta = self.metas[self.metaI]
        echo2("self.metaI={}".format(self.metaI))
        name = meta.get('name')
        status_msg = name
        path = name
        echo1("getCurrentFullPath...")
        if name is None:
            echo1('* no name: using bare line as path: "{}"'.format(path))
            path = meta.get('line')
            status_msg = meta.get('line')
        # self.setStatus(status_msg)
        try_path = self.getFullPath(path)  # formerly getAbs
        # ok = True
        # err = None
        if os.path.exists(try_path):
            path = try_path
        return path

    def showCurrentImage(self):
        '''Show whatever image is the current one in the loaded/generated list
        using loadImage, or if the item is a subdirectory, call
        previewFolder.

        Always let loadImage handle paths, so that all path fault
        tolerance code is in one place.
        '''
        err = None
        path = self.getCurrentFullPath()
        status_msg = path
        meta = self.metas[self.metaI]
        name = meta.get('name')
        if name is not None:
            echo1('* name="{}"'.format(name))
            status_msg = "..."
            if os.path.isdir(path):
                self.previewFolder(path)
                status_msg = 'loaded folder "{}"'.format(path)
            else:
                ok, err = self.loadImage(path)
                status_msg = path
        else:
            ok, err = self.loadImage(path)
            self.nameSV.set("")
            self.pathSV.set("")
            self.hideImages()
            self.markBV.set(False)
        echo2("meta['checked']={}".format(meta.get('checked')))

        if meta.get('checked') is True:
            self.markBV.set(True)
        else:
            self.markBV.set(False)

        if err is not None:
            status_msg = err + ": {}".format(path)
        self.statusSV.set(status_msg)

    def hasNext(self):
        if self.metas is None:
            return False
        if self.metaI < 0:
            return False
        return self.metaI + 1 < len(self.metas)

    def hasPrev(self):
        if self.metas is None:
            return False
        if self.metaI < 0:
            return False
        return self.metaI > 0

    def updateButtonStates(self):
        if self.hasNext():
            self.nextBtn['state'] = tk.NORMAL
        else:
            self.nextBtn['state'] = tk.DISABLED
        if self.hasPrev():
            self.prevBtn['state'] = tk.NORMAL
        else:
            self.prevBtn['state'] = tk.DISABLED

    def nextFile(self):
        self.metaI += 1
        if self.metaI >= len(self.metas):
            self.metaI = 0
        self.showCurrentImage()
        self.updateButtonStates()

    def markFile(self, mark):
        echo2("marked")
        self.markBV.set(mark)
        if mark:
            self.metas[self.metaI]['checked'] = True

    def end(self):
        self.nextBtn['state'] = tk.DISABLED
        self.prevBtn['state'] = tk.DISABLED
        self.markBtn['state'] = tk.NORMAL

    def onKeyPress(self, event):
        if event.keysym == 'Right':
            if str(self.nextBtn['state']) == tk.NORMAL:
                self.nextFile()
        elif event.keysym == 'Left':
            if str(self.prevBtn['state']) == tk.NORMAL:
                self.prevFile()
        elif event.keysym == 'Down':
            if str(self.markBtn['state']) == tk.NORMAL:
                self.markFile(True)
        elif event.keysym == 'Up':
            if str(self.markBtn['state']) == tk.NORMAL:
                self.markFile(False)
        else:
            print("{}".format(event))
            # ^ such as:
            '''
            <KeyPress event keysym=Right keycode=114 x=-1160 y=322>
            <KeyPress event keysym=Left keycode=113 x=-1160 y=322>
            <KeyPress event keysym=minus keycode=20 char='-' x=-1160 y=322>
            <KeyPress event keysym=equal keycode=21 char='=' x=-1160 y=322>
            <KeyPress event keysym=Shift_L keycode=50 x=-1160 y=322>
            <KeyPress event state=Shift keysym=underscore
             keycode=20 char='_' x=-1160 y=322>
            <KeyPress event state=Shift keysym=plus keycode=21 char='+'
             x=-1160 y=322>
            <KeyPress event keysym=1 keycode=10 char='1' x=-1160 y=322>
            <KeyPress event keysym=space keycode=65 char=' ' x=-1160 y=322>
            <KeyPress event keysym=Return keycode=36 char='\r' x=-1160 y=322>
            '''


def main():
    global session
    session = {}

    global root
    root = tk.Tk()
    root.title("ImageProcessorX")
    # iconPath = os.path.join(pixmaps, "imageprocessorx.xbm")
    '''
    ^ XBM is the required type for iconbitmap's default param on linux
    supposedly
    (<https://stackoverflow.com/questions/29973246/using-tkinter-
    command-iconbitmap-to-set-window-icon>)
    but doesn't work (see error in comment below).
    '''
    iconPath = os.path.join(pixmaps, "imageprocessorx.png")
    if platform.system() == "Windows":
        iconPath = os.path.join(pixmaps, "imageprocessorx.ico")
    mainframe = MainFrame(root)
    if os.path.isfile(iconPath):
        # root.iconbitmap(default=iconPath)
        # ^ "root.MyIcon = Tk.PhotoImage(file='/usr/share/icons/gnome/
        #   32x32/apps/zen-icon.png')"
        # See <https://forums.raspberrypi.com/viewtopic.php?t=254725>
        root.MyIcon = tk.PhotoImage(file=iconPath)
        root.iconphoto(True, root.MyIcon)
    root.bind('<KeyPress>', mainframe.onKeyPress)
    prevArg = None
    mainDirPath = None
    listPath = None
    code = 0
    for arg in sys.argv:
        if prevArg is None:
            prevArg = arg  # the command that ran this script
            continue
        if arg.startswith("--"):
            if arg == "--verbose":
                set_verbosity(1)
            elif arg == "--debug":
                set_verbosity(2)
            else:
                echo0("Error: {} is not a valid option.".format(arg))
                code = 1
        elif listPath is None:
            listPath = arg

        elif mainDirPath is None:
            mainDirPath = arg
        prevArg = arg
    dev_list_paths = [
        os.path.join(OTHER_REPO_DIR, "check-patches-lmk-2024-02-29.txt"),
        # ^ add diffimage feature and use to verify patches were applied
        #   (output of EnlivenMinetest/utilities/check-patches-lmk)
        "/opt/minebest/assemble/bucket_game/image_list.txt",
        # ^ test existing features and new list panel.
    ]
    if not listPath:
        for dev_list_path in dev_list_paths:
            if os.path.isfile(dev_list_path):
                listPath = dev_list_path
                mainDirPath = os.path.dirname(listPath)
                break
    if listPath:
        mainframe.setList(listPath)
    if mainDirPath:
        mainframe.setPath(mainDirPath)
    print("listPath={}".format(listPath))
    print("mainDirPath={}".format(mainDirPath))
    root.after(1, mainframe.onFormLoaded)  # (milliseconds, function)
    root.mainloop()
    '''
    session.stop()
    if session.save():
        print("Save completed.")
    else:
        print("Save failed.")
    '''
    return code


if __name__ == "__main__":
    sys.exit(main())
