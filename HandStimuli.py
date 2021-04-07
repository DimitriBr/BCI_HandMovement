from psychopy import visual, event, core
import os, random, pickle, math


class HandStim(): 
    def __init__(self,
                stim_number = 5,
                stim_params = {'high_dur':0.1, 'pause_dur':0.2, 'repeats_cycle':10},
                learn_loops = 2,
                synsq_params = {'size':0.3, 'pos': (0.85, 0.85)},
                path2imgs_highed = None, # путь к папке с подствеченными пальцами,
                path2imgs_marked = None,
                path2frames = None,
                window_size = (800,800)
                ):

        self.win = visual.Window(size = window_size, winType='pyglet')

        os.chdir(path2imgs_highed) ### меняем путь к директории на тот, где хранятся наши картинки
        self.just_fingers = visual.ImageStim(self.win, size = window_size, units = 'pix', image = str(0) + '.jpg')
        self.high_fingers = [visual.ImageStim(self.win, size = window_size, units = 'pix',
                            image = str(i) + '.jpg') for i in range(1,6)] ###список картинок с подствеченными пальцами

        # os.chdir(path2videos)
        # self.videos = [visual.MovieStim3(self.win, str(i) + '.mp4', size = window_size, units = 'pix', noAudio=True,) for i in range(1,6)]

        os.chdir(path2frames)
        self.frames = [0 for i in range(5)]
        for finger in range(5):
            path2frames_singlefin = os.path.join(path2frames, str(finger))
            os.chdir(path2frames_singlefin)
            self.frames[finger] = [visual.ImageStim(self.win, size = window_size, units = 'pix',
                                image = 'frame' + str(i) + '.jpg') for i in range(61)]

        os.chdir(path2imgs_marked)
        self.target_fingers = [visual.ImageStim(self.win, size = window_size, units = 'pix',
                            image = str(i) + '.jpg') for i in range(1,6)] ###список картинок с подствеченными пальцами

        self.repeats_cycle = stim_params['repeats_cycle'] #количество циклов
        self.high_dur = stim_params['high_dur'] #время подсветки в секундах
        self.pause_dur = stim_params['pause_dur'] #время паузы в секундах
        self.stims_amount = len(self.high_fingers)
        self.learn_loops = learn_loops

        self.synsq_params = synsq_params

    def routine_hand_display(self):
        self.just_fingers.draw()
        self.win.flip()

    def flex(self, i):
        self.just_fingers.draw()
        self.win.flip()
        frames_num = len(self.frames[i])
        # print(leng)
        for frame in range(frames_num):
            self.frames[i][frame].draw()
            core.wait(0.02)
            self.win.flip()
        self.just_fingers.draw()
        self.win.flip()
        # self.win.flip()

    def _get_synSquare(self, color):
        self.Syncro = visual.Rect(self.win, size = self.synsq_params['size'])
        self.Syncro.pos = self.synsq_params['pos'] ### it's for photodetector.Position and size of the square for photodetector are defined with the class
        self.Syncro.fillColor = color
        self.Syncro.color = color
        self.Syncro.draw()

    def _highlight(self, N):
        self.high_fingers[N].draw()
        self._get_synSquare('white')
        self.win.flip()
        core.wait(self.high_dur)
    
    def _display_default_hand(self):
        self.just_fingers.draw()
        self._get_synSquare('black')
        self.win.flip()
        core.wait(self.pause_dur)
    
    def _permutate_fullflashSeq(self):
        self.fullflashSeq_default = list(range(self.stims_amount))*self.repeats_cycle
        self.fullflashSeq = random.sample(self.fullflashSeq_default, len(self.fullflashSeq_default))
        return self.fullflashSeq

    def hand_highlightenting(self):
        self.high_order = self._permutate_fullflashSeq()
        for finger in self.high_order:
            self._highlight(finger)
            self._display_default_hand()
    
    def demo_high_cycle(self):
        demo_high_order = list(range(5))
        random.shuffle(demo_high_order)
        for finger in demo_high_order:
            self.high_fingers[finger].draw()
            self._get_synSquare('black')
            self.win.flip()
            core.wait(self.high_dur)

            self._display_default_hand()


    def stimuli_classification_mode(self):
        self._display_default_hand()
        targetSeq = random.sample(self.learn_loops * list(range(self.stims_amount)), self.learn_loops * self.stims_amount)
        print(targetSeq)
        self.high_log = {}

        for i, target in enumerate(targetSeq):
            self.target_fingers[target].draw()
            self._get_synSquare('black')
            self.win.flip()
            core.wait(3)

            self.just_fingers.draw()
            self._get_synSquare('black')
            core.wait(2)

            self.hand_highlightenting()
            
            self.just_fingers.draw()
            self._get_synSquare('black')
            core.wait(3)

            self.high_log[i] = {'being_trained': target, 'highlight_sequence': self.fullflashSeq}

    def stimuli_trial_mode(self):
        self.high_seq = {}

        self.just_fingers.draw()
        self._get_synSquare('black')
        self.win.flip()
        core.wait(3)

        self.hand_highlightenting()

        # with open (self.name + '_LAST_flash_seq', 'wb') as out:
        #     pickle.dump(self.fullflashSeq, out)
        high_seq = self.fullflashSeq

        return(high_seq)


    def del_stims(self):
        del self.just_fingers
        del self.high_fingers
        del self.target_fingers
        del self.frames

class Log_file:
    def __init__(self,
                object2save = None, 
                path2dir_log = None,
                name = None,
                ):
        
        self.object2save = object2save
        self.path2dir_log = path2dir_log
        self.name = name

    def save_log(self):
        os.chdir(self.path2dir_log)
        with open(self.name + '_stimuli.pickle', 'wb') as out:
            pickle.dump(self.object2save, out)


if __name__ == '__main__':
    hand = HandStim(path2imgs_highed = 'D:/oumnique/q', path2imgs_marked = 'D:/oumnique/p', path2frames = 'D:/oumnique/frames')
    hand.stimuli_classification_mode()
    hand.del_stims()
    hand.win.close()
    # print(hand.high_log)

    # log = Log_file(hand.high_log, path2dir_log = 'C:/Users/79154/Desktop', name = 'JJ01')
    # log.save_log()






