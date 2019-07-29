import pandas as pd


# important: the header of csv is [Train, Time, Direction, Weight, headway]
# Its input data come from Class: generate_train.generate_schedule
# the tyoe of input is "dictionary"
class max_delay:
    'write csv'

    def __init__(self, In):
        self.In = In
        columns = ['X+Y', 'delay_num']
        self.dataframe = pd.DataFrame({'X+Y': self.In[1]['X+Y'], 'delay_num': self.In[1]['delay_num']}, index=[0])
        self.dataframe.to_csv("/Users/guokai/Desktop/git/Rutgers_Railway_security_research/Cyber_Risk_Research/max_delay.csv", index=0, sep=',', mode='w', header=1, columns=columns)
        n = 2
        while n < len(self.In):
            self.dataframe = pd.DataFrame({'X+Y': self.In[n]['X+Y'], 'delay_num': self.In[n]['delay_num']}, index=[0])
            self.dataframe.to_csv("/Users/guokai/Desktop/git/Rutgers_Railway_security_research/Cyber_Risk_Research/max_delay.csv", index=0, sep=',', mode='a', header=0, columns=columns)
            n += 1
        print '\nNote: train_schedule.csv has been created, and the sequence of header is [Train, Time, Direction, Weight, headway]'


# Code in main class:
#
#     from write_csv import write_csv
#     from generate_train import generate_train
#
#     a = generate_train(5000, 1500, 15, 3, '2016-05-05 20:28:54', '2016-05-05 23:28:54')
#     gene = a.generate_schedule()
#
#     write_csv(gene)