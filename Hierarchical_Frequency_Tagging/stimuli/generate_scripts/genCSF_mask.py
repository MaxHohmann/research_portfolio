"""
This script generates the mask stimuli for a breaking Continuous Flash Suppression (bCFS)
experiment. It creates a sequence of CFS mask frames using additive circular patches. The
resulting sequence is saved both as NumPy array (.npy) for use in PsychoPy while singe 
frames are saved as PNG files for visualization.


Version:    1.0
Date:       27/04/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""


import os
import numpy as np
import random
from PIL import Image



# ----- parameters -----
np.random.seed(42)          # seed for reproducibility

frame_rate  = 120           # refersh rate (Hz)
target_size = 300           # size of frame array

PATCH_number    = 80                                                                # number of patches used in one frame
PATCH_radius    = [5,    10,   15,   20,   25,   30,   35,   40,   45,   50]        # patche class defined by radius
PATCH_prob      = [0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10]      # probability that a patch class is sampled
PATCH_col_min   = -0.8                                                              # minimum of color values used for patches
PATCH_col_max   = 0.8                                                               # maximum of color values used for patches


# ----- image root -----
STIM_FOLDER     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FOLDER      = os.path.join(STIM_FOLDER, "bCFS_stim")                            # output folder
PNG_FOLDER      = os.path.join(OUT_FOLDER, "PNG_files")                             # folder for PNG files

os.makedirs(OUT_FOLDER, exist_ok=True)
os.makedirs(PNG_FOLDER, exist_ok=True)



# # ----- helper functions -----

# -------------------------
# RMS contrast normalization
# -------------------------
def normalize_rms(image, target_lum, target_rms):
    image = image.astype(np.float64)

    # substract mean
    image = image - np.mean(image)

    # get RMS contrast
    rms = np.sqrt(np.mean(image**2))

    if rms > 0:
        image = image * (target_rms / rms)

    # add target mean
    image_norm = image + target_lum

    # clip image values
    image_norm = np.clip(image_norm, 0, 255)

    return image_norm
# -------------------------



# -------------------------
# Main Script
# -------------------------
if __name__ == "__main__":


    # frames per cycle
    nbframes = int(frame_rate / 1)

    # initiate sequence
    mask_seq = np.zeros((nbframes, target_size, target_size))


    # ----- generate frames -----
    for f in range(nbframes):

        # initiate frame array
        frame   = np.zeros((target_size, target_size))

        # get coodinates
        cx_img  = cy_img = target_size // 2
        y, x    = np.ogrid[:target_size, :target_size]


        # ----- generate patches -----
        for _ in range(PATCH_number):

            # sample patch parameters
            cr = np.random.choice(PATCH_radius, p = PATCH_prob)

            cx = random.randint(0, target_size - 1)
            cy = random.randint(0, target_size - 1)

            color = random.uniform(PATCH_col_min, PATCH_col_max)


            # get coordinates of circle
            dx = x - cx + 0.5
            dy = y - cy + 0.5

            dist = np.sqrt(dx**2 + dy**2)
            patch = dist <= cr
            
            
            # assign color to patch
            frame[patch] = color


        # assign frames to sequence
        mask_seq[f,:,:] = frame


    # ----- normalization -----
    for i in range(mask_seq.shape[0]):
        
        mask_seq[i] = normalize_rms(mask_seq[i], target_lum=127.5, target_rms=50)

    # get frame parameters for control
    frame_lum   = [np.mean(f) for f in mask_seq]
    frame_rms   = [np.sqrt(np.mean((f - np.mean(f))**2)) for f in mask_seq]

    print("\t------------------------------------------------")
    print("\tLUM across frames     \t:", np.mean(frame_lum))
    print("\tStd Lum across frames \t:", np.std(frame_lum))
    print("\tRMS across frames     \t:", np.mean(frame_rms))
    print("\tStd RMS across frames \t:", np.std(frame_rms))
    print("\t------------------------------------------------")


    # ----- save stimulus as array -----
    filename    = "CFS_mask.npy"
    out_path    = os.path.join(OUT_FOLDER, filename)

    np.save(out_path, mask_seq)


    # ----- save sequence frames as PNG file -----
    png_frames = [0, 15, 30, 45, 60, 75]    # frame index

    # time of each frame 
    png_labels = [int((f / 3) * 25) for f in png_frames]

    # save frames (
    for i, idx in enumerate(png_frames):

        # define filename
        filename = f"CFS_maks_frame_{png_labels[i]}ms.png"
        out_path = os.path.join(PNG_FOLDER, filename)

        stim_png = Image.fromarray(mask_seq[idx].astype(np.uint8))
        stim_png.save(out_path, "PNG")

    print(f"\tSAVED FRAMES")
    print("\t------------------------------------------------")

