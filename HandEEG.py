from pylsl import resolve_stream, StreamInlet
import numpy as np
import sys, os, pickle
import matplotlib.pyplot as plt


class EEG_stream():
    def __init__(self,
                sj_name = None,
                eeg_stream_type = 'Data',
                path2savedata = None,
                max_rec = 7, 
                num_ch = 9, #in minutes
                ):

        self.sj_name = sj_name
        self.path2savedata = path2savedata
        self.num_ch = num_ch
        self.stop = False
        self.ix_count = 0 #for array
        self.max_rec = max_rec

        print("Connection to the stream...")
        streaming = resolve_stream('type', eeg_stream_type)
        self.inlet = StreamInlet(streaming[0])
        self.sampling = streaming[0].nominal_srate()
        print('Nominal srate is {}'.format(self.sampling))
        print('EEG stream contains {} channels'.format(self.inlet.channel_count))

        if self.inlet.channel_count == num_ch:
            print('SUCCESS: module had been connected to the stream!')
        else:
            print('Pardonnez-moi, mes amis. Il y a du probleme C1...')

    def create_array(self, 
                    max_rec = None, #in minutes
                    num_ch = 16,
                    memmap_name = 'eeg.mmap'
                    ):

        if max_rec is None:
            max_rec = self.max_rec
    
        rec_len = self.max_rec*60*self.sampling #mintutes to seconds, and then to samples
        dims = (int(rec_len), self.num_ch + 1)
        print ("Dimmention of EEG aray are %s" %str(dims))

        arr = np.memmap(memmap_name, dtype = 'float', mode = 'w+', shape = dims)
        arr[:,:] = np.nan
        print('Voila')
        return arr

    def fill_array(self, pre_array, data_chunk, timestamp_chunk, ix_count = None):

        if ix_count is None:
            ix_count = self.ix_count

        pre_array[ix_count:ix_count+len(data_chunk), 1:] = data_chunk
        pre_array[ix_count:ix_count+len(data_chunk), 0] = timestamp_chunk
        pre_array.flush()

    def save_data(self, array2save = None, sj_name = None):

        if sj_name is None:
            sj_name = self.sj_name 

        filename = sj_name + '_EEG_data'
        array2save = array2save[~np.isnan(array2save[:,0])] #delete all the extra elements (rows containing nans)
        np.save(os.path.join(self.path2savedata, filename), array2save)


    def record_data(self, max_rec = None):

        self.eeg_array = self.create_array(max_rec = max_rec)
        while self.stop == False :

            #checking whether nans keep containing in a created array. If all nans are filled with numbers, making self.stop == True and terminate iteration
            selected_nans = self.eeg_array[np.isnan(self.eeg_array)]
            is_nans_over = selected_nans.size == 0
            if is_nans_over:
                self.stop = True
            
            try:
                eeg_data, timestamp_eeg = self.inlet.pull_chunk()
            except:
                eeg_data, timestamp_eeg = [], []
        
            if timestamp_eeg:
                try:
                    self.fill_array(self.eeg_array, eeg_data, timestamp_eeg, self.ix_count)
                    self.ix_count = self.ix_count + len(timestamp_eeg)
                except:
                    self.stop = True

            # print(self.eeg_array)


        self.save_data(array2save = self.eeg_array, sj_name = self.sj_name)
        print ('\n...data saved.\n Au revoir, mes amis!.\n')

        sys.exit()

        return self.eeg_array



