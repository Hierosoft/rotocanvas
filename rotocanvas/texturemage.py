#!/usr/bin/env python3
"""
Fake detail generator for pixel art textures.

Generates two images:
- Diffuse: low-quality scaling, grayscale=False, noise overlay optional
- Bump: high-quality scaling, grayscale=True, noise overlay optional

Backends:
- Pillow (default)
- AV (PyAV)
- Wand (ImageMagick wrapper)

Usage:
    python filtered_resample.py input.png
    python filtered_resample.py input.png --diffuse-with-av --bump-with-wand
"""
# TODO: Consider using Image.ANTIALIAS if scaling down (input>128)
from __future__ import print_function
from __future__ import division
import argparse
from collections import OrderedDict
import os
import numpy as np
import shutil
import sys
import tempfile

from argparse import RawTextHelpFormatter
from pathlib import Path
from PIL import Image
from typing import Optional, Tuple

if sys.version_info.major < 3:
    ModuleNotFoundError = ImportError
    from hierosoft.logging2 import getLogger
    # ^ Requires installing the https://github.com/Hierosoft/hierosoft.git
    #   Python module. To avoid this use Python 3.
else:
    from logging import getLogger

# Try imports
has_wand = False
try:
    import wand.image
    from wand.image import Image as WandImage
    has_wand = True
except ModuleNotFoundError:
    pass

has_av = False
try:
    import av
    from av.filter import Graph
    has_av = True
except ModuleNotFoundError:
    pass

logger = getLogger(__name__)


def preprocess(in_file: Path, tile_and_shift: bool) -> Path:
    """
    Convert an input image to RGB32 and save as a temporary PNG.

    Args:
        in_file (Path): The original or preprocessed image (typically
            preprocessed to scale seamless textures without introducing
            edge artifacts, but RGBA is forced here either way to avoid
            jagged edges when scaling non-truecolor images, so either is
            technically acceptable).
        tile_and_shift (bool): double the resolution by tiling, and
            shift by half of original size on each dimension to prevent
            resampling (on a later step) from distorting edges (making them
            non-seamless).

    Returns:
        Path: the path to the temporary file.
    """
    img = Image.open(in_file).convert("RGBA")  # RGBA = 32bit
    temp_dir = tempfile.mkdtemp()
    if tile_and_shift:
        temp_file = Path(temp_dir) / f"{in_file.stem}.truecolor-tiled-shifted.tmp.png"
        img2x = Image.new("RGBA", (img.width*2, img.height*2))
        middle = (
            img.width//2,
            img.height//2,
        )
        # Perform seamless shift (but also tiled in this case, so paste
        #   it 9 times, wrapped, so the untouched image lands in middle;
        #   left of first col and right of last col are automatically
        #   cropped by Pillow).
        # * 1st row (tops are automatically cropped off by Pillow):
        img2x.paste(img, (middle[0]-img.width, middle[1]-img.height))
        img2x.paste(img, (middle[0],           middle[1]-img.height))
        img2x.paste(img, (middle[0]+img.width, middle[1]-img.height))
        # * 2nd row (only sides of 1st & last are cropped):
        img2x.paste(img, (middle[0]-img.width, middle[1]))
        img2x.paste(img, (middle[0],           middle[1]))
        img2x.paste(img, (middle[0]+img.width, middle[1]))
        # * 3rd row (bottoms are automatically cropped off by Pillow):
        img2x.paste(img, (middle[0]-img.width, middle[1]+img.height))
        img2x.paste(img, (middle[0],           middle[1]+img.height))
        img2x.paste(img, (middle[0]+img.width, middle[1]+img.height))
        img2x.save(temp_file)
        return temp_file
    temp_file = Path(temp_dir) / f"{in_file.stem}.truecolor.tmp.png"
    img.save(temp_file)
    return temp_file


