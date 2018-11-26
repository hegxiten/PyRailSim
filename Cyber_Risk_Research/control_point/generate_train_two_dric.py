import numpy as np
import time
import simpy


def train_direction(direction):
    if direction == 0:
        return 'A'
    elif direction == 1:
        return 'B'


class generate_train_two_dric:
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
        self.map = {}
        self.schedule = ''

    # def generate_train_two_dric(self, env):
        num_of_direction = 2
        prev_direction = 0
        weight = []
        variance = []


        # create weight and variance according to N(5000, 1500) & N(15, 3)
        np.random.seed()
        n = int(self.num_train) + 100
        while n >= 0:
            weight.append(int(np.random.normal(self.exp_MGT, self.var_MGT)))
            variance.append(int(np.random.normal(self.exp_buffer, self.var_buffer)))
            n -= 1

        ticks = self.begin
        n = 0
        while 1:
            map_value = {}
            # train time
            map_value['departure_ticks'] = (ticks - self.begin) / 60
            train_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
            # direction
            cur_direction = np.random.randint(0, num_of_direction)
            if n > 0:
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
            m = "%04d" % (n + 1)
            # get the schedule of every train
            map_value['time_arrival'] = train_time
            map_value['time_departure'] = train_time
            map_value['delay'] = 0
            map_value['direction'] = train_direction(cur_direction)
            map_value['headway_prev'] = variance[n - 1]
            map_value['headway_next'] = variance[n]
            map_value['total_weight'] = weight[n]
            map_value['index'] = m
            map_value['misrouted'] = 'False'
            map_value['train_type'] = 'Default'
            map_value['train_length'] = None
            map_value['train_speed'] = None
            map_value['train_acceleration'] = None
            map_value['train_deceleration'] = None
            map_value['Future_parameters'] = None
            map_value['X+Y'] = 0
            map_value['Dos_time'] = 'null'

            self.map[n+1] = map_value
            if n == 0:
                map_value['headway_prev'] = None
            # self.schedule = self.schedule + 'Train ' + str(self.map[n][0]) + ' ' + str(self.map[n][1]) + ' ' + \
            #                 self.map[n][2] + ' ' + str(self.map[n][3]) + ' ' + 'Tons' + '\n'
            n += 1
            if ticks > time.mktime(time.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")):
                break
        # env = simpy.Environment()
        # env.process(self.generate_train_two_dric(env))
        # env.run(until=15)

    def generate_schedule(self):
        return self.map

    def print_schedule(self):
        print self.schedule
