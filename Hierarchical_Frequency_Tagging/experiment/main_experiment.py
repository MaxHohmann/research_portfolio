"""
This is the main script for running the experiment in PsychoPy.

Version:    1.6
Date:       21/07/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""



# Psychopy
from psychopy import core, event, gui, monitors, visual

# standard libraries
import numpy as np
import pyglet
import os
import csv

# custom utility functions
from sample_trials import sample_trials
from mmbts import MMBTS
from utils import get_circle_mask, CalibLines, read_swift_seq, colorize_red, colorize_green, compute_flicker_alpha



# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

n_TRIAL        = 20
TRIAL_dur       = 120       # in s
frame_rate      = 120
n_frames        = int(TRIAL_dur * frame_rate)

# stmilus parameters
STIM_size       = 250               # total stimulus size (image + fusion ring)
STIM_radius     = 100               # stimulus radius

POS_dist        = 550               # default for distance between stimuli
POS_dist_min    = STIM_size + 40    # minimum for allowed distance between stimuli
POS_left        = -(POS_dist / 2)   # default for left stimulus position
POS_right       = (POS_dist / 2)    # default for right stimulus position

TEXT_height     = 50                # default height for text
TEXT_width      = 100               # default width for text

# flicker modulation depth
alpha_min       = 0.7               # minimum of alpha values

# timer variables
frame_buffer    = (1/frame_rate) + 0.001
ISI_time        = 0.5 - frame_buffer
WAIT_time       = 1 - frame_buffer
trigger_delay   = 0.05


# enable debugging mode
debugging       = True     # True        


# path settings
EXP_PATH        = os.path.dirname(os.path.abspath(__file__))    # experiment folder
PROJECT_PATH    = os.path.dirname(EXP_PATH)                     # project folder
STIM_PATH       = os.path.join(PROJECT_PATH, "stimuli")         # stimulus folder
DATA_PATH       = os.path.join(EXP_PATH, "data")                # data folder

os.makedirs(DATA_PATH, exist_ok=True)


print("=====> INITIATE EXPERIMENT <=====")
print(f"project dir\t: {PROJECT_PATH}")


# ----------------------
# monitor setup
# ----------------------
mon = monitors.Monitor('LabMonitor')
mon.setWidth(54.3)
mon.setDistance(57)
mon.setSizePix([1920, 1080])
#mon.setGamma(1.0)  # gamma correction
mon.save()
# ----------------------



# ----------------------
# window
# ----------------------
if debugging == True:
    win = visual.Window(
        size            = [800, 800],
        color           = [-1, -1, -1],     # black
        units           = 'pix',
        monitor         = mon,
        screen          = 0,                # primary screen
        fullscr         = False,            # no full screen
        allowGUI        = True,             # GUI
        waitBlanking    = True,
        infoMsg         = ""
    )

elif debugging == False:
    win = visual.Window(
        size            = [1920, 1080],
        color           = [-1, -1, -1],     # black
        units           = 'pix',
        monitor         = mon,
        screen          = 1,                # second screen
        fullscr         = True,             # full screen
        allowGUI        = False,            # no GUI
        waitBlanking    = True,
        infoMsg         = ""
    )

actual_fps = np.floor(1 / win.monitorFramePeriod)

print(f"window size\t: {win.size}")
print(f"refresh rate\t: {actual_fps} Hz") 


# check refresh rate
if np.floor(actual_fps) >= (frame_rate -1) and np.floor(actual_fps) <= (frame_rate+1)and debugging == False:
   
   print("=====> STOPPED EXPERIMENT <=====")
   print(f"WARNING\t\t: Invalid Refresh Rate!") 

   win.close()
   core.quit()   # stop experiment
# ----------------------



# ----------------------
# subject information
# ----------------------
subj_info = {
    'Subject': '',
    'Session': ''
    }

dlg = gui.DlgFromDict(
    subj_info,
    title   = 'Subject Info',
    order=['Subject', 'Session']
    )

if not dlg.OK:
    core.quit()


# assign input
subject_ID  = subj_info['Subject']
session_ID  = subj_info['Session']
time_ID     = int(core.getAbsTime())


# create file path fo log file and timing file
log_filename = f"{subject_ID}_{session_ID}_data_{time_ID}.csv"
timing_filename = f"{subject_ID}_{session_ID}_timing_{time_ID}.csv"

LOG_PATH = os.path.join(DATA_PATH, log_filename)
TIMING_PATH = os.path.join(DATA_PATH, timing_filename)
# ----------------------



# ----------------------
# trial conditions
# ----------------------
trials, group_ID = sample_trials(subject_ID)

print(f"subject ID\t: '{subject_ID}'")
print(f"session ID\t: '{session_ID}'")
print(f"group ID\t: '{group_ID}'")
# ----------------------


# ----------------------
# response key mapping
# ----------------------
if group_ID in ["group_1", "group_3"]:
    key_mapping = {
        "red":   "LEFT",
        "green": "RIGHT"
    }
elif group_ID in ["group_2", "group_4"]:
    key_mapping = {
        "red":   "RIGHT",
        "green": "LEFT"
    }

print(f"key mapping \t: RED == '{key_mapping['red']}'")
print(f"key mapping \t: GREEN == '{key_mapping['green']}'")

RED_key     = "LINKE" if key_mapping['red'] == "LEFT" else "RECHTE"
GREEN_key   = "LINKE" if key_mapping['green'] == "LEFT" else "RECHTE"



# ------------------------------------------------------------
# DEVICES
# ------------------------------------------------------------

# ----- response keys -----
key_state = pyglet.window.key.KeyStateHandler()
win.winHandle.push_handlers(key_state)

# initiate key
keys = {
    'LEFT': {
        'code':             pyglet.window.key.LEFT,
        'is_pressed':       False,
        'press_time':       None,
        'release_time':     None
    },

    'RIGHT': {
        'code':             pyglet.window.key.RIGHT,
        'is_pressed':       False,
        'press_time':       None,
        'release_time':     None
    }
}


# ----- EEG -----
if not debugging:

    # show all available ports
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(p.device, p.description)


    # open serial port
    mmbt = MMBTS()
    mmbt.open_port("COM5")
    
    # ser_port = serial.Serial(
    #     port        = 'COM5',
    #     baudrate    = 9600
    # )


# ----- Trigger Values -----
TRIGGERS = {
     
    # stimulus conditions
    "FACE_12_08":       1,
    "FACE_12_1":        2,
    "FACE_15_08":       3,
    "FACE_15_1":        4,
    "HOUSE_12_08":      5,
    "HOUSE_12_1":       6,
    "HOUSE_15_08":      7,
    "HOUSE_15_1":       8,

    # Responses
    "BOTH_pressed":     10,
    "LEFT_pressed":     11,
    "RIGHT_pressed":    12,
    "NONE_pressed":     13,

    # Eye Calibration
    "Eye_Calib_0":      20,
    "Eye_Calib_45":     21,
    "Eye_Calib_90":     22,
    "Eye_Calib_135":    23,
    "Eye_Calib_180":    24,
    "Eye_Calib_225":    25,
    "Eye_Calib_270":    26,
    "Eye_Calib_315":    27,
    "Eye_Calib_360":    28,

    # CFS trials
    "CFS_face_left":    30,
    "CFS_face_right":   31,
    "CFS_house_left":   32,
    "CFS_house_right":  33,
    "CFS_response":     34,

    # Timing
    "TRIAL_start_ctrl": 252,
    "TRIAL_end_ctrl":   253,
    "TRIAL_start":      254,
    "TRIAL_end":        255
}


# ----------------------
# TRIGGER FUNCTION
# ----------------------
def trial2trigger(category, FLICKER_freq, SWIFT_freq):
    cat_bit     = 1 if category == "house"    else 0
    ssvep_bit   = 1 if FLICKER_freq == 15.0   else 0
    swift_bit   = 1 if SWIFT_freq == 1.0      else 0

    trigger_bit = 4 * cat_bit + 2 * ssvep_bit + swift_bit + 1


    return trigger_bit



# ------------------------------------------------------------
# STIMULI
# ------------------------------------------------------------

# ----- SWIFT sequences -----
IMG_left = visual.ImageStim(
    win,
    size    = (2*STIM_radius, 2*STIM_radius),
    mask    = get_circle_mask(2*STIM_radius, STIM_radius),
    pos     = (POS_left, 0)
)

IMG_right = visual.ImageStim(
    win,
    size    = (2*STIM_radius, 2*STIM_radius),
    mask    = get_circle_mask(2*STIM_radius, STIM_radius),
    pos     = (POS_right, 0)
)


# ----- image backgrounds -----
DISC_left = visual.Circle(
    win,
    radius      = STIM_radius+0.5,   # slight overlap to prevent gap
    fillColor   = [1,1,1],
    pos         = (POS_left, 0)
)

DISC_right = visual.Circle(
    win,
    radius      = STIM_radius+0.5,   # slight overlap to prevent gap
    fillColor   = [1,1,1],
    pos         = (POS_right, 0)
)


# ----- fusion rings -----
RING_left = visual.ImageStim(
    win,
    image   = os.path.join(STIM_PATH, "fusion_ring.png"),
    size    = (STIM_size, STIM_size),
    pos     = (POS_left, 0)
)

RING_right = visual.ImageStim(
    win,
    image   = os.path.join(STIM_PATH, "fusion_ring.png"),
    size    = (STIM_size, STIM_size),
    pos     = (POS_right, 0)
)


# ----- fixation crosses -----
FIX_left = visual.ShapeStim(
    win,
    vertices    = 'cross',
    size        = 10,
    color       = [1,1,1],  # [1,0,0]
    lineWidth   = 0, 
    pos         = (POS_left, 0)
)

FIX_right = visual.ShapeStim(
    win,
    vertices    = 'cross',
    size        = 10,
    color       = [1,1,1],  # [0,0,1]
    lineWidth   = 0, 
    pos         = (POS_right, 0)
)


# ----- fixation dots -----
EYE_probe_left = visual.Circle(
    win,
    radius      = 4,
    fillColor   = [1, 1, 1],
    lineColor   = None
)

EYE_probe_right = visual.Circle(
    win,
    radius      = 4,
    fillColor   = [1, 1, 1],
    lineColor   = None
)


# ----- calibration lines -----
LINES_heigth     = STIM_radius * 0.7
LINES_offsets    = [-STIM_radius/2, 0, STIM_radius/2]

LINES_left = CalibLines(
    win,
    color       = [1,1,1],
    width       = 5, 
    line_pos    = [POS_left, POS_left, 0, -LINES_heigth],
    offsets     = LINES_offsets
)

LINES_right = CalibLines(
    win,
    color       = [1,1,1],
    width       = 5, 
    line_pos    = [POS_right, POS_right, 0, LINES_heigth],
    offsets     = LINES_offsets
)


# ----- Calibration instruction -----
INSTRUCTION_disc_calib = visual.TextStim(
    win,
    text        = (
        "Scheiben Kalibirierung:\n\n"
        "Richten Sie die Scheiben so aus, dass sie beim Betrachten durch das Stereoskops vollständig sichtbar sind.\n"
        "Drücken Sie die LINKE und RECHTE Pfeiltasten, um die Scheiben zu verschieben.\n\n"
        "Nachdem Sie beide Scheiben separat eingestellt haben, werden Ihnen innerhalb der Scheiben Linien angezeigt.\n"
        "Diese Linien sollen beim Betrachten durch das Stereoskop genau aneinander liegen.\n"
        "Drücken Sie die LINKE und RECHTE Pfeiltasten, um beide Scheiben dementsprechend auszurichten.\n\n"
        "Wenn Sie die Scheiben vollständig ausgerichtet haben, drücken Sie die LEERTASTE.\n\n\n"
        "Drücken Sie nun die LEERTASTE, um die Kalibrierung zu starten"
        ),
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 24,
    wrapWidth   = 800,
    pos         = (0, 0)
)


# ----- Fixation instruction -----
INSTRUCTION_eye_calib = visual.TextStim(
    win,
    text        = (
        "Augen Kalibrierung:\n\n"
        "Ein Fixationspunk wird an verschiedenen Stellen angezeigt.\n"
        "Schauen Sie solange auf den Fixationspunkt bis er verschwindet\n"
        "und an einer anderen Stelle auftaucht.\n\n\n"
        "Drücken Sie nun die LEERTASTE, um die Kalibrierung zu starten"
        ),
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 24,
    wrapWidth   = 800,
    pos         = (0, 0)
)


# ----- CFS instruction -----
INSTRUCTION_CFS = visual.TextStim(
    win,
    text        = (
        "Augendominanz Messung:\n\n"
        "Im folgenden möchten wir Ihre Augendominanz messen.\n"
        "Ihnen wird auf einem Auge eine dynamische Maske gezeigt.\n"
        "Auf dem anderen Auge wird langsam entweder ein Gesicht\n"
        "oder ein Haus eingeblendet.\n\n"
        "Sobald Sie das Haus oder das Gesicht sehen, drücken Sie die LEERTASTE\n\n\n"
        "Drücken Sie nun die LEERTASTE, um den Durchgang zu starten"
        ),
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 24,
    wrapWidth   = 800,
    pos         = (0, 0)
)


# ----- BR instruction -----
INSTRUCTION_BR = visual.TextStim(
    win,
    text        = (
        "Experiment:\n\n"
        "Ihnen werden gleichzeitig ein ROTES und ein GRÜNES Bild gezeigt.\n" 
        "Sie solle dabei berichten, welche Farbe Sie wahrnehmen.\n\n"
        f"Drücken Sie die {RED_key} Pfeiltaste, solange Sie ein ROTES Bild sehen.\n"
        f"Drücken Sie die {GREEN_key} Pfeiltaste, solange Sie ein GRÜNES Bild sehen.\n"
        "Halten Sie die jeweiligen Pfeiltaste solange gedrückt, bis sich Ihre Wahrnehmung ändert.\n\n" 
        "Wenn Sie BEIDE Farben gleichzeitig wahrnehmen, drücken Sie BEIDE Pfeiltasten.\n"
        "Halten Sie BEIDE Pfeiltasten solange gedrückt, bis Sie nur noch eine Farben sehen.\n\n"
        "Versuchen Sie so SCHNELL und AKKURAT wie möglich Ihre Wahrnehmung zu berichten.\n\n\n"
        "Drücken Sie nun die LEERTASTE, um das Experiment zu starten"
        ),
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 24,
    wrapWidth   = 800,
    pos         = (0, 0)
)


# ----- warning text -----
TEXT_disc_warning_left = visual.TextStim(
    win,
    font        = "Helvetica",
    color       = [1,-1,-1],
    height      = 12,
    wrapWidth   = TEXT_width,
)

TEXT_disc_warning_right = visual.TextStim(
    win,
    font        = "Helvetica",
    color       = [1,-1,-1],
    height      = 12,
    wrapWidth   = TEXT_width,
)


# ----- start text -----
TEXT_start_left = visual.TextStim(
    win,
    text        = "Press SPACE to start",
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)

TEXT_start_right = visual.TextStim(
    win,
    text        = "Press SPACE to start",
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)


# ----- break text -----
TEXT_break_left = visual.TextStim(
    win,
    text        = "Press SPACE to continue",
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)

TEXT_break_right = visual.TextStim(
    win,
    text        = "Press SPACE to continue",
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)


# ----- progress text -----
TEXT_progress_left = visual.TextStim(
    win,
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)

TEXT_progress_right = visual.TextStim(
    win,
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)


# ----- exit text -----
TEXT_exit_left = visual.TextStim(
    win,
    text        = "Press SPACE to end the experiment",
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)

TEXT_exit_right = visual.TextStim(
    win,
    text        = "Press SPACE to end the experiment",
    font        = "Helvetica",
    color       = [1,1,1],
    height      = 12,
    wrapWidth   = TEXT_width,
)



# ------------------------------------------------------------
# INITIATE EXPERIMENT
# ------------------------------------------------------------

print("=====> START EXPERIMENT <=====")

# clock
clock = core.Clock()
clock.reset()

TRIAL_num   = 0     # trial number
log_data    = []    # log file
timing_data = []    # timing log file



# ------------------------------------------------------------
# DISC CALIBRATION
# ------------------------------------------------------------

print(f"=====> DISC CALIBRATION <===== [{clock.getTime():.3f}s]")

INSTRUCTION_disc_calib.draw()

win.flip()

event.waitKeys(keyList=['space'])


# ----- calibration loop -----
space_pressed = True   # track press state

for calib in ["left", "right", "both"]:

    is_calib = True
    print(f"disc \t\t: {calib} [{clock.getTime():.3f}s]")

    while is_calib:

        # compute current distance
        POS_dist    = abs(-POS_left + POS_right)
        too_close   = (POS_dist < POS_dist_min)

        # only left disc
        if calib == "left":         
            
            RING_left.draw()

            FIX_left.draw()

            LINES_left.draw()

            # warning if discs are too close
            if too_close:
                TEXT_disc_warning_left.text = "Scheiben sind zu weit rechts! \nVerschieben Sie sie nach links!"
                TEXT_disc_warning_left.draw()


        # only right disc
        elif calib == "right":

            RING_right.draw()

            FIX_right.draw()

            LINES_right.draw()

            # warning if discs are too close
            if too_close:
                TEXT_disc_warning_right.text = "Scheiben sind zu weit links! \nVerschieben Sie sie nach rechts!"
                TEXT_disc_warning_right.draw()


        # both discs
        elif calib == "both":       

            RING_left.draw()
            RING_right.draw()

            FIX_left.draw()
            FIX_right.draw()

            LINES_left.draw()
            LINES_right.draw()

            # warning if discs are too close
            if too_close:
                TEXT_disc_warning_left.text    = "Scheiben sind zu nah beisammen! \nBewegen Sie sie auseinander!"
                TEXT_disc_warning_right.text   = "Scheiben sind zu nah beisammen! \nBewegen Sie sie auseinander!"
                TEXT_disc_warning_left.draw()
                TEXT_disc_warning_right.draw()


        # update screen       
        win.flip()


        # ----- key responses -----
        win.winHandle.dispatch_events()

        # confirm position
        if key_state[pyglet.window.key.SPACE]:
            if not space_pressed and not too_close:

                space_pressed = True
                is_calib = False
                
                print(f"left position \t: {POS_left}")
                print(f"right position\t: {POS_right}")
                print(f"distance      \t: {POS_dist}")

        else:
            space_pressed = False   # reset press state

        # single movement (only left)
        if calib == "left":

            # move leftward
            if key_state[keys['LEFT']['code']]:
                    POS_left    -= 1

            # move rightward
            if key_state[keys['RIGHT']['code']]:
                    POS_left    += 1

        # single movement (only right)
        if calib == "right":

            # move leftward
            if key_state[keys['LEFT']['code']]:
                    POS_right   -= 1

            # move rightward
            if key_state[keys['RIGHT']['code']]:
                    POS_right   += 1

        # paired movement
        elif calib == "both":

            # move closer
            if key_state[keys['LEFT']['code']]:
                    POS_left    += 1
                    POS_right   -= 1

            # move apart
            if key_state[keys['RIGHT']['code']]:
                    POS_left    -= 1
                    POS_right   += 1


        # ----- update position ------
        RING_left.pos   = (POS_left, 0)
        RING_right.pos  = (POS_right, 0)

        FIX_left.pos    = (POS_left, 0)
        FIX_right.pos   = (POS_right, 0)

        LINES_left.update([POS_left, POS_left, 0, -LINES_heigth])
        LINES_right.update([POS_right, POS_right, 0, LINES_heigth])   

        TEXT_disc_warning_left.pos     = (POS_left, TEXT_height)
        TEXT_disc_warning_right.pos    = (POS_right, -TEXT_height)
        
        core.wait(0.1)


# ----- blank screen -----
RING_left.draw()
RING_right.draw()

win.flip()

print(f"disc calibration done. [{clock.getTime():.3f}s]")

core.wait(ISI_time)


# ----- update position ------
DISC_left.pos           = (POS_left, 0)
DISC_right.pos          = (POS_right, 0)

IMG_left.pos            = (POS_left, 0)
IMG_right.pos           = (POS_right, 0)

TEXT_start_left.pos     = (POS_left, TEXT_height)
TEXT_start_right.pos    = (POS_right, TEXT_height)

TEXT_break_left.pos     = (POS_left, TEXT_height)
TEXT_break_right.pos    = (POS_right, TEXT_height)

TEXT_progress_left.pos  = (POS_left, -TEXT_height)
TEXT_progress_right.pos = (POS_right, -TEXT_height)

TEXT_exit_left.pos      = (POS_left, TEXT_height)
TEXT_exit_right.pos     = (POS_right, TEXT_height)


# ----- log stimulus position -----
log_data.append({'trial':   TRIAL_num,
                 'time':    clock.getTime(),
                 'event':   "POS_left",
                 'value':   POS_left})

log_data.append({'trial':   TRIAL_num,
                 'time':    clock.getTime(),
                 'event':   "POS_right",
                 'value':   POS_right})

log_data.append({'trial':   TRIAL_num,
                 'time':    clock.getTime(),
                 'event':   "POS_dist",
                 'value':   POS_dist})




# ------------------------------------------------------------
# COLOR CALIBRATION
# ------------------------------------------------------------

print(f"=====> Color Calibration (HFP) <===== [{clock.getTime():.3f}s]")

# ----- stimulus -----
STIM_radius = 100
STIM_contrast = 1

HFP_disc_left = visual.Circle(
    win,
    radius      = STIM_radius,
    pos         = (POS_left,0)
)

HFP_disc_right = visual.Circle(
    win,
    radius      = STIM_radius,
    pos         = (POS_right,0)
)

# ----- instruction -----
INSTRUCTION_color_calib = visual.TextStim(
    win,
    text=(
        "Farbkalibrierung:\n\n"
        "Im folgenden sehen Sie einen Kreis, der schnell zwischen ROT und GRÜN wechselt.\n\n"
        "Verändern Sie die Helligkeit der ROTEN Farbe:\n\n"
        "LINKE Pfeiltaste  = Rot dunkler\n"
        "RECHTE Pfeiltaste = Rot heller\n\n"
        "Stellen Sie die rote Farbe so ein,\n"
        "dass das Flimmern möglichst gering erscheint.\n\n"
        "Drücken Sie LEERTASTE zur Bestätigung."
    ),
    font="Helvetica",
    color=[1,1,1],
    height=24,
    wrapWidth=800,
    pos=(0,0)
)


INSTRUCTION_color_calib.draw()

win.flip()

event.waitKeys(keyList=['space'])


# ----- HFP PARAMETERS -----
HFP_freq    = 15    # Hz
HFP_nTRIALS = 4     # trials

# 8 frames (4 frames red, 4 frames green)
HFP_cycle_frames   = int(frame_rate / HFP_freq)

# start values for color
GAIN_start  = -0.2
GAIN_step   = 0.01

# initiate results
RED_GAIN_results    = []
GREEN_GAIN_results  = []


# ----- HFP trial loop -----
for hfp_trial in range(HFP_nTRIALS):

    print(f"===> HFP trial {hfp_trial+1}/{HFP_nTRIALS} <===")
    
    finished = False

    frame = 0

    RED_GAIN    = GAIN_start - 0.1  # adjustable
    GREEN_GAIN  = GAIN_start        # reference


    while not finished:

        # ----- flicker phase -----
        phase = frame % HFP_cycle_frames

        # red phase
        if phase < HFP_cycle_frames/2:

            HFP_disc_left.fillColor     = [RED_GAIN, -1, -1]
            HFP_disc_right.fillColor    = [RED_GAIN, -1, -1]

        # green phase
        else:

            HFP_disc_left.fillColor     = [-1, GREEN_GAIN, -1]
            HFP_disc_right.fillColor    = [-1, GREEN_GAIN, -1]


        # ----- update discs -----
        HFP_disc_left.draw()
        HFP_disc_right.draw()

        RING_left.draw()
        RING_right.draw()

        FIX_left.draw()
        FIX_right.draw()

        win.flip()



        # ---------------------------------
        # response
        # ---------------------------------
        keys_pressed = event.getKeys()

        if 'left' in keys_pressed:

            RED_GAIN -= GAIN_step
            # GREEN_GAIN -= GAIN_step


        if 'right' in keys_pressed:

            RED_GAIN += GAIN_step
            # GREEN_GAIN -= GAIN_step

        if 'space' in keys_pressed:

            RED_GAIN_results.append(RED_GAIN)
            GREEN_GAIN_results.append(GREEN_GAIN)


            print(f"RED gain \t: {RED_GAIN:.3f}")
            print(f"GREEN gain \t: {GREEN_GAIN:.3f}")


            log_data.append(
                {
                'trial':    TRIAL_num,
                'time':     clock.getTime(),
                'event':    "HFP_COLOR_RED",
                'value':    RED_GAIN
                }
            )

            log_data.append(
                {
                'trial':    TRIAL_num,
                'time':     clock.getTime(),
                'event':    "HFP_COLOR_GREEN",
                'value':    GREEN_GAIN
                }
            )

            finished=True

        # update franme number
        frame += 1


    # break between trials
    RING_left.draw()
    RING_right.draw()

    FIX_left.draw()
    FIX_right.draw()

    win.flip()

    core.wait(1)



# ----- final color values -----
RED_GAIN    = np.median(RED_GAIN_results)
GREEN_GAIN  = np.median(GREEN_GAIN_results)


print("=====> COLOR CALIBRATION DONE <=====")
print(f"median RED gain \t:  {RED_GAIN:.3f}")
print(f"median GREEN gain \t: {GREEN_GAIN:.3f}")


log_data.append(
    {
    'trial': TRIAL_num,
    'time': clock.getTime(),
    'event': "HFP_COLOR_RED",
    'value': RED_GAIN
    }
)

log_data.append(
    {
    'trial': TRIAL_num,
    'time': clock.getTime(),
    'event': "HFP_COLOR_GREEN",
    'value': GREEN_GAIN
    }
)


core.wait(ISI_time)



# ------------------------------------------------------------
# EYE CALIBRATION
# ------------------------------------------------------------

print(f"=====> Eye Calibration <===== [{clock.getTime():.3f}s]")

INSTRUCTION_eye_calib.draw()

win.flip()

event.waitKeys(keyList=['space'])

if not debugging:
    mmbt.send_trigger(TRIGGERS["TRIAL_start"])


# start timer
wait_clock = core.Clock()

core.wait(trigger_delay)

if not debugging:
    mmbt.send_trigger(TRIGGERS["TRIAL_start_ctrl"])


# ----- fixation parameters -----
EYE_onset_time  = 1 - frame_buffer
EYE_ISI_time    = 0.5 - frame_buffer

FIX_radius      = STIM_radius + 35

# 8 positions in degrees
angles_deg  = [45, 90, 135, 180, 225, 270, 315, 360]
angles_rad  = [np.deg2rad(a) for a in angles_deg]

# compute positions relative to stimulus center
FIX_pos = [(FIX_radius * np.cos(a), FIX_radius * np.sin(a)) for a in angles_rad]

# randomize order
random_order = list(range(len(FIX_pos)))
np.random.shuffle(random_order)


# wait for remaining time 
remaining = WAIT_time - wait_clock.getTime()
core.wait(remaining)


# ----- loop over dot positions -----
for idx in random_order:

    angle   = angles_deg[idx]
    pos_rel = FIX_pos[idx]

    print(f"fixation\t: at {angle} deg [{clock.getTime():.3f}s]")


    # central probe
    EYE_probe_left.pos  = (POS_left, 0)
    EYE_probe_right.pos = (POS_right, 0)

    RING_left.draw()
    RING_right.draw()

    EYE_probe_left.draw()
    EYE_probe_right.draw()

    win.flip()

    if not debugging:
        mmbt.send_trigger(TRIGGERS["Eye_Calib_0"])

    core.wait(EYE_onset_time)


    # withdraw fix dot
    RING_left.draw()
    RING_right.draw()

    win.flip()

    core.wait(EYE_ISI_time)


    # peripheral probe
    EYE_probe_left.pos  = (POS_left  + pos_rel[0], pos_rel[1])
    EYE_probe_right.pos = (POS_right + pos_rel[0], pos_rel[1])

    RING_left.draw()
    RING_right.draw()

    EYE_probe_left.draw()
    EYE_probe_right.draw()

    win.flip()

    if not debugging:
        mmbt.send_trigger(TRIGGERS[f"Eye_Calib_{angle}"])

    core.wait(EYE_onset_time)


    # withdraw fix dot
    RING_left.draw()
    RING_right.draw()

    win.flip()

    core.wait(EYE_ISI_time)


# back to center
EYE_probe_left.pos  = (POS_left, 0)
EYE_probe_right.pos = (POS_right, 0)

RING_left.draw()
RING_right.draw()

EYE_probe_left.draw()
EYE_probe_right.draw()

win.flip()

if not debugging:
    mmbt.send_trigger(TRIGGERS["TRIAL_end_ctrl"])

core.wait(WAIT_time)


# withdraw fix dot
RING_left.draw()
RING_right.draw()

win.flip()

if not debugging:
    mmbt.send_trigger(TRIGGERS["TRIAL_end"])


print(f"fixation calibration done. [{clock.getTime():.3f}s]")

core.wait(ISI_time)



# ------------------------------------------------------------
# CFS TRIALS
# ------------------------------------------------------------

print(f"=====> start CFS <===== [{clock.getTime():.3f}s]")

INSTRUCTION_CFS.draw()

win.flip()

event.waitKeys(keyList=['space'])


# ----- CFS parameters -----
CFS_log     = []
CFS_nTRIALS = 20



##########################################################

# ----- load stimuli -----
face_stim  = np.load(os.path.join(STIM_PATH, "bCFS_stim", "face_test.npy"))
house_stim = np.load(os.path.join(STIM_PATH, "bCFS_stim", "house_test.npy"))
mask_stim  = np.load(os.path.join(STIM_PATH, "bCFS_stim", "CFS_mask.npy"))

face_stim  = (face_stim[::-1, :].astype(float)  / 255.0) * 2 - 1
house_stim = (house_stim[::-1, :].astype(float) / 255.0) * 2 - 1
mask_stim  = (mask_stim[:, ::-1, :].astype(float) / 255.0) * 2 - 1


# ----- alpha ramp -----
alpha_steps = 20
alpha_ramp  = np.concatenate([
    np.linspace(0, 1, alpha_steps),
    np.ones(alpha_steps)
    ])
alpha_flat  = np.concatenate([
    np.ones(alpha_steps),
    np.linspace(1, 0, alpha_steps)
    ])

alpha_update_time = 1 - frame_buffer
mask_update_time  = 0.01667 - frame_buffer


# ----- CFS Trial Loop -----
for CFS_trial in range(CFS_nTRIALS):

    print(f"=====> CFS TRIAL {CFS_trial+1} <===== [{clock.getTime():.3f}s]")

    # Trial Parameter
    target_cat = np.random.choice(["face", "house"])
    target_pos = np.random.choice(["left", "right"])
    target_img = face_stim if target_cat == "face" else house_stim

    print(f"target\t\t: {target_cat} ({target_pos})")

    # Farbe vorberechnen
    target_red   = colorize_red(target_img,   gain=1, baseline=RED_GAIN, contrast=STIM_contrast)
    target_green = colorize_green(target_img, gain=1, baseline=GREEN_GAIN, contrast=STIM_contrast)



    mask_colored = np.array([
        colorize_red(mask_stim[i],   gain=1, baseline=RED_GAIN, contrast=STIM_contrast) if target_pos == "right"
        else colorize_green(mask_stim[i], gain=1, baseline=GREEN_GAIN, contrast=STIM_contrast)
        for i in range(mask_stim.shape[0])
    ])

    if target_pos == "left":
        target_colored = target_red
        alpha_target    = alpha_ramp
        alpha_mask      = alpha_flat

    else:
        target_colored = target_green
        alpha_target    = alpha_flat
        alpha_mask      = alpha_ramp
    

    # ISI
    RING_left.draw();  RING_right.draw()
    FIX_left.draw();   FIX_right.draw()
    win.flip()
    core.wait(WAIT_time)

    # Frame Loop
    alpha_idx         = 0
    mask_frame_idx    = 0
    space_pressed     = False
    last_alpha_update = core.getTime()
    last_mask_update  = core.getTime()
    trial_clock       = core.Clock()

    while not space_pressed:

        t = core.getTime()

        # Alpha Update
        if t - last_alpha_update >= alpha_update_time:
            last_alpha_update = t
            if alpha_idx < len(alpha_ramp) - 1:
                alpha_idx += 1

        # Mask Update
        if t - last_mask_update >= mask_update_time:
            last_mask_update = t
            mask_frame_idx = np.random.randint(0, mask_stim.shape[0])

        # Bild zuweisen
        if target_pos == "left":
            IMG_left.image  = target_colored
            IMG_right.image = mask_colored[mask_frame_idx]
        else:
            IMG_left.image  = mask_colored[mask_frame_idx]
            IMG_right.image = target_colored

        IMG_left.opacity  = alpha_target[alpha_idx]
        IMG_right.opacity = alpha_mask[alpha_idx]

        # Draw
        IMG_left.draw();   IMG_right.draw()
        RING_left.draw();  RING_right.draw()
        FIX_left.draw();   FIX_right.draw()
        win.flip()

        # Response
        if 'space' in event.getKeys():
            rt = trial_clock.getTime()
            print(f"RT\t\t: {rt:.3f}s (alpha_idx={alpha_idx})")

            CFS_log.append({'trial':    CFS_trial + 1,
                            'time':     rt,
                            'event':    "CFS_response",
                            'target':   target_cat,
                            'position': target_pos,
                            'alpha':    alpha_ramp[alpha_idx]})
            space_pressed = True








# ----- blank screen -----
RING_left.draw()
RING_right.draw()

win.flip()

print(f"bCFS task done. [{clock.getTime():.3f}s]")

core.wait(ISI_time)



# ----- CFS Daten speichern -----
cfs_filename = f"{subject_ID}_{session_ID}_cfs_{time_ID}.csv"
CFS_PATH     = os.path.join(DATA_PATH, cfs_filename)

with open(CFS_PATH, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['trial', 'time', 'event',
                                           'target', 'position', 'alpha'])
    writer.writeheader()
    writer.writerows(CFS_log)

print(f"SAVED CFS log\t: {CFS_PATH}")


##########################################################




# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# Start BR task
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
print(f"=====> start BR task <===== [{clock.getTime():.3f}s]")

INSTRUCTION_BR.draw()

win.flip()

# wait for key response
event.waitKeys(keyList = ['space'])



TEXT_progress_left.text = f"{TRIAL_num} / {n_TRIAL} Trials"
TEXT_progress_right.text = f"{TRIAL_num} / {n_TRIAL} Trials"

RING_left.draw()
RING_right.draw()

FIX_left.draw()
FIX_right.draw()

TEXT_start_left.draw()
TEXT_start_right.draw()

TEXT_progress_left.draw()
TEXT_progress_right.draw()

win.flip()

# wait for key response
event.waitKeys(keyList = ['space'])



# ----- loop over trials -----
last_response_state = None

for trial in range(n_TRIAL):

    TRIAL_num   += 1

    if not debugging:
        mmbt.send_trigger(TRIGGERS["TRIAL_start"])

    print(f"=====> TRIAL {TRIAL_num} <===== [{clock.getTime():.3f}s]")


    # ----------------------
    # delay until stim onset
    # ----------------------
    RING_left.draw()
    RING_right.draw()

    FIX_left.draw()
    FIX_right.draw()

    win.flip()


    # start timer
    wait_clock = core.Clock()

    core.wait(trigger_delay)

    if not debugging:
        mmbt.send_trigger(TRIGGERS["TRIAL_start_ctrl"])


    # ----------------------
    # Trial parameters
    # ----------------------
    trial_cond = trials[trial]

    # image filename
    filename_left   = trial_cond["left_file"]
    filename_right  = trial_cond["right_file"]

    # get file paths for stimuli
    IMG_LEFT_PATH   = os.path.join(STIM_PATH, "swift",
                                   trial_cond["left_category"] + "s",
                                   filename_left + ".npy")
    
    IMG_RIGHT_PATH  = os.path.join(STIM_PATH, "swift",
                                   trial_cond["right_category"] + "s",
                                   filename_right + ".npy")
    
    # SWIFT frequency
    SWIFT_left      = float(trial_cond["left_swift_Hz"])
    SWIFT_right     = float(trial_cond["right_swift_Hz"])

    # Flicker frequency
    FLICKER_left    = float(trial_cond["left_flicker_Hz"])
    FLICKER_right   = float(trial_cond["right_flicker_Hz"])


    # ----- SWIFT sequence -----
    swift_seq_left      = read_swift_seq(IMG_LEFT_PATH)
    swift_seq_right     = read_swift_seq(IMG_RIGHT_PATH)

    # colorize
    # swift_seq_left      = colorize_red(swift_seq_left, gain=1, baseline=0.2)       # 0.15       # left is red
    # swift_seq_right     = colorize_green(swift_seq_right, gain=1, baseline=0.0)    # 0.15       # right is green
    swift_seq_left      = colorize_red(swift_seq_left, gain=1, baseline=RED_GAIN, contrast=STIM_contrast)       # 0.15       # left is red
    swift_seq_right     = colorize_green(swift_seq_right, gain=1, baseline=GREEN_GAIN, contrast=STIM_contrast)    # 0.15       # right is green


    # get cycle length
    swift_cycle_left    = swift_seq_left.shape[0]
    swift_cycle_right   = swift_seq_right.shape[0]
    

    # ----- Flicker values -----
    alpha_left          = compute_flicker_alpha(FLICKER_left, frame_rate, alpha_min=0.7)
    alpha_right         = compute_flicker_alpha(FLICKER_right, frame_rate, alpha_min=0.7)
    
    # get cycle length
    alpha_cycle_left    = len(alpha_left)
    alpha_cycle_right   = len(alpha_right)


    # ----- trial bit for trigger -----
    trial_bit = trial2trigger(trial_cond["left_category"], FLICKER_left, SWIFT_left)


    # ----- log trial data ----- 
    print(f"trial ID    \t: {trial_cond['ID']}")

    print(f"left image  \t: {filename_left}")
    print(f"left color  \t: red")
    print(f"left swift  \t: {SWIFT_left} Hz")
    print(f"left flicker\t: {FLICKER_left} Hz")

    print(f"right image  \t: {filename_right}")
    print(f"right color  \t: green")
    print(f"right swift  \t: {SWIFT_right} Hz")
    print(f"right flicker\t: {FLICKER_right} Hz")


    # trial data
    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "TRIAL_start",
                     'value':   TRIAL_num})
    
    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "TRIAL_ID",
                     'value':   trial_cond['ID']})
    
    # left image
    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "IMG_left",
                     'value':   filename_left})

    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "COL_left",
                     'value':   "red"}) 
    
    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   'SWIFT_left',
                     'value':   SWIFT_left})

    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "FLICKER_left",
                     'value':   FLICKER_left})
    
    # right image
    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "IMG_right",
                     'value':   filename_right})

    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "COL_right",
                     'value':   "green"}) 

    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   'SWIFT_right',
                     'value':   SWIFT_right})

    log_data.append({'trial':   TRIAL_num,
                     'time':    clock.getTime(),
                     'event':   "FLICKER_right",
                     'value':   FLICKER_right})


    # wait for remaining time 
    remaining = WAIT_time - wait_clock.getTime()

    if remaining > 0:
        core.wait(remaining)
    else:
        print(f"WARNING: Trial loading took too long! ({wait_clock.getTime():.3f}s)")


    # ----------------------
    # Frame Loop
    # ----------------------
    both_pressed = False

    # start frame clock to track frame onsets
    frame_clock = core.Clock()


    for frame in range(n_frames):

        # image frame relative to sequence cycle length
        IMG_left.image      = swift_seq_left[frame % swift_cycle_left,:,:]
        IMG_right.image     = swift_seq_right[frame % swift_cycle_right,:,:] 

        # flicker value relative to alpha cycle length
        IMG_left.opacity    = alpha_left[frame % alpha_cycle_left]
        IMG_right.opacity   = alpha_right[frame % alpha_cycle_right]

        
        # display update
        DISC_left.draw()
        DISC_right.draw()

        IMG_left.draw()
        IMG_right.draw()

        RING_left.draw()
        RING_right.draw()

        FIX_left.draw()
        FIX_right.draw()
        
        win.flip()


        # send trigger for first and last frame onset
        if frame == 0:
            if not debugging:
                mmbt.send_trigger(trial_bit)

        elif frame == n_frames - 1:
            if not debugging:
                mmbt.send_trigger(TRIGGERS["TRIAL_end_ctrl"])


        # ----- log frame onset -----
        frame_onset = frame_clock.getTime()

        timing_data.append({'trial':   TRIAL_num,
                            'time':    frame_onset,
                            'event':   "STIM_onset",
                            'value':   frame})

        timing_data.append({'trial':   TRIAL_num,
                            'time':    frame_onset,
                            'event':   "STIM_alpha_left",
                            'value':   IMG_left.opacity})

        timing_data.append({'trial':   TRIAL_num,
                            'time':    frame_onset,
                            'event':   "STIM_alpha_right",
                            'value':   IMG_right.opacity})



        # ----------------------
        # RESPONSE STATE
        # ----------------------

        left_pressed    = key_state[keys['LEFT']['code']]
        right_pressed   = key_state[keys['RIGHT']['code']]

        # classify state
        if left_pressed and right_pressed:
            response_state = "BOTH"
        elif left_pressed:
            response_state = "LEFT"
        elif right_pressed:
            response_state = "RIGHT"
        else:
            response_state = "NONE"

        # log only on state change
        if response_state != last_response_state:

            log_data.append({
                'trial':    TRIAL_num,
                'time':     clock.getTime(),
                'event':    "RESPONSE_STATE",
                'value':    response_state
            })

            if debugging:
                print(f"RESPONSE \t: {response_state} pressed")

            # EEG triggers
            if not debugging:
                mmbt.send_trigger(TRIGGERS[f"{response_state}_pressed"])

            # if response_state == "BOTH":
            #     mmbt.send_trigger(TRIGGERS["BOTH_pressed"])

            # elif response_state == "LEFT":
            #     mmbt.send_trigger(TRIGGERS["LEFT_pressed"])

            # elif response_state == "RIGHT":
            #     mmbt.send_trigger(TRIGGERS["RIGHT_pressed"])

            # elif response_state == "NONE":
            #     mmbt.send_trigger(TRIGGERS["NONE_pressed"])

            # update last response state
            last_response_state = response_state




        # #################################################################
        # both_now = key_state[keys['LEFT']['code']] and key_state[keys['RIGHT']['code']]

        # for name, info in keys.items():
        #     key_code = info['code']


        #     # ----- key pressed -----
        #     if key_state[key_code]:
        #         if not info['is_pressed']:

        #             info['is_pressed']  = True
        #             info['press_time'] = clock.getTime()

        #             # log press time
        #             log_data.append({'trial':   TRIAL_num,
        #                             'time':     info['press_time'],
        #                             'event':    f"KEY_{name}",
        #                             'value':    1})
                    
        #             if debugging:
        #                 print(f"KEY_{name}  \t: pressed [{info['press_time']:.3f}s]")


        #             # trigger
        #             if both_now and not both_pressed:
        #                 send_trigger(TRIGGERS["both_down"])
        #                 both_pressed = True

        #             elif name == "LEFT" and not both_now:
        #                 send_trigger(TRIGGERS["left_down"])

        #             elif name == "RIGHT" and not both_now:
        #                 send_trigger(TRIGGERS["right_down"])

        #     # ----- key released -----
        #     else:
        #         if info['is_pressed']:

        #             info['is_pressed']  = False
        #             info['release_time'] = clock.getTime()

        #             # log release time
        #             log_data.append({'trial':   TRIAL_num,
        #                             'time':     info['release_time'],
        #                             'event':    f"KEY_{name}",
        #                             'value':    0})
                    
        #             if debugging:
        #                 print(f"KEY_{name}  \t: released [{info['release_time']:.3f}s]")


        #             # trigger
        #             if both_pressed and not both_now:
        #                 send_trigger(TRIGGERS["both_released"])
        #                 both_pressed = False

        #             elif name == "LEFT"  and not both_now:
        #                 send_trigger(TRIGGERS["left_released"])

        #             elif name == "RIGHT" and not both_now:
        #                 send_trigger(TRIGGERS["right_released"])
        # ----------------------


    # ----------------------
    # time delay for EEG
    # ----------------------
    RING_left.draw()
    RING_right.draw()

    FIX_left.draw()
    FIX_right.draw()

    win.flip()

    core.wait(WAIT_time)

    if not debugging:
        mmbt.send_trigger(TRIGGERS["TRIAL_end"])
    # ----------------------


    # log trial end
    log_data.append({'trial':   TRIAL_num,
                    'time':     clock.getTime(),
                    'event':    "TRIAL_end",
                    'value':    TRIAL_num})


    # show break or exit screen
    TEXT_progress_left.text = f"{TRIAL_num} / {n_TRIAL} Trials"
    TEXT_progress_right.text = f"{TRIAL_num} / {n_TRIAL} Trials"

    RING_left.draw()
    RING_right.draw()

    FIX_left.draw()
    FIX_right.draw()

    if TRIAL_num < n_TRIAL:
        TEXT_break_left.draw()
        TEXT_break_right.draw()

    elif TRIAL_num == n_TRIAL:
        TEXT_exit_left.draw()
        TEXT_exit_right.draw()

    TEXT_progress_left.draw()
    TEXT_progress_right.draw()

    win.flip()

    # wait for key response
    event.waitKeys(keyList=['space'])


    # # ----- break -----
    # if TRIAL_num < n_TRIAL:
    #
    #     TEXT_progress_left.text = f"{TRIAL_num} / {n_TRIAL} Trials"
    #     TEXT_progress_right.text = f"{TRIAL_num} / {n_TRIAL} Trials"
    #
    #     RING_left.draw()
    #     RING_right.draw()
    #
    #     FIX_left.draw()
    #     FIX_right.draw()
    #
    #     TEXT_break_left.draw()
    #     TEXT_break_right.draw()
    #
    #     TEXT_progress_left.draw()
    #     TEXT_progress_right.draw()
    #
    #     win.flip()
    #
    #     # wait for key response
    #     event.waitKeys(keyList=['space'])
    #
    #
    # # ----- exit -----
    # elif TRIAL_num == n_TRIAL:
    #
    #     TEXT_progress_left.text = f"{TRIAL_num} / {n_TRIAL} Trials"
    #     TEXT_progress_right.text = f"{TRIAL_num} / {n_TRIAL} Trials"
    #
    #     RING_left.draw()
    #     RING_right.draw()
    #
    #     FIX_left.draw()
    #     FIX_right.draw()
    #
    #     TEXT_exit_left.draw()
    #     TEXT_exit_right.draw()
    #
    #     TEXT_progress_left.draw()
    #     TEXT_progress_right.draw()
    #
    #     win.flip()
    #
    #     # wait for key response
    #     event.waitKeys(keyList=['space'])
    # # ----------------------


# ----------------------
# save log file
# ----------------------
with open(LOG_PATH, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['trial',
                                           'time',
                                           'event',
                                           'value'])
    writer.writeheader()
    writer.writerows(log_data)

print(f"SAVED log file\t: {LOG_PATH}")


# ----------------------
# save timing file
# ----------------------
with open(TIMING_PATH, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['trial',
                                           'time',
                                           'event',
                                           'value'])
    writer.writeheader()
    writer.writerows(timing_data)

print(f"SAVED timing file\t: {TIMING_PATH}")


# ----------------------
# end EEG recording
# ----------------------
if not debugging:
    mmbt.close_port()


# ----------------------
# Close window
# ----------------------
print("=====> STOPPED EXPERIMENT <=====")
print("succesfully completed experiment")
win.close()
core.quit()

