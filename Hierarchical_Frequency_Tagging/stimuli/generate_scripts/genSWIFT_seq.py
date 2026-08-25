"""
This script generates the SWIFT stimuli based on wavelect-scrambleing of original images.
Each stimulus is a sequence of frames whereby each frame corresponds to descrete state of 
one cycle at the SWIFT modulation (at f0) sampled in respective to a defined refresh rate 
of a divice for stimulus presentation. Additionaly, sequences can be saved as video files
or can be previewed.


Version:    1.3
Date:       27/04/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""


import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from PIL import Image
from scipy.ndimage import gaussian_filter
from swift import swift


# ----- parameters -----
swift_freq  = [1, 1.2]              # scramble frequency (Hz)
frame_rate  = 120                   # refersh rate (Hz)
target_size = 300                   # size of frame
category    = ["faces", "houses"]   # stimulus category

# additional visualization of the first image of each category for both swift frequences
show_preview    = False     # show preview of swift sequence (True, False)
save_video      = True      # generates a video of swift sequence (True, False)
save_png        = True      # generates a png files for each 125 ms within the swift sequence (True, False)

# ----- image root -----
STIM_FOLDER     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_FOLDER       = os.path.join(STIM_FOLDER, "original")         # input folder
OUT_FOLDER      = os.path.join(STIM_FOLDER, "swift")       # output folder

PNG_FOLDER      = os.path.join(OUT_FOLDER, "PNG_files")         # folder for PNG files
VIDEO_FOLDER    = os.path.join(OUT_FOLDER, "video")            # folder for video

os.makedirs(PNG_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)


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
# generate SWIFT-sequence
# -------------------------
# loop for each stimulus category subfolder (face, house)
# lopp for each image file within subfolder (10)
# loop for each scramble frequency (2)

# initialize array to store image parameters
Lum_mean    = []
Lum_std     = []
RMS_mean    = []
RMS_std     = []


# ----- category loop -----
for cat in category:

    # get category subfolder
    IN_SUBFOLDER    = os.path.join(IN_FOLDER, cat)
    OUT_SUBFOLDER   = os.path.join(OUT_FOLDER, cat)

    os.makedirs(OUT_SUBFOLDER, exist_ok=True)

    print(f"category: {cat.upper()}")

    
    # files in subfolder
    img_files = sorted(f for f in os.listdir(IN_SUBFOLDER) if f.lower().endswith(".jpg"))


    # ----- image loop -----
    for img in img_files:

        # input path
        path_in = os.path.join(IN_SUBFOLDER, img)

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


        # ----- freq loop -----
        for freq in swift_freq:
            
            print(f"image\t: {img}\tfreq\t: {freq} Hz")


            # frequency label in mHz
            freq_label = f"{int(freq * 1000)}mHz"

            # apply swift
            sequence = swift(freq, frame_rate, stim_img)

            # RMS contrast normalization
            for i in range(sequence.shape[0]):

                sequence[i] = normalize_rms(sequence[i], target_lum=127.5, target_rms=50)


            # ----- get frame parameters for control -----
            frame_lum   = [np.mean(f) for f in sequence]
            frame_rms   = [np.sqrt(np.mean((f - np.mean(f))**2)) for f in sequence]

            print("\t------------------------------------------------")
            print("\tLUM across frames     \t:", np.mean(frame_lum))
            print("\tStd Lum across frames \t:", np.std(frame_lum))
            print("\tRMS across frames     \t:", np.mean(frame_rms))
            print("\tStd RMS across frames \t:", np.std(frame_rms))
            print("\t------------------------------------------------")
            
            # assign values
            Lum_mean.append(np.mean(frame_lum))
            Lum_std.append(np.std(frame_lum))
            RMS_mean.append(np.mean(frame_rms))
            RMS_std.append(np.std(frame_rms))


            # ----- change frame order -----
            n_frames    = sequence.shape[0] # number of frames
            noise_frame = n_frames // 2     # most scrambled frame 

            # reshape sequence
            order       = (np.arange(n_frames) + noise_frame) % n_frames
            sequence    = sequence[order]


            # ----- save sequence as array -----
            filename    = img.replace(".jpg", f"_swift_{freq_label}.npy")
            out_path    = os.path.join(OUT_SUBFOLDER, filename)
            
            np.save(out_path, sequence)


            # ----- save sequence frames as PNG file -----
            if save_png and img == img_files[0]:

                # frame index
                png_frames = [0, 15, 30, 45, 60, 75]

                # time of each frame 
                png_labels = [int((f / 3) * 25) for f in png_frames]

                # save frames (
                for i, idx in enumerate(png_frames):

                    # define filename
                    filename = f"{img.replace('.jpg','')}_swift_{freq_label}_frame_{png_labels[i]}ms.png"
                    out_path = os.path.join(PNG_FOLDER, filename)

                    stim_png = Image.fromarray(sequence[idx].astype(np.uint8))
                    stim_png.save(out_path, "PNG")

                print(f"\tSAVED FRAMES")
                print("\t------------------------------------------------")

        
            # ----- generate video -----
            if save_video and img == img_files[0]:

                # define filename 
                filename    = img.replace(".jpg", f"_swift_{freq_label}.mp4")
                out_path    = os.path.join(VIDEO_FOLDER, filename)

                # iterations of swift cycle
                video_cycles = 5 # number of swift cycles
                video_frames = sequence.shape[0] * video_cycles

                # generate video sequence
                writer = imageio.get_writer(out_path, fps=frame_rate)
                for fr in range(video_frames):

                    # get frame from sequence array
                    frame = sequence[fr % sequence.shape[0]]

                    # make frame compatible for video 
                    frame = np.clip(frame, 0, 255).astype(np.uint8)
                    frame = cv2.resize(frame, (608, 608))

                    # assign frame 
                    writer.append_data(frame)

                writer.close()

                print(f"\tSAVED VIDEO")
                print("\t------------------------------------------------")


            # ----- show preview -----
            if show_preview:

                # initiate figure window
                current_frame = 0
                fig, ax = plt.subplots(figsize=(5, 5))
                img_handle = ax.imshow(
                    sequence[current_frame],
                    cmap='gray',
                    vmin=0,
                    vmax=255
                    )
                ax.axis('off')
                ax.set_title(f"Frame {current_frame+1}/{sequence.shape[0]}")
                

                # -------------------------
                # # key-event function
                # -------------------------
                def on_key(event): 
                    global current_frame

                    # update figure
                    if event.key == ' ':
                        
                        # go to next frame within sequence 
                        current_frame = (current_frame + 1) % sequence.shape[0]
                        img_handle.set_data(sequence[current_frame])
                        ax.set_title(f"Frame {current_frame+1}/{sequence.shape[0]}")
                        fig.canvas.draw_idle()
                        
                    # close figure
                    elif event.key == 'escape': 
                        plt.close(fig)


                # connect key-event
                fig.canvas.mpl_connect('key_press_event', on_key)
                
                # show figure
                plt.show()
                # -------------------------
            

# ----- save frame parameters -----
# np.save(os.path.join(PHASE_FOLDER, "lum_values.npy"), Lum_mean)
# np.save(os.path.join(PHASE_FOLDER, "rms_values.npy"), RMS_mean)
# -------------------------

