"""
utility scrip containing helper functions for running the main experiment in PsychoPy.

Version:    1.0
Date:       23/04/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""


import numpy as np



# ----------------------
# create image mask
# ----------------------
def get_circle_mask(size, radius):
    """
    generates an array for opacity values based on the size of an image.
    mask array only shows image parts within a central circle.
    """

    # check input
    if radius > size:
        raise ValueError("radius cannot be larger than size")

    # initiate mask array
    mask_arr = np.ones((size, size))

    # center of image
    cx = cy = size // 2

    # coordinate grid
    y, x = np.ogrid[:size, :size]
    dx = x - cx + 0.5
    dy = y - cy + 0.5

    # get distance to center
    dist = np.sqrt(dx**2 + dy**2)

    # apply mask
    mask_arr[dist >= radius] = -1


    return mask_arr
# ----------------------



# ----------------------
# Calibration lines
# ----------------------
class CalibLines:
    """
    Object that handles calibration lines:
        - generation
        - drawing
        - updating position
    """

    # ----------------------
    # generate lines
    # ----------------------
    def __init__(self, win, color, width, line_pos, offsets):
        """
        generate multiple equal lines that are spaced depending offset on line position
        
        Parameters
        ----------
        win : psychopy.visual.Window

        line_pos : list, defining line possition
            -   line_pos[0] :   x-coordinate of line start
            -   line_pos[1] :   x-coordinate of line end
            -   line_pos[2] :   y-coordinate of line start
            -   line_pos[3] :   y-coordinate of line end

        offsets : list, defining horizontal offsets added to x-coordinates for line start and end

        color : list, defining RGB color of lines

        width : int, defining line width in pixels.
        """

        from psychopy import visual

        # initiate lines
        self.lines = []

        self.win        = win 
        self.offsets    = offsets


        # check line position values
        if len(line_pos) != 4:
            raise ValueError("line_pos must have 4 values")


        # get coordinates
        self.pos_x_start    = line_pos[0]   # start position on x axis
        self.pos_x_end      = line_pos[1]   # end position on x axis
        self.pos_y_start    = line_pos[2]   # start position on y axis
        self.pos_y_end      = line_pos[3]   # end position on y axis


        # create each line
        for offset in offsets:
            line = visual.Line(
                win,
                start       = (self.pos_x_start + offset, self.pos_y_start),
                end         = (self.pos_x_end + offset, self.pos_y_end),
                lineColor   = color,
                lineWidth   = width
            )

            self.lines.append(line)


    # ----------------------
    # draw lines
    # ----------------------
    def draw(self):
        """
        draws lines for the next display update
        """

        for line in self.lines:
            line.draw()


    # ----------------------
    # update line position
    # ----------------------
    def update(self, line_pos):
        """
        updates the position for each line
        """

        # check line position values
        if len(line_pos) != 4:
            raise ValueError("line_pos must have 4 values")


        # get coordinates
        self.pos_x_start    = line_pos[0]   # start position on x axis
        self.pos_x_end      = line_pos[1]   # end position on x axis
        self.pos_y_start    = line_pos[2]   # start position on y axis
        self.pos_y_end      = line_pos[3]   # end position on y axis


        for i, offset in enumerate(self.offsets):
            self.lines[i].start = (self.pos_x_start + offset, self.pos_y_start)
            self.lines[i].end   = (self.pos_x_end + offset, self.pos_y_end)
# ----------------------



# ----------------------
# read swift sequence
# ----------------------
def read_swift_seq(file_path):
    """
    loads and converts the frame sequence of the swift stimulus
    """
     
    # load array
    swift_seq = np.load(file_path).astype(np.uint8)

    # flip vertically
    swift_seq = swift_seq[:, ::-1, :]

    # scale to [-1, 1]
    swift_seq = swift_seq.astype(float) / 255.0
    swift_seq = swift_seq * 2 - 1


    return swift_seq
# ----------------------



# ----------------------
# scale image colors
# ----------------------
def scale_colars(gray_seq, min_val=-1, max_val=1.6):
    """
    scales the color values of an image
    """

    gray_seq = gray_seq.astype(float)

    old_min = np.min(gray_seq)
    old_max = np.max(gray_seq)

    scaled_seq = ((gray_seq - old_min) / (old_max - old_min))

    scaled_seq = (scaled_seq * (max_val - min_val) + min_val)


    return scaled_seq
# ----------------------



# ----------------------
# colorize image red
# ----------------------
def colorize_red(gray_seq, gain=1, baseline=0, contrast=1):
    """
    changes values of an image so that the image appeares red
    """

    gray_seq = gray_seq.astype(float)

    # remove mean
    gray_seq = gray_seq - np.mean(gray_seq)

    # normalize
    gray_seq /= np.max(np.abs(gray_seq))

    # set contrast
    gray_seq *= contrast

    # add value range
    red = (gray_seq + 1) * gain - 1 - (0-baseline) 
    #red = np.clip(red, -1, 1)

    zeros = np.zeros_like(gray_seq)

    
    return np.stack([red, zeros, zeros], axis=-1)
# ----------------------



# ----------------------
# colorize image green
# ----------------------
def colorize_green(gray_seq, gain=1, baseline=0, contrast=1):
    """
    changes values of an image so that the image appeares green
    """

    gray_seq = gray_seq.astype(float)

    # remove mean
    gray_seq = gray_seq - np.mean(gray_seq)

    # normalize
    gray_seq /= np.max(np.abs(gray_seq))

    # set contrast
    gray_seq *= contrast

    # add value range
    green = (gray_seq + 1) * gain - 1 - (0-baseline) 
    # green = np.clip(green, -1, 1)

    zeros = np.zeros_like(gray_seq)


    return np.stack([zeros, green, zeros], axis=-1)
# ----------------------



# ----------------------
# compute alpha values
# ----------------------
def compute_flicker_alpha(freq, frame_rate, alpha_min=0.7):
    """
    computes alpha (opacity) values for sinusoidal flickker.
    list of alpha values corespond to the length of one cycle
    of the flicker frequency sampled at the refresh rate.
    """

    alpha_amp   = 1 - alpha_min     # modulation amplitude

    # frames per cycle
    cycle_frames = frame_rate / freq

    # check if flicker freq can be sampled by refresh rate
    if not cycle_frames.is_integer():
        raise ValueError("flicker frequency does not align with frame rate!")

    t = np.arange(int(cycle_frames)) / frame_rate

    alpha_cycle = alpha_min + alpha_amp * (0.5 * (1 + np.sin(2 * np.pi * freq * t)))
     
     
    return alpha_cycle
# ----------------------