class EEGizer():
    def __init__(self,
                name = None,
                epoch_len = 1,
                sample_rate = 500,
                pd_channel = 9,
                num_ch = 9,
                pd_threshold = 0.9,
                path2dir_log = 'D:/oumnique',
                path2play_evs = 'None'
                ):

        self.path2dir_log = path2dir_log
        self.name = name
        self.epoch_len = epoch_len
        self.sample_rate = sample_rate
        self.pd_chanel = pd_channel
        self.num_ch = num_ch
        self.pd_threshold = pd_threshold
        self.path2play_evs = path2play_evs


    def epoching(self, data, highs = None): #times_of_flashes is a list from RECORD_DATA method of EEG_stream

        ### IMPLEMENT IF TO USE CHANNEL-LIKE PD ###
        # diod = data[:, self.pd_chanel] ### take the PD-channel from the np-array with data docked
        # eeg = data[:,1:self.num_ch]

        # exceeders = np.array((diod > self.pd_threshold), dtype='int16') ###делаем список из всех семплов, где значение больше порога (то есть сэмплы, когда идет подстветка) - им присваиваем единицу
        # flash_onsets = np.nonzero((exceeders[1:] - exceeders[:-1]) == 1)[0] ### берём нумера сэмплов, в которых началась подстветка (номер последнего нуля перед серией единиц)

        # if len(highs) != len(flash_onsets):
        #     print('WARNING!\nNumber of flashes does not match the number of detected flashs in EEG data.\n',
        #         'Check diod threshold, diod channel or quality of EEG registration.')
        #     print ('Number of logged flashes - %s.\n' % len(highs),
        #         'Number of detected flashes - %s.' % len(flash_onsets))

        # self.epochs = []

        # diod = diod.transpose()
        # eeg = eeg.transpose()

        # for i in range(len((highs))):
        #     epoch = eeg[:, flash_onsets[i]:flash_onsets[i]+int(self.epoch_len*self.sample_rate)]
        #     epoch = epoch[:,1:] ### убираем первый сэмпл в каждой эпохе, так как flash-start соответсвтует сэмплу ПЕРЕД включением подстветки
        #     self.epochs.append(epoch)

        # return self.epochs

        os.chdir(self.path2play_evs)
        with open (self.name + '_pd.pickle', 'rb') as logstim:
            times_of_flashes = pickle.load(logstim)

        timestamps = data[:, 0] ### take the PD-channel from the np-array with data docked
        eeg = data[:,1:]
        eeg = eeg.transpose()

        flash_onsets = []
        for i in range(len(times_of_flashes)):
            onset = np.where(timestamps == times_of_flashes[i])[0][0]
            print(onset)
            flash_onsets.append(onset)
            print(len(flash_onsets))

        if len(highs) != len(flash_onsets):
            print('WARNING!\nNumber of flashes does not match the number of detected flashs in EEG data.\n',
                'Check diod threshold, diod channel or quality of EEG registration.')
            print ('Number of logged flashes - %s.\n' % len(highs),
                'Number of detected flashes - %s.' % len(flash_onsets))

        self.epochs = []

        for i in range(len(times_of_flashes)):
            epoch = eeg[:, flash_onsets[i]:flash_onsets[i]+int(self.epoch_len*self.sample_rate)]
            epoch = epoch[:,1:] ### убираем первый сэмпл в каждой эпохе, так как flash-start соответсвтует сэмплу ПЕРЕД включением подстветки
            self.epochs.append(epoch)

        return self.epochs


    def plotERP(self):

        epochs = self.learn_db['LearnData']
        is_it_target = self.learn_db['Is_target']
        n_target_epochs = is_it_target.count(True)
        n_nont_epochs = is_it_target.count(False)

        # print(self.num_ch - 1, self.epoch_len * self.sample_rate, n_target_epochs)
        target_array = np.zeros((self.num_ch - 1, self.epoch_len * self.sample_rate - 1, n_target_epochs))
        nont_array = np.zeros((self.num_ch - 1, self.epoch_len * self.sample_rate - 1, n_nont_epochs))
        
        target_count = 0
        nont_count = 0
        for i in range(len(epochs)):
            epoch = epochs[i]
            epoch = np.asarray(epoch)
            if is_it_target[i] == True:
                target_array[:, :, target_count] = epoch
                target_count += 1
            else:
                nont_array[:,:, nont_count] = epoch
                nont_count += 1
        
        mean_target_epoch = np.mean(target_array, axis = 2)
        mean_nont_epoch = np.mean(nont_array, axis = 2)
                
        times = np.arange(1, self.epoch_len*self.sample_rate*2,2 )
        plt.plot(times[:250], mean_target_epoch[0,:250], color='red')
        plt.plot(times[:250], mean_nont_epoch[0,:250], color='blue')
        plt.show()

# if __name__ == '__main__':
#     eeg_rec = EEG_stream(sj_name = 'JJ01', path2savedata = 'C:/Users/79154/Desktop')
#     eeg_rec.record_data()























