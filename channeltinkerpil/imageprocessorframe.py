#!/usr/bin/env python3
# ImageProcessorX
# (c) 2021 Poikilos
# license: See license file.
'''
This processes a list of images. The list is basically a "playlist" for
images. The last column in the space-separated columns is considered as
the filename. If that is not a file, more columns to the left will be
appended until a file is found, otherwise the line is skipped.

If the filenames are relative, the current working directory must be the
base path in which the relative paths can be used.
'''

import os
import sys
import platform
import math

try:
    import Tkinter as tk
    import ttk
    # Python 2
    dephelp = "sudo apt-get install python-imaging python-pil.imagetk"
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk
    from tkinter import ttk

# region same as anewcommit

dephelp = "sudo apt-get install python3-pil python3-pil.imagetk"

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
    from PIL import ImageTk  # Place this at the end (to avoid any conflicts/errors)
except ImportError as ex:
    print("{}".format(ex))
    print()
    print("You must install ImageTk such as via:")
    print(dephelp)
    print()
    sys.exit(1)
# endregion same as anewcommit

from decimal import Decimal
import decimal
import locale as lc

from rotocanvas import (
    echo0,
    echo1,
    echo2,
)

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
        self.img = None
        self.listPath = None
        self.metas = []
        self.nameSV = tk.StringVar()
        self.pathSV = tk.StringVar()
        self.mainSV = tk.StringVar()
        self.listSV = tk.StringVar()
        self.statusSV = tk.StringVar()
        self.markSV = tk.BooleanVar()
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
        wide_width = 30
        ttk.Label(self, textvariable=self.statusSV).grid(column=0, row=row, sticky=tk.W+tk.E, columnspan=2)
        self.statusSV.set("Specify a main directory. Specify a file list.")
        row += 1
        ttk.Label(self, text="Main Directory:").grid(column=0, row=row, sticky=tk.E)
        ttk.Entry(self, width=25, textvariable=self.mainSV, state="readonly").grid(column=1, columnspan=3, row=row, sticky=tk.W+tk.E)
        row += 1
        ttk.Label(self, text="List:").grid(column=0, row=row, sticky=tk.E)
        ttk.Entry(self, width=25, textvariable=self.listSV, state="readonly").grid(column=1, columnspan=3, row=row, sticky=tk.W+tk.E)
        row += 1
        ttk.Label(self, text="Name:").grid(column=0, row=row, sticky=tk.E)
        ttk.Entry(self, width=25, textvariable=self.nameSV, state="readonly").grid(column=1, columnspan=3, row=row, sticky=tk.W+tk.E)
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
        self.markBtn = ttk.Checkbutton(self, onvalue=True, offvalue=False, variable=self.markSV)
        self.markBtn.grid(column=1, row=row)
        # ttk.Button(self, text="Exit", command=root.destroy).grid(column=2, row=row, sticky=tk.W)
        row += 1
        self.imgLabel = ttk.Label(self)  # , text="..."
        self.imgLabel.grid(column=0, row=row, columnspan=3)
        for child in self.winfo_children():
            child.grid_configure(padx=6, pady=3)
        self.nextBtn['state'] = tk.DISABLED
        self.prevBtn['state'] = tk.DISABLED
        self.markBtn['state'] = tk.DISABLED
        # self.nameSV.set(money(session.getCurrentMoney(playerIndex)))

    def timedMessage(self, msg, delay=2000):
        '''
        Show a message temporarily, then revert to the previous message
        unless the message changed.
        Keyword arguments:
        delay -- Disappear after this many milliseconds.
        '''
        self.prevMsg = self.statusSV.get()
        self.timedMsg = msg
        self.statusSV.set(msg)
        self.parent.after(delay, self.revertTimedMessage)

    def revertTimedMessage(self):
        '''
        Only revert the message if the message is known. If the timed
        message was interrupted, leave the new message as is.
        '''
        if self.statusSV.get() == self.timedMsg:
            self.statusSV.set(self.prevMsg)

    def saveChecked(self):
        '''
        Save self.listPath with self.checkedSuffix added to the
        filename.
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

    def getFullPath(self, rel):
        return os.path.join(self.getBasePath(), rel)

    def loadList(self, path):
        self.listPath = path
        self.metas = []
        self.metaI = 0
        found = 0
        with open(path, 'r') as ins:
            for rawL in ins:
                isFound = False
                raw2 = rawL.rstrip()
                line = raw2.strip()
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
        path = self.listSV.get().strip()
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
                self.generateList(path)  # auto-detects a file
        if len(self.metas) > 0:
            self.showCurrentImage()
            self.prevBtn['state'] = tk.DISABLED
            if len(self.metas) > 1:
                self.nextBtn['state'] = tk.NORMAL

    def generateList(self, path, indent = ""):
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

    def showImage(self, path):
        '''
        See Apostolos' Apr 14 '18 at 16:20 answer edited Oct 26 '18 at
        8:40 on <https://stackoverflow.com/a/49833564>
        '''
        try:
            self.img = ImageTk.PhotoImage(Image.open(path))
            self.statusSV.set("")
            self.imgLabel.configure(image=self.img)
            self.markBtn['state'] = tk.NORMAL
        except PIL.UnidentifiedImageError:
            self.imgLabel.configure(image='')
            self.statusSV.set("Error: unreadable image")
        self.nameSV.set(os.path.split(path)[1])
        self.pathSV.set(path)
        # self.imgLabel = tk.Label(window, image=self.img).pack()

    def previewFolder(self, path):
        self.statusSV.set("(folder)")
        self.imgLabel.configure(image=None)
        self.markBtn['state'] = tk.NORMAL
        self.nameSV.set(os.path.split(path)[1])
        self.pathSV.set(path)


    def showCurrentImage(self):
        meta = self.metas[self.metaI]
        name = meta.get('name')
        if name is not None:
            self.statusSV.set("...")
            if os.path.isdir(name):
                self.previewFolder(name)
            else:
                self.showImage(name)
            if meta.get('checked') is True:
                self.markSV.set(True)
            else:
                self.markSV.set(False)
        else:
            self.statusSV.set(meta.get('line'))
            self.nameSV.set("")
            self.pathSV.set("")
            self.imgLabel.configure(image='')
            self.markSV.set(False)

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
        self.markSV.set(mark)
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
            <KeyPress event state=Shift keysym=underscore keycode=20 char='_' x=-1160 y=322>
            <KeyPress event state=Shift keysym=plus keycode=21 char='+' x=-1160 y=322>
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
        # ^ "root.MyIcon = Tk.PhotoImage(file='/usr/share/icons/gnome/32x32/apps/zen-icon.png')"
        # See <https://forums.raspberrypi.com/viewtopic.php?t=254725>
        root.MyIcon = tk.PhotoImage(file=iconPath)
        root.iconphoto(True, root.MyIcon)
    root.bind('<KeyPress>', mainframe.onKeyPress)
    prevArg = None
    mainDirPath = None
    listPath = None
    for arg in sys.argv:
        if prevArg is None:
            prevArg = arg  # the command that ran this script
            continue
        if listPath is None:
            listPath = arg
            mainframe.setList(arg)
        elif mainDirPath is None:
            mainDirPath = arg
            mainframe.setPath(arg)
        prevArg = arg
    root.after(1, mainframe.onFormLoaded)  # (milliseconds, function)
    root.mainloop()
    '''
    session.stop()
    if session.save():
        print("Save completed.")
    else:
        print("Save failed.")
    '''

if __name__ == "__main__":
    main()
