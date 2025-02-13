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
    # import tkinter.messagebox as messagebox
else:  # Python 2
    import Tkinter as tk  # type: ignore
    import ttk  # type: ignore
    from tkFileDialog import (  # type: ignore
        askopenfilename,
        asksaveasfilename,
    )
    # import tkMessageBox as messagebox

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
from rotocanvas.rcproject import RCProject  # noqa: E402
from rotocanvas.moremimetypes import (
    # dot_ext_mimetype,
    path_mimetype,
)

DEFAULT_SETTINGS = {
    'recent_paths': [],
}

logger = getLogger(__name__)


class ProjectFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        self.localeResult = lc.setlocale(lc.LC_ALL, "")
        if self.localeResult == "C":
            lc.setlocale(lc.LC_ALL, "en_US")
        # example: moneyStr = lc.currency(amount, grouping=True)
        self.parent = parent
        root = self.parent
        self.photo = None
        self.image_instruction = None
        self.seqPath = tk.StringVar()
        self.frameRate = tk.StringVar()
        self.result = tk.StringVar()
        self.cols = 5

        style = ttk.Style()
        style.configure("Custom.TFrame", background="darkgray")

        # kwargs['style'] = "Custom.TFrame"

        ttk.Frame.__init__(self, parent, **kwargs)


        self.menu = tk.Menu(parent)
        self.fileMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.fileMenu)

        self.fileMenu.add_command(label="Open Video", command=self.askOpen)
        self.fileMenu.add_command(label="Save", command=self.save)
        self.fileMenu.add_command(label="Save As", command=self.saveAs)
        self.fileMenu.add_separator()
        # self.recentPathsIndex = len(self.fileMenu.children)
        # NOTE: ^ 0 for some reason.
        self.recentPathsIndex = 4  # FIXME: hard-coded
        self.loadSettings()
        recent_paths = self.settings.get("recent_paths")
        if recent_paths:
            for path in recent_paths:
                self.fileMenu.add_command(
                    label=path,
                    command=lambda p=path: self.open(p),
                    # ^ p=path for early binding or all will open last path
                )
            self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.parent.destroy)

        self.prepMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Prepare", menu=self.prepMenu)
        self.prepMenu.add_command(label="Super Resolution (This Frame)",
                                  command=self.srFrame)

        # self.themeMenu = tk.Menu(self.menu, tearoff=0)
        # self.menu.add_cascade(label="Theme", menu=self.themeMenu)
        # root.style = ttk.Style()
        # for name in root.style.theme_names():
        #     self.themeMenu.add_command(
        #         label=name,
        #         command=lambda: self.setTheme(name)
        #     )
        # ^ skip this. On Windows it is automatic, and on GNU+Linux
        #   systems, all of them (clam, alt, default, classic) are all
        #   the same, like motif (thick "3D" edges like Windows 3.1)

        parent.config(menu=self.menu)
        self.pack(fill=tk.BOTH, expand=True)
        row = 0
        self.seq_label = ttk.Label(self, text="Sequence:")
        self.seq_label.grid(column=0, row=row, sticky=tk.E)
        self.seq_entry = ttk.Entry(self, textvariable=self.seqPath)
        self.seq_entry.grid(column=1, columnspan=self.cols-1, row=row,
                            sticky=tk.EW)
        row += 1
        self.fr_label = ttk.Label(self, text="Frame Rate:")
        self.fr_label.grid(column=0, row=row, sticky=tk.E)
        self.fr_entry = ttk.Entry(self, textvariable=self.frameRate)
        self.fr_entry.grid(column=1, columnspan=self.cols-1, row=row,
                           sticky=tk.EW)
        self.frameRate.set("60000/1001")
        # Entry width=25, state="readonly"
        row += 1
        self.prev_button = ttk.Button(self, text="<", command=self.prev)
        self.prev_button.grid(column=0, row=row, sticky=tk.W)
        self.play_button = ttk.Button(self, text="Play", command=self.play)
        self.play_button.grid(column=2, row=row, sticky=tk.EW)
        self.next_button = ttk.Button(self, text=">", command=self.next)
        self.next_button.grid(column=self.cols-1, row=row, sticky=tk.E)
        row += 1
        # exitBtn = ttk.Button(self, text="Exit", command=root.destroy)
        # exitBtn.grid(column=2, row=row, sticky=tk.W)
        # row += 1

        self.canvas_frame = ttk.Frame(self, style="Custom.TFrame")
        # self.canvas = tk.Canvas(self)
        # self.canvas.grid(column=0, row=row, sticky=tk.NSEW,
        #                  columnspan=self.cols)
        self.canvas_frame.grid(column=0, row=row, sticky=tk.NSEW,
                               columnspan=self.cols)
        self.canvas = tk.Canvas(self.canvas_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas_row = row
        row += 1

        # ttk.Label(self, text="Status: ").grid(column=0, row=row, sticky=tk.E)
        resultE = ttk.Entry(self, textvariable=self.result, state="readonly")
        resultE.grid(column=0, columnspan=self.cols, row=row, sticky=tk.EW)
        # grid sticky=tk.W
        row += 1

        for child in self.winfo_children():
            child.grid_configure(padx=6, pady=3)
        # self.prev_button['state'] = tk.DISABLED
        # self.next_button['state'] = tk.DISABLED

        self.project = RCProject()
        self.titleFmt = "RotoCanvas - {}"
        root.title(self.titleFmt.format(self.project.path))

        # weight=1 allows widget to expand:
        for i in range(self.cols):
            if i == 0 or i == self.cols - 1:
                self.columnconfigure(i, weight=0)
            else:
                self.columnconfigure(i, weight=1)

        for i in range(row):  # 'row' holds the last used row index
            if i == self.canvas_row:
                self.rowconfigure(i, weight=1)  # weight=1 to expand
            else:
                self.rowconfigure(i, weight=0)

    def configsPath(self):
        confs_dir = os.path.join(sysdirs['APPDATA'], "rotocanvas")
        if not os.path.isdir(confs_dir):
            os.makedirs(confs_dir)
        return confs_dir

    def configPath(self):
        return os.path.join(self.configsPath(), "settings.json")

    def addRecent(self, path):
        if path in self.settings['recent_paths']:
            self.settings['recent_paths'].remove(path)
            self.fileMenu.delete(path)
        self.fileMenu.insert(
            self.recentPathsIndex,
            'command',
            label=path,
            command=lambda p=path: self.open(p),
        )
        if not self.settings['recent_paths']:
            # If it is the first one, add a separator.
            self.fileMenu.insert_separator(
                self.recentPathsIndex + 1,
            )
        self.settings['recent_paths'].insert(0, path)

    def loadSettings(self):
        path = self.configPath()
        loaded = False
        if os.path.isfile(path):
            with open(path, 'r') as stream:
                settings = json.load(stream)
                loaded = True
        else:
            settings = {}
        self.settings = copy.deepcopy(DEFAULT_SETTINGS)
        for key, value in settings.items():
            self.settings[key] = value
        return loaded

    def saveSettings(self):
        path = self.configPath()
        tmp = path + ".tmp"
        with open(tmp, 'w') as stream:
            json.dump(self.settings, stream)
        if os.path.isfile(path):
            os.remove(path)
        shutil.move(tmp, path)

    def setTheme(self, name):
        self.parent.style.theme_use(name)

    def next(self):
        pass

    def prev(self):
        pass

    def play(self):
        pass

    def srFrame(self):
        video = self.project._videos[self.seqPath.get()]
        video.superResolutionAI(
            onlyTimes=None,
            forceRatio=None,
            outFmt="png",
            qscale_v=2,
            minDigits=None,
            preserveDim=1,
            organizeMode=0,
            onlyFrames=None
        )

    def saveAs(self):
        path = asksaveasfilename(
            initialdir=RCProject.VIDEOS,
            title="Select file",
            filetypes=(
                ("RotoCanvas project files", "*.rotocanvas"),
                ("all files", "*.*"),
            ),
        )
        self.project.path = path

    def save(self):
        saveError = self.project.save()
        if saveError is not None:
            self.result.set(saveError)

    def askOpen(self):
        startIn = RCProject.VIDEOS
        tryIn = os.path.join(sysdirs['HOME'], "Nextcloud", "Tabletop",
                             "Campaigns", "The Path of Resistance",
                             "scanned-unsorted")
        if os.path.isdir(tryIn):
            startIn = tryIn
        path = askopenfilename(
            initialdir=startIn,
            title="Select file",
            filetypes=(
                ("image files", ["*.jpg", "*.png"]),
                ("jpeg files", "*.jpg"),
                ("png files", "*.png"),
                ("all files", "*.*"),
            ),
        )
        if not path:
            return
        self.open(path)

    def _open_no_puremagic(self, path, results_template=None):
        results = make_real(results_template)
        try:
            self.photo = tk.PhotoImage(file=path)
            results['category'] = "image"
        except tk.TclError:
            self.photo = None
            if ENABLE_PIL:
                try:
                    self.photo = ImageTk.PhotoImage(file=path)
                    results['category'] = "image"
                except PIL.UnidentifiedImageError:
                    raise
                    raise NotImplementedError()
                    # self.photo = ImageTk.PhotoImage()
                    results['category'] = "video"
            else:
                logger.error("PIL is not enabled.")
                raise
        return results

    def openImageSequence(self, path, results_template):
        results = make_real(results_template)
        try:
            self.photo = tk.PhotoImage(file=path)
            results['category'] = "image"
        except tk.TclError:
            self.photo = None
            if ENABLE_PIL:
                try:
                    self.photo = ImageTk.PhotoImage(file=path)
                    results['category'] = "image"
                except PIL.UnidentifiedImageError:
                    logger.error("PIL couldn't load the file.")
                    raise
            else:
                logger.error("PIL is not enabled.")
                raise
        return results

    def onLoadProgress(self, event_d):
        ratio = event_d.get('ratio')
        percent_s = ""
        if ratio:
            percent_s = "{}%".format(round(ratio))
        logger.warning("[onLoadProgress] Not implemented. {}"
                       .format(percent_s))

    def openVideo(self, path, results_template=None):
        results = make_real(results_template)
        if ENABLE_AV:
            cache = rc_av.cache_keyframes(path)
            meta = rc_av.analyze_video(path, self.onLoadProgress)
            # collect and remove runtime data:
            self.container = meta['container']
            del meta['container']
            raise NotImplementedError(meta)
            # See analyze_video in docs/development
            # Generate a picture (or use canvas directly?) to show video.
        else:
            raise RuntimeError(
                "Only PyAV is implemented (not pyav)"
                " but av is not detected/enabled.")
        return results

    def showFrame(self, frame_number):
        """Displays a specific frame of the video."""
        # Seek to the desired frame
        self.container.seek(frame_number, stream=self.video_stream)

        # Decode the frame
        for packet in self.container.demux(self.video_stream):
            for frame in packet.decode():
                # Display the decoded frame
                self.current_frame = frame
                img = frame.to_image()
                # self.photo = ImageTk.PhotoImage(img)
                # ^ Keep a reference to prevent garbage collection
                self.showPhotoImage(self.photo)
                # self.label.config(image=self.photo)
                # self.label.image = self.photo
                break
            break

    def clearCanvas(self):
        self.canvas.delete("all")

    def showPhotoImage(self, photoimage):
        self.photo = photoimage
        self.clearCanvas()
        self.image_instruction = \
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        # self.image_instruction example: int(1)
        # raise NotImplementedError(
        #     "self.image_instruction={}({})"
        #     .format(type(self.image_instruction).__name__,
        #             self.image_instruction))

    def open(self, path, results_template=None):
        results = make_real(results_template)
        # self.project.open(path)
        self.project.addVideo(path, self.frameRate.get())
        self.seqPath.set(path)
        self.addRecent(path)
        self.saveSettings()
        self.clearCanvas()
        try:
            file_info = puremagic.from_file(path)
            # ^ huh? Only gets a string: ".mp4" so:
            if isinstance(file_info, str):
                # Why just mp4?
                logger.warning("file_info={}".format(file_info))
                if "/" not in file_info:
                    mime_type = path_mimetype(path)
                    if mime_type is None:
                        raise ValueError(
                            "Unknown extension for \"{}\""
                            .format(path))
                else:
                    mime_type = file_info
            else:
                logger.info("file_info={}".format(file_info))
                mime_type = file_info[0].mime_type  # Get the MIME type
            results['mime_type'] = mime_type
            logger.warning("Loading {}".format(mime_type))
            # Check if the file is an image or video
            if mime_type.startswith("image/"):
                results.update(
                    self.openImageSequence(path, results_template=results)
                )
            elif mime_type.startswith("video/"):
                results.update(self.openVideo(path))
                results['category'] = "video"
            else:
                logger.error("The file is of another type:", mime_type)
        except puremagic.PureError as ex:
            logger.error("Could not determine file type:")
            logger.exception(ex)
        self.showPhotoImage(self.photo)
        return results

    def end(self):
        pass


demo_paths = [
    os.path.join(sysdirs['HOME'], "Videos", "The Secret of Cooey", "media",
                 "Darkness Ethereal - The Secret of Cooey - 1998.mp4"),
    os.path.join(sysdirs['HOME'], "Nextcloud", "Music", "Projects",
                 "The Secret of Cooey", "album-cover",
                 "Cooey's Call (Album Cover) - Piano EP.jpg"),
]


def main():
    root = tk.Tk()
    root.title("RotoCanvas")
    frame = ProjectFrame(root)
    project = frame.project
    for demo_path in demo_paths:
        if os.path.exists(demo_path):
            demo_link = os.path.join(REPO_DIR, "video.mp4")
            if not os.path.islink(demo_link):
                os.symlink(demo_path, demo_link)
            if not ENABLE_AV and demo_path.lower().endswith(".mp4"):
                continue
            root.after(0, frame.open, demo_path)
            break
    root.mainloop()
    project.stop()
    saveError = project.save()
    if saveError is None:
        print("Save completed.")
    else:
        print("[rotocanvas run.py main] Save failed: {}"
              "".format(saveError))


if __name__ == "__main__":
    main()
