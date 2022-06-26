import pandas as pd

# important: the header of csv is [train, Time, Direction, Weight, headway]
# Its input data come from Class: generate_train.generate_schedule
# the tyoe of input is "dictionary"
class write_csv:
    '''
    since I want to output original schedule and delay schedule in one class,
    two "white_csv" classes are needed,
    "write_csv' output the original schedule
    and "write_csv2" output the delay schedule
    '''

    def __init__(self, In):
        self.In = In
        columns = ['train', 'time_arrival', 'time_departure', 'direction', 'weight(tons)', 'headway(mins)', 'delay(mins)', 'X+Y(hours)']
        self.dataframe = pd.DataFrame({'train': self.In[1]['index'], 'time_arrival': self.In[1]['time_arrival'], 'time_departure': self.In[1]['time_departure'], 'direction': self.In[1]['direction'], 'weight(tons)': self.In[1]['total_weight'], 'headway(mins)': self.In[1]['headway_next'], 'delay(mins)': self.In[1]['delay'], 'X+Y(hours)': self.In[1]['X+Y']}, index=[0])
        self.dataframe.to_csv("/Users/guokai/Desktop/git/Rutgers_Railway_security_research/Cyber_Risk_Research/orig_schedule.csv", index=0, sep=',', mode='w', header=1, columns=columns)
        n = 2
        while n < len(self.In):
            self.dataframe = pd.DataFrame({'train': self.In[n]['index'], 'time_arrival': self.In[n]['time_arrival'], 'time_departure': self.In[n]['time_departure'], 'direction': self.In[n]['direction'], 'weight(tons)': self.In[n]['total_weight'], 'headway(mins)': self.In[n]['headway_next'], 'delay(mins)': self.In[n]['delay'], 'X+Y(hours)': self.In[n]['X+Y']}, index=[0])
            self.dataframe.to_csv("/Users/guokai/Desktop/git/Rutgers_Railway_security_research/Cyber_Risk_Research/orig_schedule.csv", index=0, sep=',', mode='a', header=0, columns=columns)
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