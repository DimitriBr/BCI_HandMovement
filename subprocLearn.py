from HandEEG import EEG_stream2
import sys

name = 'tempo'
print("YEP")

recording = EEG_stream2(sj_name = name, path2savedata = 'D:/oumnique/learn_eegs', path2saveevents = 'D:/oumnique/flashes',  max_rec = 6.2)
rec = recording.record_data()
sys.exit()