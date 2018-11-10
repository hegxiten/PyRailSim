import numpy as np
import time


def train_direction(direction):
    if direction == 0:
        return 'Dic_A'
    elif direction == 1:
        return 'Dic_B'


class generate_train:
    """
    Generate N trains.
    Weight of a train is following the standard distribution of: N~(exp_MGT tons, var_MGT tons).
    Incorporate the train minimum spacing buffer: N~(exp_buffer minutes, var_buffer minutes).
    The jamming DoS lasts for X hours, and recovery needs Y hours
    """

    # the format of start and end time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    # ex:begin_time = '2016-05-05 20:28:54'
    def __init__(self, X, Y, exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, end_time):
        self.X = X
        self.Y = Y
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

    def generate_schedule(self):
        num_of_direction = 2
        n = 1
        prev_direction = 0
        schedule = ''
        weight = []
        variance = []
        # create weight and variance according to N(5000, 1500) & N(15, 3)
        np.random.seed()
        n = int(self.num_train)
        while n > 0:
            weight.append(int(np.random.normal(self.exp_MGT, self.var_MGT)))
            variance.append(int(np.random.normal(self.exp_buffer, self.var_buffer)))
            n -= 1

        while n < self.num_train:
            # train time
            ticks = self.begin
            # direction
            cur_direction = np.random.randint(0, num_of_direction)

            if cur_direction != prev_direction:
                if variance[n - 1] + variance[n] < 28:
                    ticks = ticks + (28 + 28 - variance[n - 1] - variance[n]) * 60
                else:
                    ticks = ticks + variance[n] * 60
            elif cur_direction == prev_direction:
                if (28 - variance[n - 1]) > (variance[n] - 3):
                    ticks = ticks + (28 + 3 - variance[n] - variance[n - 1]) * 60
                else:
                    ticks = ticks + variance[n] * 60
            prev_direction = cur_direction
            # fill '0' before n, ex: turn '1' into '0001'
            m = "%04d" % (n+1)
            # get the schedule of every train
            train_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(ticks))
            schedule = schedule + 'Train ' + str(m) + ' ' + str(train_time) + ' ' + \
                       train_direction(cur_direction) + ' ' + str(weight[n]) + ' ' + 'Tons' + '\n'
            n += 1
        return schedule
