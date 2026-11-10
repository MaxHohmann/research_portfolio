# ---------------------------------------------------------
# EXPERIMENT DEMO
# ---------------------------------------------------------
"""
Short script demonstrating how to use the MMBTS functions within 
an experiment. The experiment contains a short loop over trials 
with different event.

Trial triggers indicate the start and end of each trial (useful
for aligning and averaging trials).

Event triggers indicate the timing of specific events (useful for
marking target onsets, stimulus changes, etc.).

Pause triggers are used to control the pause mode for saving data. 
Trigger values for 'PauseOn' and 'PauseOff' are defined in the 
.cfg file within the ActiveTwo application.

As ActiView saves data in chunks of 1 second (BDF record length), 
enabling pause mode ('PauseOn') stops saving incoming data to disk, 
while data streaming continues. Enabling pause mode can affect 
previously sent triggers if they fall within the same saving cycle
as the 'PauseOn' trigger. The current 1-second buffer is not saved
once pause mode is enabled. 

Therefore, 'PauseOn' should be sent at least 1 second after the last
trigger relevant for analysis (e.g., trigger marking the end of 
trials) to ensure that all relevant data have been written to disk.


Date    :   10/11/2026
Author. :   Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
            https://github.com/MaxHohmann
"""



# ----- SETUP ---------------------------------------------

from pathlib import Path
import time


# import MMBT-S module
from mmbts import MMBTS



# ----- SETTINGS ------------------------------------------

# set debugging mode
# debugging = True        # simulate port, check trigger values
debugging = False       # for running the experiment


# trial parameters
n_trials            = 5         # number of trials
ITI_time            = 3.0       # inter-trial-interval in s
BDF_Buffer_time     = 1.0       # time to finsish BDF recording in s


# trigger values
TRIGGERS = {
    # trial events
    "trial_start":      10,
    "trial_end":        11,

    "event_01":         20,
    "event_02":         21,
    "event_03":         22,
    "event_04":         23,
    "event_05":         24,


    # mode for data saving
    "PauseOff":         254,    # data is saved
    "PauseOn":          255,    # no data saving
}



# ----- START EXPERIMENT ----------------------------------

print("---=== START EXPERIMENT ===---")


# open serial port
MMBTS.show_ports()                  # show available ports

mmbt = MMBTS()
mmbt.open_port("COM5", debugging)   # open port

time.sleep(3.0)



# ----- TRIAL LOOP ----------------------------------------

for trial in range(1, n_trials + 1):

    print(f"-----> TRIAL ({trial}/{n_trials}) <-----")


    # start recording
    mmbt.send_trigger(TRIGGERS['PauseOff'])


    # ensure delay between 'PauseOff' and first relevant trigger 
    time.sleep(0.5)


    # start trial
    mmbt.send_trigger(TRIGGERS['trial_start'])

    time.sleep(1.0)


    # event onset
    if trial == 1:
        mmbt.send_trigger(TRIGGERS['event_01'])

    elif trial == 2:
        mmbt.send_trigger(TRIGGERS['event_02'])
        
    elif trial == 3:
        mmbt.send_trigger(TRIGGERS['event_03'])

    elif trial == 4:
        mmbt.send_trigger(TRIGGERS['event_04'])

    elif trial == 5:
        mmbt.send_trigger(TRIGGERS['event_05'])

    time.sleep(5.0)


    # end trial
    mmbt.send_trigger(TRIGGERS['trial_end'])


    # ensure current BDF record cycle is saved before 'PauseOn' 
    time.sleep(BDF_Buffer_time)


    # stop recording
    mmbt.send_trigger(TRIGGERS['PauseOn'])


    print(f"TRIAL completed...")


    # break
    time.sleep(ITI_time)



# ----- EXIT EXPERIMENT -----------------------------------

print("---=== EXPERIMENT COMPLETED ===---")


# close serial port
mmbt.close_port()

