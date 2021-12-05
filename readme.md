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

This project may serve as a backend or companion or replacement for the
[RotoCanvasPaint](https://github.com/poikilos/RotoCanvasPaint), project
where you can find more information about the goals and scope of the
project.

This project now includes and replaces the gimp-plugin-channel-tinker
project (See the "Merging gimp-plugin-channel-tinker" section).


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


## Tasks
- [ ] for upscaling VHS (tested using Rebel Assault IX), use one of the
  following G'MIC plugins after upscaling:
  - "Sharpen [Richardson-Lucy]"; Sigma: 1.25; Iterations: 10 (default);
    Blur: Gaussian (default); cut: True (default)
  - Sharpen [Octave Sharpening]; Parallel Processing: Four Threads (or
    more--use a global setting); (others: default)
  - Simple Local Contrast (seems to add noise or false detail, but may
    be ok); Edge Sensitivity: 4.05; Iterations: 1; (others: default)
- [ ] Try making the "Smart Sharpening" tutorial into a script:
  https://www.gimp.org/tutorials/Smart_Sharpening/
- [ ] Try TecoGAN
  - Docker version: https://github.com/tom-doerr/TecoGAN-Docker
- [ ] Try enhancenet-pretrained:
  ~/Videos/Demo_Reel-Recovered-SD_but_2nd_Gen/enhancenet_pretrained/
- [ ] Try RealSR (requires Vulkan):
```
wget https://github.com/nihui/realsr-ncnn-vulkan/releases/download/20200818/realsr-ncnn-vulkan-20200818-linux.zip
unzip realsr-ncnn-vulkan-20200818-linux.zip
cd realsr-ncnn-vulkan-20200818-linux
mkdir -p $HOME/bin/realsr-ncnn-vulkan-models
cp -r models-DF2K models-DF2K_JPEG $HOME/bin/realsr-ncnn-vulkan-models
cp realsr-ncnn-vulkan $HOME/bin
```
  -<https://linuxreviews.org/RealSR#Installation>
- [ ] Automatically download models from [ONNX Model
  Zoo](https://github.com/onnx/models) (OpenCV allows loading ONNX
  models via `cv2.dnn.readNetFromONNX(`--See [Super Resolution with
  OpenCV](https://bleedai.com/super-resolution-with-opencv/))


## Authors

All work is by Jake "Poikilos" Gustafson except that which is listed
below in this section or in its subsections.

### super_res_image_save
super_res_image_save is based on super_res_image.py
  by Adrian Rosebrock (conformed to PEP8 by Jake "Poikilos" Gustafson)

[OpenCV Super Resolution with Deep
Learning](https://www.pyimagesearch.com/2020/11/09/opencv-super-resolution-with-deep-learning/)
by Adrian Rosebrock on November 9, 2020

I requested for the Wayback Machine to archive it:
- [snapshot](https://web.archive.org/web/20201109211028/https://www.pyimagesearch.com/2020/11/09/opencv-super-resolution-with-deep-learning/)
- [screen shot](https://web.archive.org/web/20201109211028/http://web.archive.org/screenshot/https://www.pyimagesearch.com/2020/11/09/opencv-super-resolution-with-deep-learning/)

> ...there are super resolution deep neural networks that are both:
>
> 1. Pre-trained (meaning you don’t have to train them yourself on a dataset)
> 2. Compatible with OpenCV
> However, OpenCV’s super resolution functionality is actually “hidden”
> in a submodule named in `dnn_superres` in an obscure function called
> `DnnSuperResImpl_create`.


> Photoshop, GIMP, Image Magick, OpenCV (via the cv2.resize function),
> etc. all use classic interpolation techniques and algorithms (ex.,
> nearest neighbor interpolation, linear interpolation, bicubic
> interpolation)

Related methods and corresponding papers:
> - _**EDSR:** [Enhanced Deep Residual Networks for Single Image Super-Resolution](https://arxiv.org/abs/1707.02921) ([implementation](https://github.com/Saafke/EDSR_Tensorflow))_
> - **ESPCN:** _[Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network](https://arxiv.org/abs/1609.05158)_ ([implementation](https://github.com/fannymonori/TF-ESPCN))
> - **FSRCNN:** _[Accelerating the Super-Resolution Convolutional Neural Network](https://arxiv.org/abs/1608.00367)_ ([implementation](https://github.com/Saafke/FSRCNN_Tensorflow))
> - **LapSRN:** _[Fast and Accurate Image Super-Resolution with Deep Laplacian Pyramid Networks](https://arxiv.org/abs/1710.01992)_ ([implementation](https://github.com/fannymonori/TF-LAPSRN))
> A big thank you to Taha Anwar from BleedAI for putting together
> [his guide](https://bleedai.com/super-resolution-going-from-3x-to-8x-resolution-in-opencv/)
> on OpenCV super resolution, which curated much of this information —
> it was immensely helpful when authoring this piece.


## Developer Notes

### RCSource
- if `_first` is `None`, it is a single image.
  - Use `self.os.path.split(self._vidPathNoExt)[1]` not `_prefix` to
    generate a name (along with `self._ext`).
  - `self.getFrameName` will still work but will always return the same
    image file name.

### First-time Setup of This Repo
(running some of these steps again may not be necessary)

```
#python3 -m pip install --user virtualenv
REPO_PATH=`pwd`
python3 -m venv ../opencvenv
source ../opencvenv/bin/activate
pip install opencv-contrib-python
# Rosebrock recommends `pip install opencv-contrib-python==4.1.0.25`
# at https://www.pyimagesearch.com/2018/09/19/pip-install-opencv/
# pip install --upgrade pip
mkdir ../super-resolution-implementations
cd ../super-resolution-implementations
git clone https://github.com/Saafke/EDSR_Tensorflow.git
git clone https://github.com/fannymonori/TF-ESPCN.git
git clone https://github.com/Saafke/FSRCNN_Tensorflow.git
git clone https://github.com/fannymonori/TF-LAPSRN.git
cd $REPO_PATH
cd ..
REPOS_PATH=`pwd`
cd $REPO_PATH
mkdir models
ln -s $REPOS_PATH/super-resolution-implementations/EDSR_Tensorflow/models/EDSR_x4.pb models/
ln -s $REPOS_PATH/super-resolution-implementations/TF-ESPCN/export/ESPCN_x4.pb models/
ln -s $REPOS_PATH/super-resolution-implementations/FSRCNN_Tensorflow/models/FSRCNN_x3.pb models/
ln -s $REPOS_PATH/super-resolution-implementations/TF-LAPSRN/export/LapSRN_x8.pb models/

deactivate
```

### Merging gimp-plugin-channel-tinker
The gimp-plugin-channel-tinker project was merged into and replaced by
rotocanvas (formerly pyrotocanvas).
- See the [changelog](changelog.md) entry for 2021-12-04.

## Channel Tinker GIMP plugin

This is a GIMP plugin with tools for manipulating color and alpha.

This package contains a generalized advanced color channel manipulation
module called channeltinker that is currently only available here.

In GIMP, you can manipulate color and alpha using new "Channel Tinker"
sub-menu in the GIMP "Colors" menu.


### Install GIMP Plugin
#### Linux
```
mkdir -p ~/git
git clone https://github.com/poikilos/rotocanvas
if [ -f ~/.config/GIMP/2.10/plug-ins/channel_tinker.py ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channel_tinker.py
fi
if [ -f ~/.config/GIMP/2.10/plug-ins/channeltinkergimp.py ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channeltinkergimp.py
fi
if [ -d ~/.config/GIMP/2.10/plug-ins/channel_tinker ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channel_tinker  # try symlink FIRST
    if [ $? -ne 0 ]; then
        # If there was an error, assume it is a directory:
        rm -Rf ~/.config/GIMP/2.10/plug-ins/channel_tinker
    fi
fi
if [ -d ~/.config/GIMP/2.10/plug-ins/channeltinker ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channeltinker  # try symlink FIRST
    if [ $? -ne 0 ]; then
        # If there was an error, assume it is a directory:
        rm -Rf ~/.config/GIMP/2.10/plug-ins/channeltinker
    fi
fi
cp -R channeltinker ~/.config/GIMP/2.10/plug-ins/
cp channeltinkergimp.py ~/.config/GIMP/2.10/plug-ins/
# or
# ln -s ~/git/rotocanvas/channeltinkergimp.py ~/.config/GIMP/2.10/plug-ins/
# ln -s ~/git/rotocanvas/channeltinker ~/.config/GIMP/2.10/plug-ins/
# ls -l ~/.config/GIMP/2.10/plug-ins/channeltinker
```

### How to Help
- ChannelTinkerProgressInterface and ChannelTinkerInterface are
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

