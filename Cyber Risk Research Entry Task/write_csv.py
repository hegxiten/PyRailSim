import pandas as pd


# important: the header of csv is [Train, Time, Direction, Weight, Time buffer]
# Its input data come from Class: generate_train.generate_schedule
# the tyoe of input is "dictionary"
class write_csv:
    'write csv'

    def __init__(self, In):
        self.In = In
        columns = ['Train', 'Time', 'Direction', 'Weight(tons)', 'Time buffer(mins)']
        self.dataframe = pd.DataFrame({'Train': self.In[0][0], 'Time': self.In[0][1], 'Direction': self.In[0][2], 'Weight(tons)': self.In[0][3], 'Time buffer(mins)': self.In[0][4]}, index=[0])
        self.dataframe.to_csv("/Users/guokai/PycharmProjects/ATCS_task/train_schedule.csv", index=0, sep=',', mode='a', header=1, columns=columns)
        n = 1
        while n < len(self.In):
            self.dataframe = pd.DataFrame({'Train': self.In[n][0], 'Time': self.In[n][1], 'Direction': self.In[n][2], 'Weight(tons)': self.In[n][3], 'Time buffer(mins)': self.In[n][4]}, index=[0])
            self.dataframe.to_csv("/Users/guokai/PycharmProjects/ATCS_task/train_schedule.csv", index=0, sep=',', mode='a', header=0, columns=columns)
            n += 1
        print '\nNote: train_schedule.csv has been created, and the sequence of header is [Train, Time, Direction, Weight, Time buffer]'


# Code in main class:
#
#     from write_csv import write_csv
#     from generate_train import generate_train
#
#     a = generate_train(5000, 1500, 15, 3, '2016-05-05 20:28:54', '2016-05-05 23:28:54')
#     gene = a.generate_schedule()
#
#     write_csv(gene)