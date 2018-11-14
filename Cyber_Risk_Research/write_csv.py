import pandas as pd


# important: the header of csv is [Train, Time, Direction, Weight, headway]
# Its input data come from Class: generate_train.generate_schedule
# the tyoe of input is "dictionary"
class write_csv:
    'write csv'

    def __init__(self, In):
        self.In = In
        columns = ['Train', 'Time', 'Direction', 'Weight(tons)', 'headway(mins)', 'delay(mins)']
        self.dataframe = pd.DataFrame({'Train': self.In[1]['index'], 'Time': self.In[1]['time_departure'], 'Direction': self.In[1]['direction'], 'Weight(tons)': self.In[1]['total_weight'], 'headway(mins)': self.In[1]['headway_next'], 'delay(mins)': self.In[1]['delay']}, index=[0])
        self.dataframe.to_csv("/Users/guokai/Desktop/git/Rutgers_Railway_security_research/Cyber_Risk_Research/train_schedule.csv", index=0, sep=',', mode='w', header=1, columns=columns)
        n = 2
        while n < len(self.In):
            self.dataframe = pd.DataFrame({'Train': self.In[n]['index'], 'Time': self.In[n]['time_departure'], 'Direction': self.In[n]['direction'], 'Weight(tons)': self.In[n]['total_weight'], 'headway(mins)': self.In[n]['headway_next'], 'delay(mins)': self.In[n]['delay']}, index=[0])
            self.dataframe.to_csv("/Users/guokai/Desktop/git/Rutgers_Railway_security_research/Cyber_Risk_Research/train_schedule.csv", index=0, sep=',', mode='a', header=0, columns=columns)
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