from sklearn import preprocessing as prp
from sklearn import discriminant_analysis as LinDA
from sklearn import ensemble
from sklearn import model_selection as ms
from sklearn import linear_model
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import pickle
import os



class Classifier():

    def __init__(self,
                path2classifiers = None,
                path2learnlogs = None,
                path2learneegs = None,
                path2flashes = None,
                name = None,
                epoch_len = 0.5,
                sample_rate = 500,
                pd_channel = 9,
                num_ch = 9,
                pd_threshold = 0.7,
                filt_lowcut = 2,
                filt_highcut = 30):
        self.path2classifiers = path2classifiers
        self.path2learnlogs = path2learnlogs
        self.path2learneegs = path2learneegs
        self.path2flashes = path2flashes
        self.name = name

        self.x = None
        self.y = None
        self.clf = None

        self.epoch_len = epoch_len
        self.sample_rate = sample_rate
        self.pd_chanel = pd_channel
        self.num_ch = num_ch
        self.pd_threshold = pd_threshold

        self.lowcut = filt_lowcut
        self.highcut = filt_highcut

    def _filt_n_reshape(self, data2process):
        x = data2process
        sos = signal.butter(10, [self.lowcut, self.highcut], 'bandpass', fs=500, output='sos')
        x = signal.sosfilt(sos, x)
        x_dims = x.shape
        x = x.reshape(x_dims[0], x_dims[1] * x_dims[2])
        print(x.shape)
        # x = prp.scale(x)
        return x

    def make_classif(self, x = None, y = None):

        Clf = LinDA.LinearDiscriminantAnalysis(solver = 'lsqr', shrinkage='auto')

        # print(x)
        # for i in x:
        #     print(i.shape)

        x = np.asarray(x)
        print(x.shape)
        x_dims = x.shape

        x = self._filt_n_reshape(x)

        # sos = signal.butter(10, [2, 30], 'bandpass', fs=500, output='sos')
        # x = signal.sosfilt(sos, x)
        # x = x.reshape(x_dims[0], x_dims[1] * x_dims[2])
        # print(x.shape)
        # x = prp.scale(x)

        Clf.fit(x, y)


        os.chdir(self.path2classifiers)
        with open(self.name + '_clf.pickle', 'wb') as out:
            pickle.dump(Clf, out)

        # print(Clf.score(x,y))

        scores = ms.cross_val_score(Clf, x, y, cv=5)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))

        self.x = x 
        self.y = y
        self.clf = Clf

    def learn(self):

        os.chdir(self.path2learnlogs)
        with open (self.name + '_stimuli.pickle', 'rb') as logstim:
            alltheflashes = pickle.load(logstim)

        os.chdir(self.path2learneegs)
        data = np.load(self.name + '_EEG_data.npy')

        os.chdir(self.path2flashes)
        with open (self.name + '_pd.pickle', 'rb') as logstim:
            times_of_flashes = pickle.load(logstim)

      
        highs = []
        current_target = []
        
        for i in alltheflashes:
            highs.extend(alltheflashes[i]['highlight_sequence'])
            current_target.extend([alltheflashes[i]['being_trained']] * len(alltheflashes[i]['highlight_sequence']))

        is_it_target = []
        for i in range(len(highs)):
            is_it_target.append(highs[i] == current_target[i])

    
        timestamps = data[:, 0] ### take the PD-channel from the np-array with data docked
        eeg = data[:,1:]
        eeg = eeg.transpose()

        flash_onsets = []
        for i in range(len(times_of_flashes)):
            onset = np.where(timestamps == times_of_flashes[i])[0][0]
            # print(onset)
            flash_onsets.append(onset)
            # print(len(flash_onsets))

        if len(highs) != len(flash_onsets):
            print('WARNING!\nNumber of flashes does not match the number of detected flashs in EEG data.\n',
                'Check diod threshold, diod channel or quality of EEG registration.')
            print ('Number of logged flashes - %s.\n' % len(highs),
                'Number of detected flashes - %s.' % len(flash_onsets))
        else:
            print("MAAAAN, IT'S ZAYEBOOMBA WITH MARKS, YEAH")

        self.epochs = []

        for i in range(len(times_of_flashes)):
            # print('AAAA:', len(times_of_flashes))
            epoch = eeg[:, flash_onsets[i]:flash_onsets[i]+int(self.epoch_len*self.sample_rate)]
            epoch = epoch[:,1:] ### убираем первый сэмпл в каждой эпохе, так как flash-start соответсвтует сэмплу ПЕРЕД включением подстветки
            self.epochs.append(epoch)

        # self.learn_db = {'LearnData': self.epochs, 'Is_target': is_it_target}

        # with open (self.name + '_LearnDB.pickle', 'wb') as file:
        #     pickle.dump(self.learn_db, file ) 

        return self.epochs, is_it_target

    def get_choice(self, EEGdata, is_highed):
      
        EEGdata = np.asarray(EEGdata)
        # x_dims = EEGdata.shape
        # print(x_dims)

        EEGdata = self._filt_n_reshape(EEGdata)
        # sos = signal.butter(10, [2, 30], 'bandpass', fs=500, output='sos')
        # EEGdata = signal.sosfilt(sos, EEGdata)
        # EEGdata = EEGdata.reshape(x_dims[0], x_dims[1] * x_dims[2])
        # EEGdata = prp.scale(EEGdata)
        # print(EEGdata.shape)

        finger_scores = []
        print(is_highed)
        for finger in range(5):
            vectors = EEGdata[finger == np.array(is_highed),:]
            score = np.mean(self.clf.predict_proba(vectors), axis = 0)
            print(score)
            finger_scores.append(score[1])
            print(finger_scores)

        best_finger = finger_scores.index(max(finger_scores));

        return (best_finger)
