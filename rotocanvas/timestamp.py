#!/usr/bin/env python3
from __future__ import division
from __future__ import print_function
from datetime import timedelta

from rotocanvas import (  # noqa: F401
    echo0,
    echo1,
    echo2,
)


def srtTsToDelta(timestampStr):
    """Convert an SRT-format timestamp to a datetime.timedelta object.

    Args:
        timestampStr (str): This is a millisecond-based timestamp such
            as 00:00:21,341 which is the format used in SRT subtitle
            files.
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
    """Convert a timedelta to an SRT string such as 00:00:21,341.

    See <https://stackoverflow.com/a/539360/4541104>

    Args:
        delta (datetime.timedelta): Any timedelta.
    """
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    ms = delta.microseconds // 1000
    return ("{:02}:{:02}:{:02},{:03}"
            "".format(int(hours), int(minutes), int(seconds), ms))


def frame_to_ffmpeg_timecode(frame_number, fps):
    """Convert a frame number to an FFMPEG timecode

    Offset by half of a frame delay to ensure the correct frame is
    obtained--ensure float storage, rounding or FFMPEG oddities,
    whichever is involved, doesn't cause the issue of getting the wrong
    frame (See my comments at an issue that is possibly related:
    <github.com/mifi/lossless-cut/issues/126#issuecomment-1159735807>).

    Args:
        frame_number (int): Frame number.
        fps (float): Exact frames per second (such as 29.97 if using
            NTCS drop-frame).
    """
    # I originally posted this code at
    # <https://github.com/mifi/lossless-cut/issues/126
    # #issuecomment-1159735807>
    # but it is based on <https://github.com/poikilos/RetroEngine-cs/
    # blob/433773855ab8e792f9756ed0b39c80d4976a097a/RConvert.cs#L257>
    # ^ fixed since then to add `1000.0 *` in millisecond formula
    fps = float(fps)
    frame_remainder = float(frame_number)
    second_to_hour = 60.0 * 60.0
    second_to_minute = 60.0
    hour = int(frame_remainder / (fps * second_to_hour))
    frame_remainder -= float(hour) * (fps * second_to_hour)
    minute = int(frame_remainder / (fps * second_to_minute))
    frame_remainder -= float(minute) * (fps * second_to_minute)
    second = int(frame_remainder / fps)
    frame_remainder -= float(second) * fps
    sec_per_frame = 1.0 / fps
    echo2("frame_remainder={}".format(frame_remainder))
    millisecond_f = (frame_remainder * (1000.0 / fps)
                     + 1000.0 * sec_per_frame / 2.0)
    echo2("millisecond_f={}".format(millisecond_f))
    millisecond = int(millisecond_f)
    # ^ add sec_per_frame / 2.0 to get to the "middle" of the frame
    #   --so as not to undershoot!
    return "{}:{}:{}:{:0=3d}".format(hour, minute, second, millisecond)


class Timestamp:
    """
    This is a video timestamp that rolls on forever and doesn't roll
    over the day. It is much like a timedelta.

    Args:
        timestampStr (str): See "srtTsToDelta" function documentation.
    """
    def __init__(self, timestampStr):
        # For Args see class docstring.
        self.delta = srtTsToDelta(timestampStr)


if __name__ == "__main__":
    print("To use this file, import parts using Python such as via:")
    print("    from timestamp import srtTsToDelta, deltaToSrtTs")
    # print("Or install nose and test via:")
    # print("python -m nose")
    print("For tests, see tests/test_timestamp in the rotocanvas"
          " module or run nose in the parent directory"
          " (the rotocanvas repo).")
