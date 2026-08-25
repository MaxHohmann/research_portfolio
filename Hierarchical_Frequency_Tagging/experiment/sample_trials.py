"""
This function loads a pre-generated condition table and selects a subset of trial
conditions based on predefined experimental groups. Each group represents a balanced 
subset of trial conditions. Trial conditions contain 10 unique stimulus pairs (house
and face) that are sampled repeatedly with varying position, flicker frequencies, 
and SWIFT frequencies.

Groups of trial conditions are counterbalaced across participants by assigning each
group based on participant IDs. The corresponding sequence of trials is then randomly 
shuffled in order. Thus, each participant will see a controlled subset of trials but 
in radomized order, maintaining balanced trial conditions across sessions.

INPUT:      
            subject_ID : int or str, optional
                Identifier of the participant used to ensure reproducible
                group assignment and trial randomization.

OUTPUT:
            trials : list of dict
                List of trial dictionaries containing all condition parameters 
                (e.g., stimulus files, categories, frequencies). The order of 
                trials is randomized.

            group_name : str
                Name of the selected group (e.g., "group_1"), 
                indicating which subset of conditions was assigned.

Version:    1.1
Date:       27/04/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""


import os
import csv
import re
import random


# ----------------------
# sample trials
# ----------------------
def sample_trials(subject_ID):

    # each group contains 2 times  all stimuli (20) with:
    #       - balanced SWIFT frequencies (2) 
    #       - balanced SSVEP frequencies (2)
    #       - balanced position (2)


    # initiate
    trials      = []


    # trial IDs for each group
    GROUPS = {
        "group_1": [1,5,10,14,19,23,28,32,33,37,42,46,51,55,60,64,65,69,74,78],
        "group_2": [2,6,11,15,20,24,25,29,34,38,43,47,52,56,57,61,66,70,75,79],
        "group_3": [3,7,12,16,17,21,26,30,35,39,44,48,49,53,58,62,67,71,76,80],
        "group_4": [4,8,9,13,18,22,27,31,36,40,41,45,50,54,59,63,68,72,73,77]
    }


    # path to condition table
    EXP_PATH        = os.path.dirname(os.path.abspath(__file__))    # experiment folder
    COND_PATH       = os.path.join(EXP_PATH, 
                                "conditions", 
                                "condition_table.csv")


    # read condition table
    with open(COND_PATH, newline='') as f:
        reader      = csv.DictReader(f)
        conditions  = list(reader)

    group_names = list(GROUPS.keys())


    # get subject number from ID
    subject_num = re.findall(r'\d+', subject_ID)

    # assign group
    if subject_num != []:
        group_index = (int(subject_num[0]) - 1) % len(group_names)
        group_ID = group_names[group_index]
    else:
        print(f"WARNING\t\t: Invalid Subject ID. Using Random Group Assignment.")
        group_ID = random.choice(group_names)

    # get trial IDs
    trial_IDs = GROUPS[group_ID]

    # get assigned stimulus conditions
    for row in conditions:
        if int(row["ID"]) in trial_IDs:
            trials.append(row)


    # randomize trial order
    random.shuffle(trials)


    return trials, group_ID
# ----------------------

