"""
This function generates a circular ring containing black and white segments.
The ring can contain multiple numbers of concentric rings with segments in
alternating color (checkerboard pattern). Stimulus is saved as separate PNG
file.

Version:    2.0
Date:       22/04/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""



import numpy as np
from PIL import Image
import os


# -------------------------
# genrate fusion ring
# -------------------------
def createRingArray(size, radius, width, n_rings, n_segments):


    # define colors for checkerboard pattern
    color_dark  = 64    # dark grey (-0.5)  (32 => -0.75)
    color_light = 255   # white (1.00)      (242 => 0.9 // 230 => 0.8 // 223 => 0.75)

    # center of image
    cx = cy = size // 2

    # get coordinates of circle
    y, x = np.ogrid[:size, :size]
    dx = x - cx + 0.5
    dy = y - cy + 0.5

    dist = np.sqrt(dx**2 + dy**2)

    # get angles relative to center
    angles          = (np.arctan2(dy, dx) + 2*np.pi) % (2*np.pi)
    seg_angle       = 2 * np.pi / n_segments
    ring_thickness  = width / n_rings

    # initiate image array (RGBA)
    rgba_arr = np.zeros((size, size, 4), dtype=np.uint8)

    # loop over ring layer
    for ring_idx in range(n_rings):

        r_inner = radius + ring_idx * ring_thickness
        r_outer = r_inner + ring_thickness

        ring_mask = (dist >= r_inner) & (dist <= r_outer)

        # loop over segments
        for seg in range(n_segments):

            ang_start   = seg * seg_angle
            ang_end     = (seg + 1) * seg_angle

            seg_mask    = (angles >= ang_start) & (angles < ang_end)
            mask        = ring_mask & seg_mask

            # checkerboard pattern
            dark = (ring_idx + seg) % 2 == 0

            # assign color to segments
            color = color_dark if dark else color_light

            rgba_arr[mask, 0:3] = color
            rgba_arr[mask, 3] = 255


    return rgba_arr 
# -------------------------



# -------------------------
# Main Script
# -------------------------
if __name__ == "__main__":

    # parameters
    scale   = 1             # used for higher resolution
    radius  = 100 * scale
    width   = 25 * scale
    size    = (radius + width) * 2


    # create ring array
    ring_arr = createRingArray(
        size        = size,
        radius      = radius,
        width       = width,
        n_rings     = 2,
        n_segments  = 24
    )


    # save image
    STIM_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path    = os.path.join(STIM_FOLDER, "fusion_ring.png")

    # convert array to image
    Image.fromarray(ring_arr).save(out_path, "PNG")

    print(f"SAVED FUSION RING SAVED\t: {out_path}")