def postprocess(processed_file: Path, destination_file: Path,
                untile_and_unshift: bool):
    """Transfer the resampled image to the destination.

    Args:
        processed_file (Path): The resampled file path.
        destination_file (Path): The file to write/overwrite.
        untile_and_unshift (bool): Recover the original image from the
            tiled image (See tile_and_shift in preprocess).
    """
    img = Image.open(processed_file).convert("RGBA")  # RGBA = 32bit
    if untile_and_unshift:
        imgHalf = Image.new("RGBA", (img.width//2, img.height//2))
        # 1/4 is position of old image, since old image is tiled twice
        #   in each dimension (and shifted by half of original size) by
        #   preprocess if tile_and_shift was True:
        oldImgPos = (
            img.width//4,
            img.height//4,
        )
        # Use negative pos to crop top left (bottom left is also cropped
        #   automatically by Pillow since size above is half):
        imgHalf.paste(img, (-oldImgPos[0], -oldImgPos[1]))
        imgHalf.save(destination_file)
    else:
        if os.path.isfile(destination_file):
            os.remove(destination_file)
        shutil.move(processed_file, destination_file)


def pil_resampling_dict(to_lower=True):
    # if hasattr(Image, 'Resampling'):
    results = OrderedDict()
    if hasattr(Image, 'Resampling'):
        # Pillow >= 9.1.0
        for k, v in Image.Resampling.__dict__.items():
            if k != k.upper():
                continue
            results[k.lower() if to_lower else k] = v
        return results
    # Pillow < 9.1.0
    reserved = ('ADAPTIVE', 'AFFINE', 'DEFAULT_STRATEGY', 'EXTENT',
                'FASTOCTREE', 'FILTERED', 'FIXED', 'FLIP_LEFT_RIGHT',
                'FLIP_TOP_BOTTOM', 'FLOYDSTEINBERG', 'HUFFMAN_ONLY',
                'LIBIMAGEQUANT', 'MAXCOVERAGE', 'MAX_IMAGE_PIXELS',
                'MEDIANCUT', 'MESH', 'NONE', 'ORDERED', 'PERSPECTIVE', 'QUAD',
                'RASTERIZE', 'RLE', 'ROTATE_180', 'ROTATE_270', 'ROTATE_90',
                'TRANSPOSE', 'TRANSVERSE', 'TYPE_CHECKING',
                'WARN_POSSIBLE_FORMATS', 'WEB')
    for key in dir(Image):
        if key != key.upper():
            # not a constant
            continue
        if not isinstance(getattr(Image, key), int):
            # not (Pillow<9.1) resampling constant
            continue
        if key in reserved:
            # Some other non-resampling (Pillow<9.1) constant
            continue
        results[key.lower() if to_lower else key] = getattr(Image, key)
    return results


def pil_resampling_keys_str(to_lower=True):
    return ", ".join(pil_resampling_dict(to_lower=to_lower).keys())


# ----------------------
# Pillow backend
# ----------------------
def filtered_resample(
    img: Image.Image,
    width: int = 128,
    height: int = 128,
    *,
    grayscale: bool = False,
    resample_method: str = "bicubic",
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
) -> Image.Image:
    """
    Pillow-based scaling with optional sigmoidal contrast and noise.
    Newer versions may have additional scaling methods
    such as "hamming".

    Available resampling methods:
      nearest, bilinear, bicubic, lanczos, box
    """
    # method_map = {
    #     "nearest": Image.NEAREST,
    #     "bilinear": Image.BILINEAR,
    #     "bicubic": Image.BICUBIC,
    #     "lanczos": Image.LANCZOS,
    #     "box": Image.BOX,
    # }
    method_map = pil_resampling_dict()
    method = method_map.get(resample_method.lower())
    # , Image.BICUBIC
    if method is None:
        raise ValueError(
            "Resample method {} is not available in Pillow. Expected: {}"
            .format(repr(resample_method), pil_resampling_keys_str())
        )
    img = img.convert("RGBA")
    img = img.resize((width, height), method)

    if sigmoidal_contrast is not None:
        c, m = sigmoidal_contrast
        factor = c / 5.0
        midpoint = m / 100.0
        lut = [int(255 / (1 + np.exp(-factor*(i/255.0-midpoint)))) for i in range(256)]
        img = img.point(lut * 4)  # 32bit image: 4 channels

    if add_noise:
        arr = np.array(img).astype(np.float32)
        noise = np.random.uniform(-23, 23, arr.shape)  # ~0.45*50
        arr += noise
        arr = np.clip(arr, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8), "RGBA")

    if grayscale:
        img = img.convert("L")

    return img


def filtered_resample_file(
    in_file: Path,
    out_file: Path,
    width: int = 128,
    height: int = 128,
    *,
    grayscale: bool = False,
    resample_method: str = "bicubic",
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
):
    img = Image.open(in_file)
    out_img = filtered_resample(img, width, height,
                         grayscale=grayscale,
                         resample_method=resample_method,
                         add_noise=add_noise,
                         sigmoidal_contrast=sigmoidal_contrast)
    out_img.save(out_file, quality=100)


# ----------------------
# Wand backend
# ----------------------
def filtered_resample_wand(
    img: Image.Image,
    width: int,
    height: int,
    *,
    grayscale: bool = False,
    resample_method: str = "lanczos",
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
) -> Image.Image:
    """
    Wand-based scaling with optional sigmoidal contrast and noise.
    NOTE: liquid_rescale is not available in wand-git as of 2025-09-06,
    but it has a very poor outcome on low-res images (16x16 stone
    texture ends up looking like a waterfall).

    Args:
        sigmoidal_contrast (tuple[int]): Tuple of strength, midpoint.
            Defaults to (5, 50).

    Available resampling methods:
      point, box, triangle, hermite, hanning, hamming, blackman,
      gaussian, quadratic, cubic, catrom, mitchell, sinc, lanczos,
      bessel, bartlett, lagrange
    """
    # TODO: Make PR to add bessel to wand
    if not has_wand:
        raise RuntimeError("Wand requested but not available")
    assert resample_method in wand.image.FILTER_TYPES, \
        "{} not in wand image FILTER_TYPES: {}".format(repr(resample_method),
                                                       wand.image.FILTER_TYPES)
    with WandImage.from_array(np.array(img.convert("RGB"))) as wi:
        wi.resize(width, height, filter=resample_method)
        if sigmoidal_contrast is not None:
            strength, midpoint = sigmoidal_contrast
            wi.sigmoidal_contrast(False, strength, midpoint)
        if add_noise:
            wi_clone = WandImage(width=width, height=height, background='gray50')
            wi_clone.noise(channel='all', attenuate=0.45)
            wi_clone.level(0.35, 0.65)
            wi.composite(wi_clone, 0, 0, 'overlay')
        if grayscale:
            wi.type = 'grayscale'
        arr = wi.clone().export_pixels(channel_map='RGBA')  # returns list
        # So convert to bytes:
        img_out = Image.frombytes("RGBA", (wi.width, wi.height), bytes(arr))
        return img_out


def split_multiline_csv(paragraph):
    return (paragraph.replace("\n", "").replace("\r", "").replace(" ", "")
            .strip().split(","))


resampling_heading = "Available resampling methods:"
wand_doc_opening, wand_resample_methods = \
    filtered_resample_wand.__doc__.split(resampling_heading)

if has_wand:
    wand_resample_methods = ", ".join(wand.image.FILTER_TYPES)
    filtered_resample_wand.__doc__ = (
        wand_doc_opening + resampling_heading + " " + wand_resample_methods
    )


def filtered_resample_wand_file(in_file, out_file, **kwargs):
    img = Image.open(in_file)
    out_img = filtered_resample_wand(img, **kwargs)
    out_img.save(out_file, quality=100)


# ----------------------
# AV backend
# ----------------------
def _av_filtergraph_process_single_frame(
    frame: "av.VideoFrame",
    width: int,
    height: int,
    *,
    resample_method: str = "nnedi",
    grayscale: bool = False,
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
) -> "av.VideoFrame":
    """
    Run AV filtergraph to resample, apply sigmoid, and optional noise overlay.

    Noise approximates IM recipe:
      gray50 base + attenuate + noise + level 35%-65% + overlay
    """
    graph = Graph()
    src = graph.add_buffer(template=frame)
    sink = graph.add("buffersink")
    prev = src

    # Resample
    if resample_method.lower() == "nnedi":
        nn = graph.add("nnedi", "field=0")
        prev.link_to(nn)
        prev = nn
        s = graph.add("scale", f"{width}:{height}")
        prev.link_to(s)
        prev = s
    else:
        s = graph.add("scale", f"{width}:{height}:flags={resample_method}")
        prev.link_to(s)
        prev = s

    # Sigmoidal contrast
    if sigmoidal_contrast is not None:
        c, m = sigmoidal_contrast
        sigmoid = graph.add("sigmoid", f"contrast={c}:midpoint={m/100.0}")
        prev.link_to(sigmoid)
        prev = sigmoid

    # Noise overlay
    if add_noise:
        noise_src = graph.add("color", f"c=gray50:size={width}x{height}")
        n = graph.add("noise", "alls=10:allf=u")
        noise_src.link_to(n)
        lut = graph.add("lut", "y=clipval((val-90)*255/64+90,90,166)")
        n.link_to(lut)
        blend = graph.add("blend", "all_mode=overlay:all_opacity=1.0")
        prev.link_to(blend)
        lut.link_to(blend)
        prev = blend

    if grayscale:
        grayf = graph.add("format", "gray")
        prev.link_to(grayf)
        prev = grayf

    prev.link_to(sink)
    graph.configure()
    graph.push(frame)
    return graph.pull()


def filtered_resample_av(
    img: Image.Image,
    width: int = 128,
    height: int = 128,
    *,
    grayscale: bool = False,
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
    resample_method: str = "nnedi",
) -> Image.Image:
    """
    AV-based scaling with optional sigmoidal contrast and noise.

    Available resampling methods:
      nnedi, bilinear, bicubic, lanczos
    """
    if not has_av:
        raise RuntimeError("PyAV requested but not available")
    frame = av.VideoFrame.from_image(img.convert("RGB"))
    out_frame = _av_filtergraph_process_single_frame(
        frame,
        width,
        height,
        resample_method=resample_method,
        grayscale=grayscale,
        add_noise=add_noise,
        sigmoidal_contrast=sigmoidal_contrast,
    )
    return out_frame.to_image()


def filtered_resample_av_file(in_file, out_file, **kwargs):
    img = Image.open(in_file)
    out_img = filtered_resample_av(img, **kwargs)
    out_img.save(out_file, quality=100)


# ----------------------
# Main
# ----------------------
def main():
    seamless = True
    parser = argparse.ArgumentParser(
        description="Generate diffuse and bump maps\n\n"
        "Available resampling methods:\n"
        "* Pillow (default): {}\n"
        "* AV: nnedi (default for bump), bilinear, bicubic, lanczos\n"
        "* Wand: Available resampling methods: {}\n\n"
        .format(pil_resampling_keys_str(), wand_resample_methods),
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("input", help="Input image file")
    parser.add_argument("--output-diffuse", help="Diffuse map output filename")
    parser.add_argument("--output-bump", help="Bump map output filename")
    parser.add_argument("--diffuse-method", help="Diffuse map scaling method")
    parser.add_argument("--bump-method", help="Bump map scaling method")
    parser.add_argument("--diffuse-with-pil", action="store_true")
    parser.add_argument("--diffuse-with-av", action="store_true")
    parser.add_argument("--bump-with-pil", action="store_true")
    parser.add_argument("--bump-with-av", action="store_true")
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--height", type=int, default=128)

    args = parser.parse_args()
    in_path = Path(args.input)
    name_no_ext = in_path.stem

    # MANUAL DEFAULTS
    if args.bump_with_pil:
        default_bump_method = "lanczos"
    elif args.bump_with_av:
        default_bump_method = "nnedi"
    else:
        default_bump_method = "gaussian"

    if args.diffuse_with_pil:
        default_diffuse_method = "bicubic"
    elif args.diffuse_with_av:
        default_diffuse_method = "nnedi"
    else:
        default_diffuse_method = "triangle"

    bump_method = args.bump_method or default_bump_method
    diffuse_method = args.diffuse_method or default_diffuse_method
    logger.info("bump_method={}".format(bump_method))
    logger.info("diffuse_method={}".format(diffuse_method))

    diffuse_name = Path(args.output_diffuse or f"{name_no_ext}_diffuse.png")
    bump_name = Path(args.output_bump or f"{name_no_ext}_bump.png")
    diffuse_tmp_name = Path(args.output_diffuse or f"{name_no_ext}_diffuse-tiled-shifted-resampled.tmp.png")
    bump_tmp_name = Path(args.output_bump or f"{name_no_ext}_bump-tiled-shifted-resampled.tmp.png")
    destination_dir = in_path.parent
    out_tmp_diffuse = destination_dir / diffuse_tmp_name
    out_tmp_bump = destination_dir / bump_tmp_name
    out_diffuse = destination_dir / diffuse_name
    out_bump = destination_dir / bump_name
    temp_width = args.width * 2 if seamless else args.width
    temp_height = args.height * 2 if seamless else args.height
    diffuse_kwargs = dict(
        width=temp_width,
        height=temp_height,
        grayscale=False,
        add_noise=True,
        sigmoidal_contrast=None,
        resample_method=diffuse_method,
    )

    bump_kwargs = dict(
        width=temp_width,
        height=temp_height,
        grayscale=True,
        add_noise=True,
        resample_method=bump_method,
        # sigmoidal_contrast=(5, 50),  # make waves round (fix pyramid
        #   artifacts caused by triangle a.k.a. linear resampling)
        sigmoidal_contrast=None,
    )

    # Convert to RGB32 temp file
    preprocessed_file = preprocess(in_path, seamless)

    # Diffuse backend
    if args.diffuse_with_pil:
        filtered_resample_file(preprocessed_file, out_tmp_diffuse, **diffuse_kwargs)
    elif args.diffuse_with_av:
        if not has_av:
            logger.fatal("PyAV not available")
            return 1
        filtered_resample_av_file(preprocessed_file, out_tmp_diffuse, **diffuse_kwargs)
    else:
        if not has_wand:
            logger.fatal("Wand not available")
            return 1
        filtered_resample_wand_file(preprocessed_file, out_tmp_diffuse, **diffuse_kwargs)

    # Bump backend
    if args.bump_with_pil:
        filtered_resample_file(preprocessed_file, out_tmp_bump, **bump_kwargs)
    elif args.bump_with_av:
        logger.warning("AV is WIP (probably will not look right).")
        if not has_av:
            logger.fatal("PyAV not available")
            return 1
        filtered_resample_av_file(preprocessed_file, out_tmp_bump, **bump_kwargs)
    else:
        if not has_wand:
            logger.fatal("Wand not available")
            return 1
        filtered_resample_wand_file(preprocessed_file, out_tmp_bump, **bump_kwargs)
    postprocess(out_tmp_diffuse, out_diffuse, seamless)
    postprocess(out_tmp_bump, out_bump, seamless)
    # Clean up temporary file/directory
    shutil.rmtree(preprocessed_file.parent)

    print("Generated diffuse:", out_diffuse)
    print("Generated bump:", out_bump)
    return 0


if __name__ == "__main__":
    sys.exit(main())
