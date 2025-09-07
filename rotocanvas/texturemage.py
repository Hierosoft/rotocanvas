#!/usr/bin/env python3
"""
Soft scale image generator for diffuse and bump maps.

Generates two images:
- Diffuse: low-quality scaling, grayscale=False, noise overlay optional
- Bump: high-quality scaling, grayscale=True, noise overlay optional

Backends:
- Pillow (default)
- AV (PyAV)
- Wand (ImageMagick wrapper)

Usage:
    python soft_scale.py input.png
    python soft_scale.py input.png --diffuse-with-av --bump-with-wand
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image
import numpy as np

# Try imports
as_wand = False
try:
    from wand.image import Image as WandImage
    has_wand = True
except ModuleNotFoundError:
    has_wand = False

as_av = False
try:
    import av
    from av.filter import Graph
    has_av = True
except ModuleNotFoundError:
    has_av = False


# ----------------------
# Pillow backend
# ----------------------
def soft_scale(
    img: Image.Image,
    width: int = 128,
    height: int = 128,
    *,
    grayscale: bool = False,
    scale_method: str = "bicubic",
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
) -> Image.Image:
    """
    Pillow-based scaling with optional sigmoidal contrast and noise.

    Available scale methods:
      nearest, bilinear, bicubic, lanczos, box
    """
    method_map = {
        "nearest": Image.NEAREST,
        "bilinear": Image.BILINEAR,
        "bicubic": Image.BICUBIC,
        "lanczos": Image.LANCZOS,
        "box": Image.BOX,
    }
    method = method_map.get(scale_method.lower(), Image.BICUBIC)

    img = img.convert("RGB32")
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


def soft_scale_file(
    in_file: Path,
    out_file: Path,
    width: int = 128,
    height: int = 128,
    *,
    grayscale: bool = False,
    scale_method: str = "bicubic",
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
):
    img = Image.open(in_file)
    out_img = soft_scale(img, width, height,
                         grayscale=grayscale,
                         scale_method=scale_method,
                         add_noise=add_noise,
                         sigmoidal_contrast=sigmoidal_contrast)
    out_img.save(out_file, quality=100)


# ----------------------
# Wand backend
# ----------------------
def soft_scale_wand(
    img: Image.Image,
    width: int,
    height: int,
    *,
    grayscale: bool = False,
    scale_method: str = "lanczos",
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
) -> Image.Image:
    """
    Wand-based scaling with optional sigmoidal contrast and noise.

    Available scale methods:
      point, box, triangle, hermite, hanning, hamming, blackman,
      gaussian, quadratic, cubic, catrom, mitchell, sinc, lanczos,
      bessel, bartlett, lagrange
    """
    if not has_wand:
        raise RuntimeError("Wand requested but not available")

    with WandImage.from_array(np.array(img.convert("RGB"))) as wi:
        wi.resize(width, height, filter=scale_method)
        if sigmoidal_contrast is not None:
            c, m = sigmoidal_contrast
            wi.sigmoidal_contrast(c, m)
        if add_noise:
            wi_clone = WandImage(width=width, height=height, background='gray50')
            wi_clone.noise(alpha=False, channel='all', attenuate=0.45)
            wi_clone.level(0.35, 0.65)
            wi.composite(wi_clone, 0, 0, 'overlay')
        if grayscale:
            wi.type = 'grayscale'
        arr = wi.clone().export_pixels(channel_map='RGBA')
        img_out = Image.frombytes("RGBA", (wi.width, wi.height), arr)
        return img_out


def soft_scale_wand_file(in_file, out_file, **kwargs):
    img = Image.open(in_file)
    out_img = soft_scale_wand(img, **kwargs)
    out_img.save(out_file, quality=100)


# ----------------------
# AV backend
# ----------------------
def _av_filtergraph_process_single_frame(
    frame: "av.VideoFrame",
    width: int,
    height: int,
    *,
    scale_method: str = "nnedi",
    grayscale: bool = False,
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
) -> "av.VideoFrame":
    """
    Run AV filtergraph to scale, apply sigmoid, and optional noise overlay.

    Noise approximates IM recipe:
      gray50 base + attenuate + noise + level 35%-65% + overlay
    """
    graph = Graph()
    src = graph.add_buffer(template=frame)
    sink = graph.add("buffersink")
    prev = src

    # Scale
    if scale_method.lower() == "nnedi":
        nn = graph.add("nnedi", "field=0")
        prev.link_to(nn)
        prev = nn
        s = graph.add("scale", f"{width}:{height}")
        prev.link_to(s)
        prev = s
    else:
        s = graph.add("scale", f"{width}:{height}:flags={scale_method}")
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


def soft_scale_av(
    img: Image.Image,
    width: int = 128,
    height: int = 128,
    *,
    grayscale: bool = False,
    add_noise: bool = True,
    sigmoidal_contrast: Optional[Tuple[int, int]] = (5, 50),
    scale_method: str = "nnedi",
) -> Image.Image:
    """
    AV-based scaling with optional sigmoidal contrast and noise.

    Available scale methods:
      nnedi, bilinear, bicubic, lanczos
    """
    if not has_av:
        raise RuntimeError("PyAV requested but not available")
    frame = av.VideoFrame.from_image(img.convert("RGB"))
    out_frame = _av_filtergraph_process_single_frame(
        frame,
        width,
        height,
        scale_method=scale_method,
        grayscale=grayscale,
        add_noise=add_noise,
        sigmoidal_contrast=sigmoidal_contrast,
    )
    return out_frame.to_image()


def soft_scale_av_file(in_file, out_file, **kwargs):
    img = Image.open(in_file)
    out_img = soft_scale_av(img, **kwargs)
    out_img.save(out_file, quality=100)


# ----------------------
# Main
# ----------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate diffuse and bump maps\n\n"
        "Pillow (default):\nAvailable scale methods: nearest, bilinear, bicubic, "
        "lanczos, box\n\n"
        "AV:\nAvailable scale methods: nnedi, bilinear, bicubic, lanczos\n\n"
        "Wand:\nAvailable scale methods: point, box, triangle, hermite, hanning, "
        "hamming, blackman, gaussian, quadratic, cubic, catrom, mitchell, sinc, "
        "lanczos, bessel, bartlett, lagrange\n\n"
    )
    parser.add_argument("input", help="Input image file")
    parser.add_argument("--output-diffuse", help="Diffuse map output filename")
    parser.add_argument("--output-bump", help="Bump map output filename")
    parser.add_argument("--diffuse-with-wand", action="store_true")
    parser.add_argument("--diffuse-with-av", action="store_true")
    parser.add_argument("--bump-with-wand", action="store_true")
    parser.add_argument("--bump-with-av", action="store_true")
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--height", type=int, default=128)

    args = parser.parse_args()
    in_path = Path(args.input)
    name_no_ext = in_path.stem

    # MANUAL DEFAULTS
    if args.bump_with_wand:
        default_bump_method = "liquid_rescale"
    elif args.bump_with_av:
        default_bump_method = "nnedi"
    else:
        default_bump_method = "lanczos"

    if args.diffuse_with_wand:
        default_diffuse_method = "triangle"
    elif args.diffuse_with_av:
        default_diffuse_method = "nnedi"
    else:
        default_diffuse_method = "bicubic"

    out_diffuse = Path(args.output_diffuse or f"{name_no_ext}_diffuse.png")
    out_bump = Path(args.output_bump or f"{name_no_ext}_bump.png")

    diffuse_kwargs = dict(
        width=args.width,
        height=args.height,
        grayscale=False,
        add_noise=True,
        sigmoidal_contrast=(5, 50),
        scale_method=default_diffuse_method,
    )

    bump_kwargs = dict(
        width=args.width,
        height=args.height,
        grayscale=True,
        add_noise=True,
        sigmoidal_contrast=(5, 50),
        scale_method=default_bump_method,
    )

    # Diffuse backend
    if args.diffuse_with_wand:
        if not has_wand:
            print("Wand not available", file=sys.stderr)
            return 1
        soft_scale_wand_file(in_path, out_diffuse, **diffuse_kwargs)
    elif args.diffuse_with_av:
        if not has_av:
            print("PyAV not available", file=sys.stderr)
            return 1
        soft_scale_av_file(in_path, out_diffuse, **diffuse_kwargs)
    else:
        soft_scale_file(in_path, out_diffuse, **diffuse_kwargs)

    # Bump backend
    if args.bump_with_wand:
        if not has_wand:
            print("Wand not available", file=sys.stderr)
            return 1
        soft_scale_wand_file(in_path, out_bump, **bump_kwargs)
    elif args.bump_with_av:
        if not has_av:
            print("PyAV not available", file=sys.stderr)
            return 1
        soft_scale_av_file(in_path, out_bump, **bump_kwargs)
    else:
        soft_scale_file(in_path, out_bump, **bump_kwargs)

    print("Generated diffuse:", out_diffuse)
    print("Generated bump:", out_bump)
    return 0


if __name__ == "__main__":
    sys.exit(main())
