
"""
Generate Cropped Directional Cue Stimuli
=========================================

Creates two transparent RGBA PNG images:
    - cue_left.png
    - cue_right.png

The images are cropped to the arrow bounding box rather than
using the full display resolution.

Arrow dimensions:
    Width  : 2 degrees of visual angle
    Height : 1 degree of visual angle

Supersampling is used to produce smooth arrow edges.

Date   : 27/10/2026
Author : Maximilian Hohmann
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


# ======================================================
# SETTINGS
# ======================================================

# Display geometry
DISPLAY_WIDTH_CM = 59.7
VIEWING_DISTANCE_CM = 57.0
DISPLAY_WIDTH_PX = 2560

# Desired arrow size in degrees of visual angle
ARROW_WIDTH_DVA = 4.0
ARROW_HEIGHT_DVA = 4.0

# Arrow color: RGB values from 0 to 255
ARROW_RGB = (0, 0, 255)  # White

# Internal rendering resolution multiplier
SUPERSAMPLING_FACTOR = 10

# Arrow shape proportions
HEAD_LENGTH_RATIO = 0.6
HEAD_HALF_HEIGHT_RATIO = 0.6
SHAFT_HALF_HEIGHT_RATIO = 0.3

# Output directory
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "CUE_stim"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ======================================================
# VISUAL ANGLE TO PIXELS
# ======================================================

def dva_to_pixels(dva):
    """Convert degrees of visual angle to display pixels."""

    size_cm = (
        2.0
        * VIEWING_DISTANCE_CM
        * np.tan(np.deg2rad(dva / 2.0))
    )

    return round(
        size_cm
        / DISPLAY_WIDTH_CM
        * DISPLAY_WIDTH_PX
    )


ARROW_WIDTH_PX = dva_to_pixels(ARROW_WIDTH_DVA)
ARROW_HEIGHT_PX = dva_to_pixels(ARROW_HEIGHT_DVA)


# ======================================================
# CREATE ARROW POLYGON
# ======================================================

def get_arrow_vertices(width_px, height_px, direction):
    """
    Create a filled arrow polygon inside a cropped canvas.
    Coordinates are specified in the final image's pixels.
    """

    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'.")

    cx = (width_px - 1) / 2.0
    cy = (height_px - 1) / 2.0

    half_w = width_px / 2.0
    half_h = height_px / 2.0

    head_base_x = half_w - width_px * HEAD_LENGTH_RATIO
    head_half_h = half_h * HEAD_HALF_HEIGHT_RATIO
    shaft_half_h = half_h * SHAFT_HALF_HEIGHT_RATIO

    # Right-pointing arrow, defined clockwise
    vertices = [
        (cx - half_w, cy - shaft_half_h),
        (cx - head_base_x, cy - shaft_half_h),
        (cx - head_base_x, cy - head_half_h),
        (cx + half_w, cy),
        (cx - head_base_x, cy + head_half_h),
        (cx - head_base_x, cy + shaft_half_h),
        (cx - half_w, cy + shaft_half_h),
    ]

    if direction == "left":
        vertices = [(2 * cx - x, y) for x, y in vertices]

    return vertices


# ======================================================
# RENDER AND SAVE CROPPED CUE
# ======================================================

def create_cue(direction, filename):
    """
    Render the arrow at high resolution and save a cropped,
    transparent PNG at the target dimensions.
    """

    scale = SUPERSAMPLING_FACTOR

    # Render only the arrow's bounding box at high resolution
    high_width = ARROW_WIDTH_PX * scale
    high_height = ARROW_HEIGHT_PX * scale

    image = Image.new(
        "RGBA",
        (high_width, high_height),
        (0, 0, 0, 0),
    )

    vertices = get_arrow_vertices(
        width_px=high_width,
        height_px=high_height,
        direction=direction,
    )

    draw = ImageDraw.Draw(image)
    draw.polygon(
        vertices,
        fill=(*ARROW_RGB, 255),
    )

    # Premultiplied-alpha resizing prevents colored halos
    image = image.convert("RGBa")
    image = image.resize(
        (ARROW_WIDTH_PX, ARROW_HEIGHT_PX),
        Image.Resampling.LANCZOS,
    )
    image = image.convert("RGBA")

    output_path = OUT_DIR / filename
    image.save(output_path)

    print(
        f"Saved {filename}: "
        f"{ARROW_WIDTH_PX} x {ARROW_HEIGHT_PX} px"
    )


# ======================================================
# GENERATE CUES
# ======================================================

create_cue("left", "cue_left.png")
create_cue("right", "cue_right.png")


# ======================================================
# SUMMARY
# ======================================================

print("\nCue stimuli generated.")
print(f"Output directory: {OUT_DIR}")
print(f"Arrow color RGB: {ARROW_RGB}")
print(
    f"Arrow size: {ARROW_WIDTH_DVA:.1f} x "
    f"{ARROW_HEIGHT_DVA:.1f} dva"
)
print(f"Supersampling: {SUPERSAMPLING_FACTOR}x")
print("Background: transparent")
