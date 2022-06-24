# Development


## Design Directives
* Completely customizable but good defaults for example there are three
  built-in views and can show any 2d or 1d parameter can be shown in any
  you at any time. For example you can make a difference node, and show
  the grey scale difference mask in any view. When you hover the mouse
  over a view, it shows the favorite inputs. When a node is created that
  has 1D or 2D output, favorite is automatically created. You can have
  infinite number of input or result nodes.
* Have "Save Project" and "Save Movie".  If you exit without saving
  movie since modifying project, it gives a warning.  If you save a
  project, the dialog says how big of a flash drive you need (& lists
  which drives will work) by checkbox for "Include source files
  (required for using file on another computer, and also if files were
  opened directly from device such as camera or removable data storage)"

## Low-priority Features
* [ ] Motion Estimation
  * True ME (intra-frame): Get MSU ME (and other virtualdub plugins) working for
    multiple motion vectors ([not free for commercial
    use](https://www.compression.ru/video/motion_estimation/index_en.html))
  * Overall image motion: Create or use an existing [Phase
    correlation](https://en.wikipedia.org/wiki/Phase_correlation) filter
    for whole-image motion at least.
```
catch(std::exception& e) {
      qCritical() << "Exception thrown:" << e.what();
    }
```
* [ ] Change Speed
  - [ ] optional tweening (frame blending to create "in-between"
    frames if slower than original)
    - [ ] use motion estimation to warp?
  - [ ] optional merged frames for faster than original
    - [ ] use motion estimation for motion blur (so the effect isn't
      simply ghosting)
* [ ] Add a test system that builds ImageSequenceExamples from the blend
  file if Blender is installed on the system. For now, render manually
  (to /home/owner/Videos/ImageSequenceExamples on Poikilos' computer).
* [ ] Effects (see <http://randombio.com/linuxsetup141.html>)
* [ ] Load VirtualDub plugins, possibly as cscript using their
  sourcecode.
* [ ] Detect Light Sabers
  * auto masking behind objects
  * auto sound generation!
  * auto strike/collide generation
    * volume based on speed
    * hits with volume based on speed
      * different saber to saber & saber to target sound
        * as long as they're touching (fades into low electrical sound
    after initial hit)
      * allow manually adding saber-to-target hits
  * Set in-out points for saber
    * generate in-out sounds
* [ ] use G'MIC library for image processing (so GIMP plugins can be
  used).
  * example: Flowblade uses G'MIC, so does EKD (see http://gmic.eu/)
  * use GIMP HQRESIZE plugin (esp for resizing letterbox movies to 16:9
    anamorphic, esp DVD low-res mode mpegs created by Panasonic DVDR EP
    mode)
* [ ] Manipulate flv directly to avoid recompression (example: Try to
  rerender and combine zelda fan film from youtube, using curves from
  Sony Vegas [see vf project file])
* [ ] Have an expandable palette of sound effects, and a depth settings
  (negative for behind camera), then allow clicking to add 3D placement
  of sound
  * also allow animation
  * eventually create Blender export of speaker objects
  * allow optional facing direction (default is track viewer [always
    face camera])
* [ ] Seam Carving resize (possibly via an existing G'MIC plugin)
  example: [SeaMonster - Content-aware resizing FOSS (Seam
  Carving)](http://blogs.msdn.com/b/mswanson/archive/2007/10/23/seamonster-a-net-based-seam-carving-implementation.aspx)
* [ ] PAL-NTSC conversion (universal size/framerate converter) idea
  (or make VirtualDub plugin for this that writes output manually)
  * Make it universal: from any size/framerate to any size/framerate
  * Blend frames retroactively once there is enough data per frame (or
    do multiple at once if there is more data, if destination frame rate
    is higher than source)
  * Scale video as needed (is VirtualDub native scaling accessible via
    SDK??)
  * dump the frames into ffmpeg successively
  * test it with a PAL movie
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

## Up-res
super_res_image_save is based on super_res_image.py
  by Adrian Rosebrock (conformed to PEP8 by Jake "Poikilos" Gustafson)

[OpenCV Super Resolution with Deep
Learning](https://www.pyimagesearch.com/2020/11/09/opencv-super-resolution-with-deep-learning/)
by Adrian Rosebrock on November 9, 2020

I requested for the Wayback Machine to archive it:
- [snapshot](https://web.archive.org/web/20201109211028/https://www.pyimagesearch.com/2020/11/09/opencv-super-resolution-with-deep-learning/)
- [screen shot](https://web.archive.org/web/20201109211028/http://web.archive.org/screenshot/https://www.pyimagesearch.com/2020/11/09/opencv-super-resolution-with-deep-learning/)

more info is in development.

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


## Storage Method
Folder and file structure is as follows, where `<sequenceName>` is
sequence name (such as, if mygreatvideo0000.png is first frame,
`<sequenceName>` is mygreatvideo) and where the base folder (containing
`<sequenceName>` folder) is the folder where the images in an image
sequence are stored:

```
<sequenceName> [folder]
  rotocanvas.yml [not yet implemented]
  frames [folder]
    <frameNumber> [folder; only exists if frame is a keyframe]
      alpha.png [file where only alpha channel is used (and applied to background upon export)--
      alpha is stored separately so when background is edited, only edits are saved (to layer 0),
      reducing storage use; then alpha is applied]
      layers [folder]
        <layerNumber>.png
        <layerNumber>.yml [not yet implemented]
```
* an older considered method:
```
  Storage Format
  *.rotocanvas folder with L folder under it (Layers folder) where * is base name of sequence (excluding sequential numbering)
  folder for each keyframe containing layer files (whether hand-painted movement frame or actual interpolated keyframe)
    Each layer has a png file and a yml file
    YML file specifies:
    paint_type:  # can be:
      mask (use alpha as final alpha, and ignore colors)
      reveal (any transparent areas reveal background--provides a maximum alpha to all previous layers)
      plain (just paint--use normal alpha overlay)
    motion_type:  # can be:
      static (non-interpolated keyframe aka paint)
      interpolated (position[and rotation & scale eventually] interpolated until next)
    interpolation_type:  # can be:
      linear
```

## Backends
### Not Tried Yet
- [moviepy](https://github.com/Zulko/moviepy)
  - [Examples](https://zulko.github.io/moviepy/examples/examples.html)
- https://github.com/colour-science/colour
- <https://github.com/gtaylor/python-colormath>: "A python module that
  abstracts common color math operations. For example, converting from
  CIE L*a*b to XYZ, or from RGB to CMYK
  http://python-colormath.readthedocs.org"
- <https://github.com/mattrobenolt/colors.py>: "Convert colors between
  rgb, hsv, and hex, perform arithmetic, blend modes, and generate
  random colors within boundaries"
- VapourSynth
  - Python equivalent to AviSynth
  - has a cli tool for piping output into ffmpeg or other tools


## RCSource
- if `_first` is `None`, it is a single image.
  - Use `self.os.path.split(self._vidPathNoExt)[1]` not `_prefix` to
    generate a name (along with `self._ext`).
  - `self.getFrameName` will still work but will always return the same
    image file name.

## First-time Setup of This Repo
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

## Merging gimp-plugin-channel-tinker
The gimp-plugin-channel-tinker project was merged into and replaced by
rotocanvas (formerly pyrotocanvas).
- See the [changelog](changelog.md) entry for 2021-12-04.


