from HandStimuli import HandStim, Log_file
from psychopy import visual, core
from HandEEG import EEG_stream, EEGizer
from HandClassificazione import Classifier
import numpy as np
import serial

import multiprocessing as mp
import subprocess as sbp
import os, pickle, random, math, time

## PARAMETERS
working_dir = 'D:/Code/Oumnique'
name = 'tempo'
trialn = 7

arduino = serial.Serial(port = 'COM6', baudrate = 115200, timeout = 0.1)
def send_trig(x):
    x = str(x)
    arduino.write(bytes(x, 'utf-8'))
    core.wait(0.1)
    arduino.write(bytes(str(0), 'utf-8'))

# ### LEARN ###
hand = HandStim(path2imgs_highed = 'D:/oumnique/q',
                 path2imgs_marked = 'D:/oumnique/p',
                 path2frames = 'D:/oumnique/frames',
                 stim_params = {'high_dur':0.1, 'pause_dur':0.2, 'repeats_cycle':10},
                 learn_loops = 2)

# # hand._get_synSquare('black')
# # hand.win.flip()
# # os.chdir(working_dir)
# # core.wait(1)
# # subL = sbp.Popen(['python', 'subprocLearn.py'], shell = True)
# # core.wait(3)
# # print(subL.poll())
# # hand.stimuli_classification_mode()
# # hand.just_fingers.draw()
# # hand.win.flip()
# # print(subL.poll())
# # while subL.poll() is None:
# #     core.wait(0.25)
# #     hand.just_fingers.draw()
# #     hand._get_synSquare('black')
# #     hand.win.flip()
# #     print(subL.poll())
# # print(subL.poll())

# # log = Log_file(hand.high_log, path2dir_log = 'D:/oumnique/learn_logs', name = name)
# # log.save_log()


## CLASSIFICAZIONE ###
clf = Classifier(path2classifiers = 'D:/oumnique/classifiers',
                path2learnlogs = 'D:/oumnique/learn_logs',
                path2learneegs = 'D:/oumnique/learn_eegs',
                path2flashes = 'D:/oumnique/flashes',
                name = name, epoch_len=0.5,
                filt_lowcut = 0.5, filt_highcut = 20,
                pd_threshold = 1)
x, y = clf.learn()
# print('SUKA ETO IGREKI:', y)
clf.make_classif(x = x, y = y)


### PLAY ###
os.chdir('D:/Code/Oumnique')
stimulation_mode_list = random.sample([0,1]*int(math.ceil(trialn/2)), trialn) #zeros are for pre-feedback stimulation and vice versa
for triali in range(trialn):

    os.chdir(working_dir)
    sub = sbp.Popen(['python', 'subproc.py'], shell = True)

    hand.stimuli_trial_mode()
    is_highed = hand.fullflashSeq
    print(hand.fullflashSeq)

    hand.just_fingers.draw()
    hand._get_synSquare('black')
    hand.win.flip()
    while sub.poll() is None:
        # core.wait(0.25)
        hand.demo_high_cycle()
        
    os.chdir('D:/oumnique/tempi')
    edata2use = np.load(name + '_EEG_data.npy')

    eeg_prop = EEGizer(epoch_len=0.5,
                    path2play_evs='D:/oumnique/tempi', name = name)
    eeg = eeg_prop.epoching(edata2use, is_highed)

    core.wait(0.3)
    if stimulation_mode_list[triali] == 0:
        send_trig(2)
    core.wait(0.7)

    finger2flex = clf.get_choice(eeg, is_highed)
    print(finger2flex, finger2flex, finger2flex)

    if stimulation_mode_list[triali] == 1:
        send_trig(2)

    hand.flex(finger2flex)
    hand.win.flip()
    hand.just_fingers.draw()
    hand.win.flip()
    core.wait(0.25)
hand.del_stims()



