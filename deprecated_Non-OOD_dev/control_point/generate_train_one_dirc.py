import numpy as np
import time


def train_direction(direction):
    if direction == 0:
        return 'dirc_A'
    elif direction == 1:
        return 'dirc_B'


class generate_train_one_dirc:
    """
    Generate N trains.
    Weight of a train is following the standard distribution of: N~(exp_MGT tons, var_MGT tons).
    Incorporate the train minimum spacing buffer: N~(exp_buffer minutes, var_buffer minutes).
    The jamming DoS lasts for X hours, and recovery needs Y hours

    the format of start and end time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    ex:begin_time = '2016-05-05 20:28:54'
    """

    def __init__(self, exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, end_time):
        self.exp_MGT = exp_MGT
        self.var_MGT = var_MGT
        self.exp_buffer = exp_buffer
        self.var_buffer = var_buffer
        self.begin_time = begin_time
        self.end_time = end_time
        self.begin = time.mktime(time.strptime(self.begin_time, "%Y-%m-%d %H:%M:%S"))
        self.end = time.mktime(time.strptime(self.end_time, "%Y-%m-%d %H:%M:%S"))
        self.num_train = (self.end - self.begin) / 60 / self.exp_buffer
        self.direction = np.random.randint(0, self.num_train)
        self.dic = {}
        self.schedule = ''
        num_of_direction = 2
        prev_direction = 0
        weight = []
        variance = []
        # create weight and variance according to N(5000, 1500) & N(15, 3)
        np.random.seed()
        n = int(self.num_train)
        while n > 0:
            weight.append(int(np.random.normal(self.exp_MGT, self.var_MGT)))
            variance.append(int(np.random.normal(self.exp_buffer, self.var_buffer)))
            n -= 1
        ticks = self.begin - variance[0] * 60

        while n < self.num_train:
            dic_value = {}
            # train time

            ticks = ticks + variance[n] * 60
            # fill '0' before n, ex: turn '1' into '0001'
            m = "%04d" % (n + 1)
            # get the schedule of every train
            train_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
            dic_value['time_arrival'] = train_time
            dic_value['time_departure'] = train_time
            dic_value['delay'] = 0
            dic_value['direction'] = 'A'
            dic_value['headway_prev'] = variance[n - 1]
            dic_value['headway_next'] = variance[n]
            dic_value['total_weight'] = weight[n]
            dic_value['index'] = m
            dic_value['misrouted'] = 'False'
            dic_value['train_type'] = 'Default'
            dic_value['train_length'] = None
            dic_value['train_speed'] = None
            dic_value['train_acceleration'] = None
            dic_value['train_deceleration'] = None
            dic_value['Future_parameters'] = None
            dic_value['X+Y'] = 'null'
            dic_value['Dos_time'] = 'null'
            dic_value['max_delay'] = 'null'
            self.dic[n + 1] = dic_value
            #self.schedule = self.schedule + 'Train ' + str(self.dic[n][0]) + ' ' + str(self.dic[n][1]) + ' ' + self.dic[n][2] + ' ' + str(self.dic[n][3]) + ' ' + 'Tons' + '\n'
            n += 1
        # for i in range(len(self.dic)):
        #     print self.dic[i+2]


    def generate_schedule(self):
        return self.dic

    def print_schedule(self):
        print self.schedule
