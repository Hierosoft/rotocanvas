#!/usr/bin/env python3
from __future__ import division
from datetime import datetime, timedelta

def srtTsToDelta(timestampStr):
    """
    Sequential arguments:
    timestampStr -- This is a millisecond-based timestamp such as
        00:00:21,341 which is the format used in SRT subtitle files.
    """
    if len(timestampStr) < 12:
        raise SyntaxError("timestampStr must be in the SRT format"
                          " such as \"00:00:21,341\"")
    if timestampStr[-4] != ",":
        raise SyntaxError("timestampStr must be in the SRT format"
                          " such as \"00:00:21,341\""
                          " but comma isn't there.")
    msStr = timestampStr[-3:]
    if timestampStr[-7] != ":":
        raise SyntaxError("timestampStr must be in the SRT format"
                          " such as \"00:00:21,341\""
                          " but ':' before seconds isn't there.")
    sStr = timestampStr[-6:-4]
    if timestampStr[-10] != ":":
        raise SyntaxError("timestampStr must be in the SRT format"
                          " such as \"00:00:21,341\""
                          " but ':' before minutes isn't there.")
    mStr = timestampStr[-9:-7]
    hStr = timestampStr[:-10]

    delta = timedelta(
        hours=int(hStr),
        minutes=int(mStr),
        seconds=int(sStr),
        milliseconds=int(msStr),
    )
    return delta


def deltaToSrtTs(delta):
    """
    Convert a timedelta to an SRT string such as 00:00:21,341.
    See <https://stackoverflow.com/a/539360/4541104>
    """
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    ms = delta.microseconds // 1000
    return ("{:02}:{:02}:{:02},{:03}"
            "".format(int(hours), int(minutes), int(seconds), ms))


class Timestamp:
    """
    This is a video timestamp that rolls on forever and doesn't roll
    over the day. It is much like a timedelta.
    """
    def __init__(self, timestampStr):
        """
        Sequential arguments:
        timestampStr -- See "srtTsToDelta".
        """
        self.delta = srtTsToDelta(timestampStr)


if __name__ == "__main__":
    print("To use this file, import parts using Python such as via:")
    print("    from timestamp import srtTsToDelta, deltaToSrtTs")
    # print("Or install nose and test via:")
    # print("python -m nose")
    print ("For tests, see tests/test_timestamp in the rotocanvas"
           " module or run nose in the parent directory"
           " (the rotocanvas repo).")
