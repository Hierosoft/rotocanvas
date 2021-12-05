class FFMPEGTime:
    def __init__(self, timeStr, fps):
        self.parts = timeStr.split(":")
        # print("TimeStr: {}".format(timeStr))
        # print("Parts: {}".format(self.parts))
        self.fps = fps
        self._fpsF = None
        self._FParts = None
        self._recalculate()

    def setFPS(fps):
        self.fps = fps
        self._recalculate()

    def getFrameNumber(self):
        seconds = 0.0
        multiplier = 1.0
        for i in reversed(range(len(self._FParts))):
            seconds += self._FParts[i] * multiplier
            multiplier *= 60.0
        return int(seconds * self._fpsF)

    def _recalculate(self):
        self._fpsF = float(self.fps)
        self._FParts = [float(part) for part in self.parts]