class EEG_stream2():
    def __init__(self,
                sj_name = None,
                eeg_stream_type = 'Data',
                pd_stream_name = 'NVX52_Events',
                path2savedata = None,
                path2saveevents = None,
                max_rec = 0.7, 
                num_ch = 8, 
                ):

        self.sj_name = sj_name
        self.path2savedata = path2savedata
        self.path2saveevents = path2saveevents
        self.num_ch = num_ch
        self.stop = False
        self.ix_count = 0 #for array
        self.max_rec = max_rec
        self.events = []

        print("Connection to the stream...")

        streaming = resolve_stream('type', eeg_stream_type)
        self.in_eeg = StreamInlet(streaming[0])
        self.sampling = streaming[0].nominal_srate()
        print('Nominal srate is {}'.format(self.sampling))
        print('EEG stream contains {} channels'.format(self.in_eeg.channel_count))

        if self.in_eeg.channel_count == num_ch:
            print('SUCCESS: module had been connected to the stream!')
        else:
            print('Pardonnez-moi, mes amis. Il y a du probleme C1...')

        streaming = resolve_stream('name', pd_stream_name)
        self.in_pd = StreamInlet(streaming[0])

    def create_array(self, 
                    max_rec = None, #in minutes
                    num_ch = 16,
                    memmap_name = 'eeg.mmap'
                    ):

        if max_rec is None:
            max_rec = self.max_rec
    
        rec_len = self.max_rec*60*self.sampling #mintutes to seconds, and then to samples
        dims = (int(rec_len), self.num_ch + 1)
        print ("Dimmention of EEG aray are %s" %str(dims))

        arr = np.memmap(memmap_name, dtype = 'float', mode = 'w+', shape = dims)
        arr[:,:] = np.nan
        print('Voila')
        return arr

    def fill_array(self, pre_array, data_chunk, timestamp_chunk, ix_count = None):

        if ix_count is None:
            ix_count = self.ix_count

        pre_array[ix_count:ix_count+len(data_chunk), 1:] = data_chunk
        pre_array[ix_count:ix_count+len(data_chunk), 0] = timestamp_chunk
        pre_array.flush()

    def save_data(self, array2save = None, sj_name = None):

        if sj_name is None:
            sj_name = self.sj_name 

        filename = sj_name + '_EEG_data'
        array2save = array2save[~np.isnan(array2save[:,0])] #delete all the extra elements (rows containing nans)
        np.save(os.path.join(self.path2savedata, filename), array2save)


    def record_data(self, max_rec = None):

        print('START')
        self.eeg_array = self.create_array(max_rec = max_rec)
        while self.stop == False :
            
            # print('JOPA')

            #checking whether nans keep containing in a created array. If all nans are filled with numbers, making self.stop == True and terminate iteration
            selected_nans = self.eeg_array[np.isnan(self.eeg_array)]
            is_nans_over = selected_nans.size == 0
            if is_nans_over:
                self.stop = True

            eeg_data, timestamp_eeg = self.in_eeg.pull_chunk()
            evs, timestamp_pd = self.in_pd.pull_chunk()

            if timestamp_eeg:
                try:
                    self.fill_array(self.eeg_array, eeg_data, timestamp_eeg, self.ix_count)
                    self.ix_count = self.ix_count + len(timestamp_eeg)
                except:
                    self.stop = True

            if timestamp_pd:
                self.events.append(timestamp_pd[0])
            # try:
            #     eeg_data, timestamp_eeg = self.inlet.pull_chunk()
            # except:
            #     eeg_data, timestamp_eeg = [], []
        
            # if timestamp_eeg:
            #     try:
            #         self.fill_array(self.eeg_array, eeg_data, timestamp_eeg, self.ix_count)
            #         self.ix_count = self.ix_count + len(timestamp_eeg)
            #     except:
            #         self.stop = True

            # print(self.eeg_array)
        
        print(self.events)


        self.save_data(array2save = self.eeg_array, sj_name = self.sj_name)
        print ('\n...data saved.\n Au revoir, mes amis!.\n')

        os.chdir(self.path2saveevents)
        with open (self.sj_name + '_pd.pickle', 'wb') as out:
            pickle.dump(self.events, out)

        # sys.exit()

        return self.eeg_array, self.events


if __name__ == '__main__':
    eeg_rec = EEG_stream2(sj_name = 'JJ01', path2savedata = 'C:/Users/79154/Desktop', path2saveevents= 'C:/Users/79154/Desktop')
    data, events = eeg_rec.record_data()

    print('HEY')
    eeg_prop = EEGizer(epoch_len=0.5)
    print('HOOY')
    eeg = eeg_prop.epoching(data, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0 ], events)
    print(eeg)
