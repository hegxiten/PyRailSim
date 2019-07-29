import numpy as np
import time


def train_direction(direction):
    if direction == 0:
        return 'A'
    elif direction == 1:
        return 'B'


class generate_a_train:
    """
    Generate one train.
    Be used at class "simpy_generate_train_two_dirc"
    """

    def __init__(self, exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, cur_time, end_time, prev_dirc, prev_headway,
                 headway, number):
        self.exp_MGT = exp_MGT
        self.var_MGT = var_MGT
        self.exp_buffer = exp_buffer
        self.var_buffer = var_buffer
        self.begin_time = begin_time
        self.cur_time = cur_time
        self.end_time = end_time
        self.cur_ticks = time.mktime(time.strptime(self.cur_time, "%Y-%m-%d %H:%M:%S"))
        self.end_ticks = time.mktime(time.strptime(self.end_time, "%Y-%m-%d %H:%M:%S"))
        self.prev_dirc = prev_dirc
        self.prev_headway = prev_headway
        self.number = number
        self.dic = {}
        self.headway = headway

        num_of_direction = 2
        prev_direction = self.prev_dirc

        # create weight and variance according to N(5000, 1500) & N(15, 3)
        np.random.seed()
        weight = int(np.random.normal(self.exp_MGT, self.var_MGT))
        cur_direction = np.random.randint(0, num_of_direction)
        self.cur_dirc = cur_direction

        ticks = self.cur_ticks

        self.dic_value = {}
        # train time

        if self.number > 1:
            if cur_direction != self.prev_dirc:
                if prev_headway + headway < 28:
                    ticks = ticks + (28 + 28 - prev_headway - headway) * 60
                else:
                    ticks = ticks + prev_headway * 60
            elif cur_direction == prev_direction:
                if (28 - prev_headway) > (headway - 3):
                    ticks = ticks + (28 + 3 - headway - prev_headway) * 60
                else:
                    ticks = ticks + headway * 60

        train_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
        self.train_time = train_time

        if ticks > time.mktime(time.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")):
            return
        # fill '0' before n, ex: turn '1' into '0001'
        m = "%04d" % self.number
        # get the schedule of every train
        self.dic_value['time_arrival'] = train_time
        self.dic_value['time_departure'] = train_time
        self.dic_value['delay'] = 0
        self.dic_value['direction'] = train_direction(cur_direction)
        self.dic_value['headway_prev'] = prev_headway
        self.dic_value['headway_next'] = headway
        self.dic_value['total_weight'] = weight
        self.dic_value['index'] = m
        self.dic_value['misrouted'] = 'False'
        self.dic_value['train_type'] = 'Default'
        self.dic_value['train_length'] = None
        self.dic_value['train_speed'] = None
        self.dic_value['train_acceleration'] = None
        self.dic_value['train_deceleration'] = None
        self.dic_value['Future_parameters'] = None
        self.dic_value['X+Y'] = 0
        self.dic_value['Dos_time'] = 'null'

        self.dic[self.number] = self.dic_value

    def generate_a_train(self):
        return self.dic_value

    def get_cur_time(self):
        return self.train_time

    def get_prev_dirc(self):
        return self.cur_dirc

    def get_prev_headway(self):
        return self.headway

    def get_number(self):
        return self.number