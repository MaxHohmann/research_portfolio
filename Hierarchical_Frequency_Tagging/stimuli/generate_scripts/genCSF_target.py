"""
This script generates target stimuli for a breaking Continuous Flash Suppression (bCFS)
experiment. Target stimuli are created by applying the same preprocessing pipeline as 
used for SWIFT stimuli, with the exception that no wavelet scrambling is applied to the 
original images. The resulting stimuli are saved both as NumPy arrays (.npy) for use in
PsychoPy and as PNG files for visualization.


Version:    1.1
Date:       28/03/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""


import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


# ----- parameters -----
frame_rate  = 120                   # refersh rate (Hz)
target_size = 300                   # size of frame array
category    = ["faces", "houses"]   # stimulus category


# ----- image root -----
STIM_FOLDER     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_FOLDER       = os.path.join(STIM_FOLDER, "original", "bCFS")     # input folder
OUT_FOLDER      = os.path.join(STIM_FOLDER, "bCFS_stim")            # output folder
PNG_FOLDER      = os.path.join(OUT_FOLDER, "PNG_files")             # folder for PNG files

os.makedirs(OUT_FOLDER, exist_ok=True)
os.makedirs(PNG_FOLDER, exist_ok=True)


# ----- helper functions -----

# -------------------------
# scale and crop Image
# -------------------------
def scale_Image(image, target_size):

    # current image size
    w, h = image.size

    # scale factor of smaller dimension
    scale = target_size / min(w, h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    # scale image
    image_scaled = image.resize((new_w, new_h), Image.BICUBIC)

    # center and crop
    left    = (new_w - target_size) // 2
    top     = (new_h - target_size) // 2
    image_cropped = image_scaled.crop((left, top, left + target_size, top + target_size))

    return image_cropped
# -------------------------


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
# generate bCFS Target Images
# -------------------------
# lopp for each image file within subfolder (face, house)
    
# files in subfolder
img_files = sorted(f for f in os.listdir(IN_FOLDER) if f.lower().endswith(".jpg"))

# ----- image loop -----
for img in img_files:

    print(f"image: {img}")

    # input path
    path_in = os.path.join(IN_FOLDER, img)

    # read image file
    stim_img = Image.open(path_in)

    # grey scale image
    stim_img = stim_img.convert("L")

    # scale image
    stim_img = scale_Image(stim_img, target_size)

    # convert to array
    stim_img = np.array(stim_img, dtype=np.float64)

    # apply gaussian filter
    stim_img = gaussian_filter(stim_img, sigma=0.5)

    # RMS contrast normalization
    stim_img = normalize_rms(stim_img, target_lum=127.5, target_rms=50)

    frame_lum   = np.mean(stim_img)
    frame_rms   = rms = np.sqrt(np.mean((stim_img - np.mean(stim_img))**2))
    print("\t------------------------------------------------")
    print("\tLUM across frames \t:", frame_lum)
    print("\tRMS across frames \t:", frame_rms)
    print("\t------------------------------------------------")


    # ----- save stimulus as array -----
    filename    = img.replace(".jpg", f".npy")
    out_path    = os.path.join(OUT_FOLDER, filename)

    np.save(out_path, stim_img)


    # ----- save stimulus as PNG file -----
    filename    = img.replace(".jpg", ".png")
    out_path    = os.path.join(PNG_FOLDER, filename)

    stim_png    = Image.fromarray(stim_img.astype(np.uint8))
    stim_png.save(out_path, "PNG")
# -------------------------

