import pandas as pd


# important: the header of csv is [train, Time, Direction, Weight, headway]
# Its input data come from Class: generate_train.generate_schedule
# the tyoe of input is "dictionary"
class XY_delay:
    'write csv'

    def __init__(self, In):
        self.In = In
        columns = ['time_departure', 'delay(mins)', 'X+Y(hours)', 'Dos_time']
        self.dataframe = pd.DataFrame({'time_departure': self.In[1]['time_departure'], 'delay(mins)': self.In[1]['delay'], 'X+Y(hours)': self.In[1]['X+Y'], 'Dos_time': self.In[1]['Dos_time']}, index=[0])
        self.dataframe.to_csv("XY_delay.csv", index=0, sep=',', mode='w', header=1, columns=columns)
        n = 2
        while n < len(self.In):
            self.dataframe = pd.DataFrame({'time_departure': self.In[n]['time_departure'], 'delay(mins)': self.In[n]['delay'], 'X+Y(hours)': self.In[n]['X+Y'], 'Dos_time': self.In[n]['Dos_time']}, index=[0])
            self.dataframe.to_csv("XY_delay.csv", index=0, sep=',', mode='a', header=0, columns=columns)
            n += 1
        print '\nNote: train_schedule.csv has been created, and the sequence of header is [train, Time, Direction, Weight, headway]'


# Code in main class:
#
#     from write_csv import write_csv
#     from generate_train import generate_train
#
#     a = generate_train(5000, 1500, 15, 3, '2016-05-05 20:28:54', '2016-05-05 23:28:54')
#     gene = a.generate_schedule()
#
#     write_csv(gene)