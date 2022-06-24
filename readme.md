# RotoCanvas
https://github.com/poikilos/rotocanvas

RotoCanvas aims to be a manual rotoscoping tool which includes a set of
tools for editing, viewing and managing images and image sequences.
Parts that are finished:
- findbyappearance: Find images of the same size by appearance!
- diffimage: Generate a difference image file (similar to the diffimg
  project, but with different flag colors such as for different size)
- The channeltinker module is an image processing library that can work
  with either GIMP or PIL images, so it can be used for either GIMP
  plugins or standalone applications!
- "Channel Tinker" GIMP Plugin:
  - Remove halo caused by bad alpha (a fringe that is an old
    background color usually).
  - Draw a centered square (such as for pixel art or other uses).
- For all commands implemented, see `entry_points` in
  [setup.py](setup.py).

This project now includes and replaces the gimp-plugin-channel-tinker
project (See the "Merging gimp-plugin-channel-tinker" section).

For now this repository serves as a collection of GUIs and modules for
manipulating videos and DVDs (being gradually moved from
[RotoCanvasPaint](https://github.com/poikilos/RotoCanvasPaint)). Star
this repo for updates. See [Using FFmpeg](#using-ffmpeg) below, and the
"more" directory in RotoCanvasPaint. Upstream ideas and code from "more" directory that
are implemented will be moved to "references". Please read "Purpose"
and "Why aren't there more rotoscoping applications?" below before
commenting on the code or submitting pull requests.


## Purpose
This is a manual rotoscoping (frame by frame painting) application.
Rotoscoping is the only accurate way to achieve effects such as manual
object removal (such as removing wires for flying scenes), cartoons
mixed with live action, correction of layer order errors (such as if the
wrong fingers get in the way of a virtual object that is held), doing
energy effects without 3D mockups of characters (3D mockups [invisible
blockers] are normally needed in order to address situations where part
or all of the energy effect goes behind a character or some of the
character's fingers), or detailed junk matte tweaking (such as is needed
when all or part of an actor appears in front of a studio wall instead
of a green screen). Before the digital age, these issues were addressed
by hand, and rotoscoping was considered an essential part of post
effects to address a whole domain of issues. The fact that there are so
few applications like this has become an obstacle. Ideally this project
will be used as a basis to create plugins (see Developer Notes) so that
more video editing applications will include rotoscoping, in this case
**nondestructive** rotoscoping. RotoCanvas is being tested and compiled
in a standalone application ("RotoCanvas Paint") so that the software
can be used right away.

### Why aren't there more rotoscoping applications?
Possibly, rotoscoping applications are not considered commercially
viable since there is unavoidable lag situations that can't be
reasonably blamed on developers but inevitably are (see "Caveats"
below). Unavoidable lag and video format complexity issues could be
reasons for the discontinuation of such programs as Ulead &reg;
VideoPaint &#174; (this project is not affiliated with Corel &reg; or
Ulead &reg;). Another reason could be that rotoscoping is highly
dependent on the source frame remaining the same, whereas MPEG (variants
of which are used almost everywhere) has inherently inexact frame
seeking. These issues may be partially or completely resolved by
advanced caching (for the lag issue) and advanced frame seeking
algorithms (for the accuracy issue), either of which are not easily
achieved but both of which are needed in a professional video
application (since video, which has slow seeking would be required,
and MPEG, which is normally inaccurate would be required). Even if image
sequences are used to resolve the seek lag and seek accuracy issues,
seek lag normally remains simply because the edits have to be re-applied
or re-loaded (basically, a multi-layer image project needs to be loaded
each time seeking to a different frame). Leaving rotoscoping out
entirely is often seen as the only way to avoid these issues. This
program aims to implement rotoscoping regardless of the possibility of
seek lag or requiring image sequences (to avoid seek accuracy issues).
In this project, rotoscoping (the core feature) is considered to be an
indispensable part of video editing, regardless of the fact that meeting
the expectations of normal consumers (primarily expectations for speed
and format support) may be impractical to be achieved by volunteer
programmers, or may be impossible for technical reasons described above.


## Caveats
Lag during frame loading cannot be avoided, since each video frame
must be loaded at full quality, which at 1080p takes up an unavoidable
8100kb per layer. Maximum performance could be achieved when one or more
frames in either direction of the current frame are cached, in their
edited form. However, upon editing, the cache will have to be updated
and the image, redrawn. To prevent further lag in that situation, the
source frame (base layer) could be cached so that editing layers can be
applied without reloading the frame from the source video file.

At this time, image sequences are required. MPEG-derived formats may
or may not ever be added, since MPEG-style frame seeking is inexact and
rotoscoping is highly dependent on the source frame remaining the same.


## Install
(See also: "Install GIMP Plugin" section)

From the web:
```
pip install --user --upgrade https://github.com/poikilos/rotocanvas/archive/refs/heads/main.zip
```

From this directory (`ls findbyappearance` makes sure you're in the
correct directory, so an error will be shown if you're not):
```
ls findbyappearance && pip install --user --upgrade .
```


## Requires
- Pillow

### Optional dependencies
- opencv for certain features such as AI super resolution
  - See tests/rcsource_tests.py under `except ImportError` for how to
    install it.
- pretrained models
  - Before using super resolution methods, you must add pb files via:

```
from RCSettings import settings
settings.addModel(pbFilePath)
```


## Planned Features
* [ ] Add markers to media OR timeline, separately (media markers are
  also on timeline behave differently: ghosted until media is selected,
  has filmstrip icon if from a clip; reversed if video is reversed,
  changed placement if speed is changed, etc).
* [ ] Use alpha.png for reducing opacity of parts of background layer.
* [ ] Allow a blocker layer type (make an animated object that seems to
  "undo" previous edits, such as to reveal parts of characters under
  the effect, without permanently erasing any part of the effect).
* [ ] Use the layer cache (purpose for unused variable cacheMaxMB).
* [ ] Keyboard controls for fast operation:
  * Ctrl Scrollwheel: zoom
  * Shift Alt Scrollwheel: brush hardness
  * Shift Scrollwheel: brush size
* [ ] Add exception handling in appropriate situations.
- Bake all changes including ffmpeg filters to png files then overlay
  them onto the video (to use frame rate from video automatically):
  `ffmpeg -i foo.mkv -i bar%04d.png -filter_complex "[1:v]format=argb,geq=r='r(X,Y)':a='alpha(X,Y)'[zork]; [0:v][zork]overlay" -vcodec libx264 myresult.mkv`
  - based on
    <https://stackoverflow.com/questions/38753739/ffmpeg-overlay-a-png-image-on-a-video-with-custom-transparency>
    answered Aug 3 '16 at 22:00 RocketNuts
    - overall opacity can be multiplied by prepending a value such
      as `0.5*`, for example: `a=0.5*'alpha(X,Y)'`
    - For no custom opacity (only 2nd layer's alpha), simplify to the
      line in the question at that link:
      `ffmpeg -i foo.mkv -i bar.png -filter_complex "[0:v][1:v]overlay" -vcodec libx264 myresult.mkv`

### Low-priority Features
See [doc/development/readme.md](doc/development/readme.md).


## Authors
All work is by Jake "Poikilos" Gustafson except that which is listed
below in this section or in its subsections.

### super_res_image_save
super_res_image_save is based on super_res_image.py
  by Adrian Rosebrock (conformed to PEP8 by Jake "Poikilos" Gustafson)

[OpenCV Super Resolution with Deep
Learning](https://www.pyimagesearch.com/2020/11/09/opencv-super-resolution-with-deep-learning/)
by Adrian Rosebrock on November 9, 2020

For more info (and alternatives) see the up-res section of
[doc/development/readme.md](doc/development/readme.md).


## Channel Tinker GIMP plugin

This is a GIMP plugin with tools for manipulating color and alpha.

This package contains a generalized advanced color channel manipulation
module called channeltinker that is currently only available here.

In GIMP, you can manipulate color and alpha using new "Channel Tinker"
sub-menu in the GIMP "Colors" menu.

### Install GIMP Plugin
#### Linux
See [setup-channeltinkergimp.sh](setup-channeltinkergimp.sh).

### How to Help
ChannelTinkerProgressInterface and ChannelTinkerInterface are
available so that far less duck typing is necessary to work with
radically different backends such as PIL and GIMP. You can make the
channeltinker module work with additional things beyond PIL and GIMP
by making your own implementation. See channel_tinker_gimp for an
example.
- You do not have to implement ChannelTinkerInterface if you provide
  the functions in channeltinker with a PIL image.
- You do not have to implement ChannelTinkerProgressInterface if you
  simply do not provide a ctpi argument to the channeltinker
  functions.

### Tasks
- [ ] Add hotkey 'r' for Channel Tinker (not yet taken in top level of
  Colors menu).
- [ ] Add [NTSC color gamut conversion](doc/development/NTSC.md) (at least recover from NTSC to RGB).

### Python-fu sites
- [API Documentation](https://www.gimp.org/docs/python/index.html)
- [Gimp Scripting: Python Fu, Automating Workflows, coding a complete plug-in](https://www.youtube.com/watch?v=uSt80abcmJs) by Jason Bates Sep 13, 2015
- [Python fu #6: Accepting user input](https://jacksonbates.wordpress.com/2015/09/14/python-fu-6-accepting-user-input/) by Jason Bates

### GIMP API
- Booleans (non-zero if true):
  - drawable.is_color
  - drawable.has_alpha
  - drawable.is_gray
  - drawable.is_indexed
  - drawable.visible
- Other
  - image.active_channel (assignable)
  - image.cmap (color map)
  - image.layers (list of layers)
  - image.selection (selection mask)
  - image.add_layer_mask(layer, mask)


## Using FFmpeg
Notes on features not yet added but which you can do manually with the
ffmpeg command are at:
[doc/development/ffmpeg.md](doc/development/ffmpeg.md)
