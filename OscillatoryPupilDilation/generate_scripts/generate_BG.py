"""
Generate Horizontal Grayscale Background Stimulus

this scripts generate a horizontal grayscale background stimuli
with a central intensity profile. The transition area is defines
within 10 dva centered horizontally on the display. The display 
anywhere left (< -5 dva) to the transition area is black [0], 
and anywhere right (> 5 dva) is white.

The transition area is defined as a logistic sigmoid function, 
with nominal 10-90% transition widths (W10-90) of 8 dva. The 
transition area is computed across the finite central pixels
and is normalized to digital intensity values between 0 and 1.
The resulting values are converted to 8-bit grayscale values
(0-255) and saved as PNG images.

The logistic function is defined as:

    I(x) = 1 / (1 + exp(-a * x))

where x is horizontal position (in dva) and a controls the 
steepness of the transition.

For an unnormalized logistic function, the nominal 10-90%
transition width is:

    W10-90 = 2 * ln(9) / a

Therefore:

    a = 2 * ln(9) / W10-90

Because the function is evaluated over a finite region and
normalized to its sampled minimum and maximum, the realized
10-90% width may differ from the nominal parameter.

The background stimulus is saved to a directory named 
'./BG_stim/' next to this script.


Date    :   27/10/2026
Author  :   Maximilian Hohmann
            mhohmann@dpz.eu
            maximilian.hohmann@stud.uni-goettingen.de
"""



# -----------------------------------------------
# SETUP
# -----------------------------------------------

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw



# -----------------------------------------------
# SETTINGS
# -----------------------------------------------

# digital display resolution in pixels
IMAGE_WIDTH_PX  = 2560
IMAGE_HEIGHT_PX = 1440

# physical display geometry in cm
DISPLAY_WIDTH_CM    = 59.7
VIEWING_DISTANCE_CM = 57.0

# width of the transition area in dva
TRANSITION_WIDTH_DVA = 10.0

# nominal 10-90% transition width
SIGMOID_TRANSITION_WIDTHS_DVA = [6.0, 7.0, 8.0]

# digital grayscale range
MIN_PIXEL_INTENSITY = 0.0   # black
MAX_PIXEL_INTENSITY = 1.0   # white
GRAYSCALE_MAX_VALUE = 255

# output directory
SCRIPT_DIR  = Path(__file__).resolve().parent
OUT_DIR     = SCRIPT_DIR / "BG_stim"
OUT_DIR.mkdir(parents=True, exist_ok=True)



# -----------------------------------------------
# CALCULATE PIXELS OF TRANSITION AREA
# -----------------------------------------------

# helper function
def dva2pix(dva, 
            VIEWING_DISTANCE_CM=57.0,
            DISPLAY_WIDTH_CM=59.7,
            IMAGE_WIDTH_PX=2560):
    """
    Convert dva into a pixel number based on 
    viewing distance and display width.
    """

    width_cm = (
        2.0
        * VIEWING_DISTANCE_CM
        * np.tan(np.deg2rad(dva / 2.0))
    )
    
    pixel_width = (
        width_cm
        / DISPLAY_WIDTH_CM
        * IMAGE_WIDTH_PX
    )


    return round(pixel_width)


# convert transition area into pixels
transition_width_px = dva2pix(TRANSITION_WIDTH_DVA)


# define center of transition area
center_px   = IMAGE_WIDTH_PX // 2
left_px     = center_px - transition_width_px // 2
right_px    = center_px + transition_width_px // 2



# -----------------------------------------------
# CALCULATE ACTUAL TRANSITION AREA
# -----------------------------------------------

# convert pixels into physical width
transition_width_cm_actual = (
    DISPLAY_WIDTH_CM
    * transition_width_px
    / IMAGE_WIDTH_PX
)

# calculate dva based on physical width
transition_width_dva_actual = np.rad2deg(
    2.0
    * np.arctan(
        transition_width_cm_actual
        / (2.0 * VIEWING_DISTANCE_CM)
    )
)

# create horizontal coordinates across the transition area
# transition boundaries span approximately -5 to +5 dva
transition_x_norm = np.linspace(
    -1.0,
    1.0,
    transition_width_px,
    dtype=np.float64,
)

transition_x_dva = (
    transition_x_norm
    * transition_width_dva_actual
    / 2.0
)



# -----------------------------------------------
# GENERATE TRANSITION AREA
# -----------------------------------------------

# helper function to normalize array for image values
def normalize(values):
    """
    Normalize an array to the range of 0 and 1.
    """

    min = np.min(values)
    max = np.max(values)

    if np.isclose(max, min):
        
        values = np.zeros_like(
            values,
            dtype=np.float64
        )

    else:
        values = (
            (values - min)
            / (max - min)
        )


    return values



# helper function to compute logistic function
def logistic_func(x):
    """
    Compute values based on a numerically stable 
    logistic function:
    
    I(x) = 1 / (1 + exp(-x))
    """

    y = 1.0 / (1.0 + np.exp(-x))

    return y


