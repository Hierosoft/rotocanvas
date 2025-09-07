#!/usr/bin/env python3
import argparse
import sys
import os
import av
from av.filter import Graph
from PIL import Image
from wand.image import Image as WandImage


def soft_scale(img, width=128, height=128, add_noise=True,
               sigmoidal_contrast=(5, 50)):
    """
    Perform soft scaling on a PIL Image object.

    Args:
        img (PIL.Image.Image): Input image.
        width (int): Target width.
        height (int): Target height.
        add_noise (bool): Whether to add noise overlay.
        sigmoidal_contrast (tuple[int, int] | None): (contrast, midpoint%).
            If None, contrast is skipped.

    Returns:
        PIL.Image.Image: Processed output image.
    """
    img = img.convert("RGB").resize((width, height), Image.LANCZOS)

    if sigmoidal_contrast:
        contrast, midpoint = sigmoidal_contrast
        img = img.point(
            lambda i: 255 / (1 + pow(2.71828, -contrast *
                                     ((i - midpoint * 255 / 100) / 255)))
        )

    if add_noise:
        noise = Image.effect_noise((width, height), 64).convert("L")
        noise = noise.point(lambda p: 128 + (p - 128) * 0.45)
        img = Image.composite(img, noise.convert("RGB"), noise)

    return img


def soft_scale_file(input_path, output_path=None, width=128, height=128,
                    add_noise=True, sigmoidal_contrast=(5, 50),
                    scale_method="bicubic"):
    """
    File-based wrapper for soft_scale, using PyAV to decode and PIL to process.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError("Input not found: {}".format(input_path))

    name_no_ext, _ = os.path.splitext(input_path)
    if not output_path:
        output_path = "{}_diffuse.png".format(name_no_ext)

    # Decode via PyAV
    container = av.open(input_path)
    stream = container.streams.video[0]
    frame = next(container.decode(stream))
    img = frame.to_image()
    container.close()

    result = soft_scale(img, width=width, height=height,
                        add_noise=add_noise,
                        sigmoidal_contrast=sigmoidal_contrast)
    result.save(output_path)
    return output_path


def soft_scale_wand(img, width=128, height=128, add_noise=True,
                    sigmoidal_contrast=(5, 50), scale_method="triangle"):
    """
    Perform soft scaling on a Wand Image object.

    Args:
        img (wand.image.Image): Input image.
        width (int): Target width.
        height (int): Target height.
        add_noise (bool): Whether to add noise overlay.
        sigmoidal_contrast (tuple[int, int] | None): (contrast, midpoint%).
        scale_method (str): Wand resize filter name.

    Returns:
        wand.image.Image: Processed output image.
    """
    img = img.clone()
    img.transform_colorspace("gray")
    img.resize(width, height, filter=scale_method)

    if sigmoidal_contrast:
        contrast, midpoint = sigmoidal_contrast
        img.sigmoidal_contrast(True, contrast, midpoint)

    if add_noise:
        noise = WandImage(width=width, height=height,
                          pseudo="xc:gray50")
        noise.noise("uniform", attenuate=0.45)
        noise.level(0.35, 0.65)
        img.composite(noise, "overlay")

    return img


def soft_scale_wand_file(input_path, output_path=None, width=128, height=128,
                         add_noise=True, sigmoidal_contrast=(5, 50),
                         scale_method="triangle"):
    """
    File-based wrapper for soft_scale_wand, handling paths and saving.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError("Input not found: {}".format(input_path))

    name_no_ext, _ = os.path.splitext(input_path)
    if not output_path:
        output_path = "{}_diffuse.png".format(name_no_ext)

    with WandImage(filename=input_path) as img:
        result = soft_scale_wand(img, width=width, height=height,
                                 add_noise=add_noise,
                                 sigmoidal_contrast=sigmoidal_contrast,
                                 scale_method=scale_method)
        result.save(filename=output_path)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate diffuse and bump maps via PyAV or Wand scaling"
    )
    parser.add_argument("input", help="Input image file")
    parser.add_argument("--output-diffuse",
                        help="Output path for diffuse map")
    parser.add_argument("--diffuse-with-wand", action="store_true",
                        help="Use Wand for diffuse scaling")
    parser.add_argument("--width", type=int, default=128,
                        help="Output width (default 128)")
    parser.add_argument("--height", type=int, default=128,
                        help="Output height (default 128)")
    args = parser.parse_args()

    try:
        if args.diffuse_with_wand:
            soft_scale_wand_file(args.input, args.output_diffuse,
                                 width=args.width, height=args.height)
        else:
            soft_scale_file(args.input, args.output_diffuse,
                            width=args.width, height=args.height)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
