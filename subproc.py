from HandEEG import EEG_stream2
import sys

name = 'tempo'
print("YEP")

dur = 25/60
recording = EEG_stream2(sj_name = name, path2savedata = 'D:/oumnique/tempi', path2saveevents = 'D:/oumnique/tempi', 
                max_rec = dur, num_ch=8)
rec = recording.record_data()