# helper function to compute the transition as logistic function 
# with an additional slope parameter
def get_sigmoid_transition(dva, transition_width_dva):
    """
    Generate a normalized logistic sigmoid transition with the
    nominal W10-90 width:

    Nominal W10-90 = 2 * ln(9) / a.

    a = 2 * ln(9) / W10-90

    The resulting values are normalized over the finite sampled 
    area. Consequently, the realized W10-90 width may differ 
    slightly from the nominal width. 
    """

    if transition_width_dva <= 0:
        raise ValueError(
            "the nominal transition width must be positive!"
        )

    # calculate a (steepness)
    a = (
        2.0
        * np.log(9.0)
        / transition_width_dva
    )

    # compute values based on sigmoid function
    y = logistic_func(a * dva)
    # y = 1.0 / (1.0 + np.exp(-(a * x_deg)))

    # normalize
    y = normalize(y)

    
    return y


# helper function to estimate the local maximum of slope
def get_max_slope(values, dva):
    """
    Estimate the maximum of absolute numerical slope.
    """

    # get slope values
    slopes = np.gradient(values, dva)

    # find maximum of absolut slope values
    slopes_max = float(np.max(
        np.abs(slopes)
    ))


    return slopes_max



# -----------------------------------------------
# GENERATE TRANSITIONS
# -----------------------------------------------

# initiate
transition_dict     = {}
transition_summary  = []

for width_dva in SIGMOID_TRANSITION_WIDTHS_DVA:

    # create filename
    label       = f"{width_dva:g}".replace(".", "p")
    filename    = f"background_{label}dva.png"


    # generate transition values
    transition_vals = get_sigmoid_transition(
        dva=transition_x_dva,
        transition_width_dva=width_dva
    )

    # get maximum slope
    slope_max = get_max_slope(
        values=transition_vals,
        dva=transition_x_dva
    )



    # store profile and its metadata
    transition_dict[filename] = transition_vals

    transition_summary.append(
        {
            "filename":         filename,
            "W10-90_width_dva": width_dva,
            "maximum_slope":    slope_max,
        }
    )



# -----------------------------------------------
# GENERATE IMAGE BASED ON TRANSITION VALUES
# -----------------------------------------------

# helper function to create image based on transition values
def transition2array(transition_vals,
                     left_px,
                     right_px,
                     min_value=0,
                     max_value=1
                     ):
    """
    Create an image by embedding the transition values into 
    an array of the full image width. Array consists of values
    on the left side for black (0), central value containing 
    the transition values, and values on the right side for 
    white (1).
    """

    # initiate array
    array = np.empty(IMAGE_WIDTH_PX, dtype=np.float64)

    # left values for black
    array[:left_px] = min_value

    # central values for transition
    array[left_px:right_px] = transition_vals

    # right values for white
    array[right_px:] = max_value

    # ensure that transition values joins the constant regions.
    # array[left_px] = min_value
    # array[right_px - 1] = max_value


    return array

def create_image(transition_vals, filename):
    """
    Create and save a full-size horizontal grayscale stimulus.

    The horizontal intensity profile is replicated identically
    across all image rows. The resulting PNG therefore contains
    a horizontal gradient without vertical intensity variation.
    """
    """
    Save a horizontal grayscale gradient with markers.
    """

    # create full image from transition values
    array = transition2array(transition_vals,
                             left_px=left_px,
                             right_px=right_px,
                             min_value=MIN_PIXEL_INTENSITY,
                             max_value=MAX_PIXEL_INTENSITY
                             )

    # convert array [0, 1] to grescale values [0, 255]
    array = np.clip(
        np.rint(array * 255.0),
        0,
        255
    ).astype(np.uint8)

    # repeat the same horizontal row to create the full image
    array = np.tile(array, (IMAGE_HEIGHT_PX, 1))

    # convert array to image
    image = Image.fromarray(array).convert("RGB")

    # save stimulus as PNG file
    output_path = OUT_DIR / filename
    image.save(output_path)

    print(f"Saved: {output_path}")


for filename, profile in transition_dict.items():

    create_image(transition_vals, filename)




# -----------------------------------------------
# SUMMARY
# -----------------------------------------------

half_transition_angle_dva = transition_width_dva_actual / 2.0


print("\nAll background stimuli have been generated.")
print(f"Output directory: {OUT_DIR}")

print(f"Image resolution: {IMAGE_WIDTH_PX} x {IMAGE_HEIGHT_PX}")
print(f"Screen width: {DISPLAY_WIDTH_CM:.1f} cm")
print(f"Viewing distance: {VIEWING_DISTANCE_CM:.1f} cm")

print(f"Requested transition width: {TRANSITION_WIDTH_DVA:.2f} dva")
print(f"Actual modulation width: {transition_width_dva_actual:.3f} dva")

print(f"transition boundaries: "
      f"-{half_transition_angle_dva:.2f} dva"
      f"+{half_transition_angle_dva:.2f} dva"
      )
print(f"Modulation width: {transition_width_px} pixels")

print(f"Number of profiles: {len(transition_dict)}")
print("\nProfile parameters and estimated maximum slopes:")

for profile_info in transition_summary:
    print(
        f"{profile_info['filename']}: "
        f"nominal W10-90="
        f"{profile_info['W10-90_width_dva']:.2f} dva, "
        f"maximum slope="
        f"{profile_info['maximum_slope']:.4f} "
        f"value/dva"
    )

