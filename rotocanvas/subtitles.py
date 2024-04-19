#!/usr/bin/env python3
from __future__ import print_function
from datetime import timedelta
import copy
from rotocanvas.timestamp import srtTsToDelta, deltaToSrtTs
from rotocanvas import (  # noqa: F401
    echo0,
    echo1,
    echo2,
)


class Subtitle:
    """Individual timed caption.

    For a sequence, use the *Subtitles* class instead.

    Args:
        startTsStr (Optional[str]): a start timestamp as a string such as
            00:00:00,899
        endTsStr (Optional[str]): an end timestamp as a string such as
            00:00:09,299
        data (Optional[str]): one or more lines separated by \n.

    """
    def __init__(self, startTsStr=None, endTsStr=None, data=None):
        # For Args see class docstring.
        self.index = -1
        self.startTsStr = startTsStr
        self.endTsStr = endTsStr
        self.startDelta = None
        self.endDelta = None
        self.data = data
        if self.data is None:
            self.data = ""

    def parse(self):
        """Interpret strings in self to create timedelta objects.
        """
        if isinstance(self.index, str):
            self.index = int(self.index)
        elif isinstance(self.index, int):
            pass
        elif self.index is None:
            # It can be None until used in processing or saving.
            pass
        else:
            raise ValueError("index should be int but is {}"
                             "".format(type(self.index).__name__))
        self.startDelta = srtTsToDelta(self.startTsStr)
        self.endDelta = srtTsToDelta(self.endTsStr)

    def unparse(self):
        """Convert deltas to startTsStr and endTsStr strings.
        """
        self.startTsStr = deltaToSrtTs(self.startDelta)
        self.endTsStr = deltaToSrtTs(self.endDelta)

    def dump(self, handle):
        if self.index is None:
            raise ValueError("index is None")
        if not self.data:
            print("WARNING: No data is in subtitle index {}"
                  "".format(self.index))
            return
        if self.startTsStr is None:
            raise ValueError("No startTsStr")
        if self.endTsStr is None:
            raise ValueError("No startTsStr")
        handle.write("{} --> {}\n"
                     "".format(self.startTsStr, self.endTsStr))
        handle.write("{}\n".format(self.data))
        handle.write("\n")


class Subtitles:
    """A set of subtitles such as for a video.

    Attributes:
        subs (list[Subtitle]): Subtitle objects.
    """
    def __init__(self, path=None):
        self.subs = None
        self.path = path
        if path is not None:
            self.load(path)

    def load(self, path):
        self.subs = []
        INDEX = 0  # index context expects a number such as 1
        TS = 1
        # ^ timestamp context expects a timestamp set
        #   such as 00:00:00,899 --> 00:00:09,299
        DATA = 2  # The data context expects 1+ lines then a blank
        context = INDEX
        sub = Subtitle()
        lineN = 0
        contexts = ["INDEX", "TIMESTAMP", "CAPTION"]
        with open(path, mode='r', encoding='UTF-8-sig') as ins:
            for rawL in ins:
                lineN += 1  # Counting numbers start at 1.
                line = rawL.strip("\n\r")
                # Avoid "ValueError: invalid literal
                # for int() with base 10: '\ufeff1'":
                # Avoid the initial EF BB BF (UTF-8 BOM)
                # Somehow the first [stripped] line found is (\ufeff1)
                # but 1 is 31 and the file starts with EF BB BF 31
                # [then OD OA]
                # - FEFF is ZERO WIDTH NO-BREAK SPACE (UTF-16 BOM)!
                # - "in UTF-8 it is more commonly known as 0xEF,0xBB, or
                #   0xBF."
                #   -<https://www.freecodecamp.org/news/a-quick-tale-
                #   about-feff-the-invisible-character-cd25cd4630e7/#:~:
                #   text=Our%20friend%20FEFF%20means%20different,
                #   0xEF%2C0xBB%2C%20or%200xBF%20.>
                # - One solution is read the whole file with read() then
                #   do data = dataBin.decode("utf-8-sig")
                # - SOLVED: Use encoding="utf-8-sig" with open.
                lineStrip = line.strip()
                if context == INDEX:
                    try:
                        sub.index = int(lineStrip)
                    except Exception as ex:
                        lsLen = len(lineStrip)
                        echo0("{}:{}: bad index format len {}: {}"
                              "".format(path, lineN, lsLen, lineStrip))
                        raise ex
                    context = TS
                elif context == TS:
                    parts = line.split(" --> ")
                    if len(parts) != 2:
                        raise SyntaxError("{}:{}: missing time --> time"
                                          "".format(path, lineN))
                    sub.startTsStr, sub.endTsStr = parts
                    try:
                        sub.parse()
                    except Exception as ex:
                        echo0("{}:{}: bad timestamp format"
                              "").format(path, lineN)
                        raise ex
                    context = DATA
                elif context == DATA:
                    if len(line.strip()) == 0:
                        if len(line) > 0:
                            print("{}:{}: WARNING: There are only"
                                  " spaces so the end of the caption"
                                  " is assumed (end with a blank line"
                                  " to avoid this warning)"
                                  "".format(path, lineN))
                        line = ""
                    if len(line) == 0:
                        sub.parse()
                        self.subs.append(sub)
                        sub = Subtitle()
                        context = INDEX
                    else:
                        if (sub.data is None) or (len(sub.data) == 0):
                            sub.data = line
                        else:
                            sub.data += "\n" + line
                else:
                    raise RuntimeError("The context is invalid: {}"
                                       "".format(context))
        if context == DATA:
            if sub.data is not None:
                self.subs.append(sub)
                context = INDEX
        if context != INDEX:
            raise SyntaxError("{}:{}: missing {}"
                              "".format(path, lineN, contexts[context]))

    def append(self, nextSubs, delay_ms=0):
        """Concatenate another Subtitles object to this one.

        Args:
            nextSubs (Subtitles): The subtitles to place starting at the
                time the last subtitle stops on this object's.
            delay_ms (int): Set how many milliseconds after the last
                subtitle ends that nextSubs should start.
        """
        pushDelta = timedelta(milliseconds=delay_ms)
        zeroDelta = self.subs[-1].endDelta + pushDelta
        index = self.subs[-1].index
        print("* appending subtitle 1 as {} at {}"
              "".format(index + 1, zeroDelta))
        for sub in nextSubs.subs:
            index += 1
            offsetSub = copy.deepcopy(sub)
            # spanDelta = offsetSub.endDelta - offsetSub.startDelta
            offsetSub.startDelta += zeroDelta
            offsetSub.endDelta += zeroDelta
            offsetSub.index = index
            self.subs.append(offsetSub)

    def save(self, path):
        """Save a SRT-format file.

        Args:
            path (str): A path to a file to create/overwrite, normally
                ending in ".srt".
        """
        self.path = path
        with open(path, 'w') as outs:
            for sub in self.subs:
                sub.unparse()
                outs.write(str(sub.index) + "\n")
                outs.write(sub.startTsStr + " --> " + sub.endTsStr + "\n")
                if "\r" in sub.data:
                    print("WARNING: \\r in {}".format(sub.data))
                outs.write(sub.data + "\n")
                outs.write("\n")

# For tests, see or create /tests/rotocanvas/test_subtitles.py
