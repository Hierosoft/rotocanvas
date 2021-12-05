#!/usr/bin/env python
from decimal import Decimal
import decimal
import locale as lc
import math
import os

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import showerror
except ImportError:
    # python 2
    import Tkinter as tk
    import ttk
    from tkFileDialog import askopenfilename
    from tkMessageBox import showerror


# List theme names:

from rotocanvas.rcproject import RCProject

class ProjectFrame(ttk.Frame):
    def __init__(self, parent):
        self.localeResult = lc.setlocale(lc.LC_ALL, "")
        if self.localeResult == "C":
            lc.setlocale(lc.LC_ALL, "en_US")
        # example: moneyStr = lc.currency(amount, grouping=True)
        self.parent = parent
        root = self.parent
        self.seqPath = tk.StringVar()
        self.frameRate = tk.StringVar()
        self.result = tk.StringVar()

        ttk.Frame.__init__(self, parent)
        self.menu = tk.Menu(parent)
        self.fileMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.fileMenu)

        self.fileMenu.add_command(label="Open Video", command=self.open)
        self.fileMenu.add_command(label="Save", command=self.save)
        self.fileMenu.add_command(label="Save As", command=self.saveAs)
        self.fileMenu.add_command(label="Exit",
                                  command=self.parent.destroy)


        self.prepMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Prepare", menu=self.prepMenu)
        self.prepMenu.add_command(
            label="Super Resolution (This Frame)",
            command=self.srFrame
        )

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
        #   the same, like old xwindows (thick "3D" edges like Windows
        #   3.1)

        parent.config(menu=self.menu)
        self.pack(fill=tk.BOTH, expand=True)
        row = 0
        ttk.Label(self, text="Sequence:").grid(column=0, row=row,
                                               sticky=tk.E)
        ttk.Entry(self, textvariable=self.seqPath).grid(column=1,
                                                        columnspan=3,
                                                        row=row,
                                                        sticky=tk.W)
        row += 1
        ttk.Label(self, text="Frame Rate:").grid(column=0, row=row,
                                                 sticky=tk.E)
        ttk.Entry(self, textvariable=self.frameRate).grid(column=1,
                                                          columnspan=3,
                                                          row=row,
                                                          sticky=tk.W)
        self.frameRate.set("60000/1001")
        # Entry width=25, state="readonly"
        row += 1
        self.prev_button = ttk.Button(self, text="<", command=self.prev)
        self.prev_button.grid(column=0, row=row, sticky=tk.W)
        self.play_button = ttk.Button(self, text="Play",
                                      command=self.play)
        self.play_button.grid(column=1, row=row, sticky=tk.E)
        self.next_button = ttk.Button(self, text=">", command=self.next)
        self.next_button.grid(column=2, row=row, sticky=tk.E)
        row += 1
        # exitBtn = ttk.Button(self, text="Exit", command=root.destroy)
        # exitBtn.grid(column=2, row=row, sticky=tk.W)
        # row += 1

        self.canvas = tk.Canvas(self)
        self.canvas.grid(
            column=0,
            row=row,
            sticky=tk.W+tk.E,
            columnspan=3
        )
        row += 1

        # ttk.Label(self, text="Status: ").grid(column=0, row=row, sticky=tk.E)
        resultE = ttk.Entry(self, textvariable=self.result,
                            state="readonly")
        resultE.grid(column=0, columnspan=4, row=row, sticky=tk.E+tk.W)
        # grid sticky=tk.W
        row += 1

        for child in self.winfo_children():
            child.grid_configure(padx=6, pady=3)
        # self.prev_button['state'] = tk.DISABLED
        # self.next_button['state'] = tk.DISABLED

        self.project = RCProject()
        self.titleFmt = "RotoCanvas - {}"
        root.title(self.titleFmt.format(self.project.path))
        self.img = None

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
            title = "Select file",
            filetypes = (
                ("RotoCanvas project files", "*.rotocanvas"),
                ("all files", "*.*"),
            ),
        )
        self.project.path = path

    def save(self):
        saveError = self.project.save()
        if saveError is not None:
            self.result.set(saveError)

    def open(self):
        startIn = RCProject.VIDEOS
        tryIn = ("/home/owner/ownCloud/Tabletop/Campaigns/"
                 "The Path of Resistance/scanned-unsorted/")
        if os.path.isdir(tryIn):
            startIn = tryIn
        path = askopenfilename(
            initialdir=startIn,
            title = "Select file",
            filetypes = (
                ("image files", ["*.jpg", "*.png"]),
                ("jpeg files", "*.jpg"),
                ("png files", "*.png"),
                ("all files", "*.*"),
            ),
        )
        # self.project.open(path)
        self.project.addVideo(path, self.frameRate.get())
        self.seqPath.set(path)
        self.img = tk.PhotoImage(file=path)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        pass

    def end(self):
        pass


def main():
    root = tk.Tk()
    root.title("RotoCanvas")
    frame = ProjectFrame(root)
    project = frame.project
    root.mainloop()
    project.stop()
    saveError = project.save()
    if saveError is None:
        print("Save completed.")
    else:
        print("[pyrotocanvas run.py main] Save failed: {}"
              "".format(saveError))


if __name__ == "__main__":
    main()
