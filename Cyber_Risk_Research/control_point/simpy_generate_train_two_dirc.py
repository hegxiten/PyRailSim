import numpy as np
import time
import simpy
from generate_a_train import generate_a_train


def train_direction(direction):
    if direction == 0:
        return 'A'
    elif direction == 1:
        return 'B'


class simpy_generate_train_two_dirc:
    """
    Generate N trains.
    Weight of a train is following the standard distribution of: N~(exp_MGT tons, var_MGT tons).
    Incorporate the train minimum spacing buffer: N~(exp_buffer minutes, var_buffer minutes).
    The jamming DoS lasts for X hours, and recovery needs Y hours

    the format of start and end time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    ex:begin_time = '2018-01-01 00:00:00'
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
        self.dic = {}
        self.schedule = ''
        env = simpy.Environment()
        env.process(self.generate_train_two_dirc(env))
        schedule_time = self.end - self.begin
        env.run(until=schedule_time)

    def generate_train_two_dirc(self, env):
        prev_dirc = 0
        prev_headway = 15
        cur_time = self.begin_time
        number = 1

        while True:
            # create weight and variance according to N(5000, 1500) & N(15, 3)
            np.random.seed()
            headway = int(np.random.normal(self.exp_buffer, self.var_buffer))

            a = generate_a_train(self.exp_MGT, self.var_MGT, self.exp_buffer, self.var_buffer, self.begin_time,
                                 cur_time, self.end_time, prev_dirc, prev_headway, headway, number)
            prev_dirc = a.get_prev_dirc()
            prev_headway = a.get_prev_headway()
            cur_time = a.get_cur_time()
            number = a.get_number()
            self.dic[number] = a.generate_a_train()
            number += 1
            yield env.timeout(headway * 60)

    def generate_schedule(self):
        return self.dic

    def print_schedule(self):
        print self.schedule
