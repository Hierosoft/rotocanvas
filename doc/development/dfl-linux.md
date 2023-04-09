# DeepFaceLabs on Linux

## Install
Get a Linux binary release from:
https://github.com/nagadit/DeepFaceLab_Linux

Releases for other platforms are listed at: <https://github.com/iperov/DeepFaceLab#releases>

## Installing from git
(using pip)
Follow the steps, including:
*Make the necessary changes to requirements-cuda.txt!*

### Requirements
Install the following packages for your distro:
- `python3.9 opencv`
- fixes "Lapack (http://www.netlib.org/lapack/) sources not found." and other LAPACK and LAPACK_SRC  errors
  - Try to fix "libraries mkl_rt not found" as per <https://forums.developer.nvidia.com/t/pip-install-something-but-error-with-could-not-find-a-satisfies-version/66300/3>
  - Ubuntu/Debian: `libblas-dev liblapack-dev libatlas-base-dev gfortran`
    - cblas package is not known.
  - Fedora: `openblas-devel lapack-devel blas-devel libgfortran`
    - blas-devel provides CBLAS as per <https://rpmfind.net/linux/rpm2html/search.php?query=pkgconfig(cblas)>
      - as required: "both BLAS and CBLAS interfaces are needed for a properly optimized build of NumPy" -<https://numpy.org/doc/stable/user/building.html>
- install more OS packages (try changing devel to dev if not Fedora, and possibly remove lib from beginning):
  `ninja-build ccache libavcodec-free-devel libavformat-free-devel libavutil-free-devel libswscale-free-devel gstreamer1-plugins-base-devel libdc1394-devel openjpeg-devel jasper-devel vtk-devel python3-vtk`
  - erases a bunch of things and removes obs-studio and shotcut which use the regular ffmpeg and x264 (packaegs which conflict with free ones above):
    - ffmpeg-libs-5.1.2-9.fc37.x86_64 conflicts with libavcodec-free
      - package x264-0.164-3.20220602gitbaee400f.fc37.x86_64 requires ffmpeg-libs(x86-64), but none of the providers can be installed
    - ffmpeg-5.1.2-3.fc37.x86_64 conflicts with ffmpeg-free
    - and the following do not exist: `libavcodec-devel libavformat-devel libavutil-devel libswscale-devel` (only `-free-devel` packages exist for them)
    - so try:
      `ninja-build ccache libavcodec-free-devel libavformat-free-devel libavutil-free-devel libswscale-devel gstreamer1-plugins-base-devel libdc1394-devel openjpeg-devel jasper-devel vtk-devel python3-vtk`
      then:
      `sudo dnf install obs-studio --allowerasing`
      - removes libavcodec-free-devel libavformat-free-devel libavutil-free-devel libswresample-free-devel libswscale-free-devel
        - but try it anyway and see if keeping obs-studio is even possible to compile opencv :(
      - then `sudo dnf install shotcut`
  - gstreamer1-plugins-base-devel may differ on other distros (to provide gstreamer-base-devel)
  - gstreamer1-plugins-base-devel provides gstreamer-app gstreamer-riff, gstreamer-pbutils (which opencv build was saying were missing) apparently
    (See <https://pkgs.org/download/pkgconfig(gstreamer-pbutils-1.0)> etc) though there is also rust-gstreamer-pbutils
  - "VTK is an open-source software system for image processing, 3D
    graphics, volume rendering and visualization. VTK includes many
    advanced algorithms (e.g., surface reconstruction, implicit modeling,
    decimation) and rendering techniques (e.g., hardware-accelerated
    volume rendering, LOD control)."


### Clone the repo
```
git clone https://github.com/iperov/DeepFaceLab.git ~/Downloads/git/iperov/DeepFaceLab
```

### Change requirements-cuda.txt
```
tqdm
numpy==1.21.6
numexpr
h5py==3.2.1
opencv-python==4.4.0.46
ffmpeg-python==0.1.17
scikit-image==0.16.2
scipy==1.6.3
colorama
tensorflow-gpu==2.7.4
pyqt5
tf2onnx==1.9.3
```

### Setup the virtual environment
NOTE: numpy 1.19.3 has a precompiled wheel for python3.9 apparently. Unofficial package(s) discussed under "Didn't work" didn't work.
```
clear
PYTHON=python3.9
mkdir -p ~/.virtualenvs
# rm -Rf ~/.virtualenvs/deepfacelab
$PYTHON -m venv ~/.virtualenvs/deepfacelab
# PYTHON=~/.virtualenvs/deepfacelab/bin/python
PIP=~/.virtualenvs/deepfacelab/bin/pip
$PIP install --upgrade pip wheel setuptools
cd ~/Downloads/git/iperov/DeepFaceLab
$PIP install -r requirements-cuda.txt
```
