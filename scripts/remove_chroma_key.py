#!/usr/bin/env python3
"""Remove a chroma-key background from an image, producing a transparent PNG.

Standalone script — no dependency on external skill directories.
Requires: Pillow (pip install Pillow).

Usage:
    python remove_chroma_key.py --input sprite.png --output sprite_alpha.png --key-color "#ff00ff"
    python remove_chroma_key.py --input sprite.png --output sprite_alpha.png --key-color "#00ff00" --soft-matte
    python remove_chroma_key.py --input sprite.png --output sprite_alpha.png --key-color "#ff00ff" --despill --force
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERROR: This script requires Pillow and numpy.", file=sys.stderr)
    print("Install with:  pip install Pillow numpy", file=sys.stderr)
    sys.exit(1)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#rrggbb' or 'rrggbb' to (r, g, b)."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def remove_chroma_key(
    image: Image.Image,
    key_color: tuple[int, int, int],
    transparent_threshold: int = 45,
    opaque_threshold: int = 170,
    soft_matte: bool = False,
    despill: bool = False,
) -> Image.Image:
    """Remove the chroma-key background from an image.

    Parameters
    ----------
    image : PIL.Image
        Input RGBA or RGB image.
    key_color : (r, g, b)
        The chroma-key colour to remove.
    transparent_threshold : int
        Colour distance below this value → fully transparent.
    opaque_threshold : int
        Colour distance above this value → fully opaque.
    soft_matte : bool
        If True, create a smooth alpha gradient between the two thresholds.
    despill : bool
        If True, reduce chroma-key colour spill on semi-transparent edges.

    Returns
    -------
    PIL.Image
        RGBA image with the chroma-key removed.
    """
    img = image.convert("RGBA")
    arr = np.array(img, dtype=np.float64)
    kr, kg, kb = key_color

    # Colour distance per pixel (Euclidean in RGB space)
    dr = arr[:, :, 0] - kr
    dg = arr[:, :, 1] - kg
    db = arr[:, :, 2] - kb
    dist = np.sqrt(dr * dr + dg * dg + db * db)

    # Alpha channel
    if soft_matte:
        # Smooth gradient between thresholds
        alpha = np.clip(
            (dist - transparent_threshold) / (opaque_threshold - transparent_threshold),
            0.0, 1.0,
        )
    else:
        alpha = np.where(dist < transparent_threshold, 0.0, 1.0)

    alpha_u8 = (alpha * 255).astype(np.uint8)

    # Despill: reduce key-colour influence on edge pixels
    if despill:
        spill_strength = 1.0 - alpha  # strongest on semi-transparent pixels
        # Neutralise the key colour channel toward grey
        for ch_idx, key_val in enumerate([kr, kg, kb]):
            channel = arr[:, :, ch_idx]
            neutral = (channel + arr[:, :, (ch_idx + 1) % 3] + arr[:, :, (ch_idx + 2) % 3]) / 3.0
            arr[:, :, ch_idx] = channel + spill_strength * (neutral - channel) * 0.5

    result = np.zeros_like(arr, dtype=np.uint8)
    result[:, :, 0] = np.clip(arr[:, :, 0], 0, 255).astype(np.uint8)
    result[:, :, 1] = np.clip(arr[:, :, 1], 0, 255).astype(np.uint8)
    result[:, :, 2] = np.clip(arr[:, :, 2], 0, 255).astype(np.uint8)
    result[:, :, 3] = alpha_u8

    return Image.fromarray(result, "RGBA")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove chroma-key background from an image."
    )
    parser.add_argument("--input", "-i", required=True, type=Path,
                        help="Input image path.")
    parser.add_argument("--output", "-o", required=True, type=Path,
                        help="Output transparent PNG path.")
    parser.add_argument("--key-color", "-k", required=True,
                        help="Chroma key colour as hex, e.g. '#ff00ff' or '#00ff00'.")
    parser.add_argument("--transparent-threshold", type=int, default=45,
                        help="Distance below this → fully transparent (default 45).")
    parser.add_argument("--opaque-threshold", type=int, default=170,
                        help="Distance above this → fully opaque (default 170).")
    parser.add_argument("--soft-matte", action="store_true",
                        help="Use smooth alpha gradient instead of hard cutoff.")
    parser.add_argument("--despill", action="store_true",
                        help="Reduce chroma-key colour spill on edges.")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite output file if it exists.")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        return 1

    if args.output.exists() and not args.force:
        print(f"ERROR: Output file already exists: {args.output}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    key_rgb = hex_to_rgb(args.key_color)
    img = Image.open(args.input)

    print(f"Processing: {args.input} ({img.size[0]}x{img.size[1]})")
    print(f"Key colour: #{key_rgb[0]:02x}{key_rgb[1]:02x}{key_rgb[2]:02x}")

    result = remove_chroma_key(
        img, key_rgb,
        transparent_threshold=args.transparent_threshold,
        opaque_threshold=args.opaque_threshold,
        soft_matte=args.soft_matte,
        despill=args.despill,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, "PNG")
    print(f"Saved: {args.output}")

    # Quick stats
    arr = np.array(result)
    total_px = arr.shape[0] * arr.shape[1]
    transparent_px = int(np.sum(arr[:, :, 3] == 0))
    print(f"Transparent pixels: {transparent_px}/{total_px} ({transparent_px / total_px:.1%})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
