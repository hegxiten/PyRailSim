import simpy
import numpy as np
import time

class one_dric:
    '''
    many trains are generated from one control point,
    here I want to output schedule of each train.
    '''

    def __init__(self, begin):
        self.all_schedule = {}
        self.begin = begin
        env = simpy.Environment()
        env.process(self.train(env))
        env.run(until=10000)

    def train(self, env):
        begin_ticks = 0
        #time.mktime(time.strptime(self.begin, "%Y-%m-%d %H:%M:%S"))
        time_ticks = begin_ticks
        number = 1
        one_schedule = {}
        one_schedule_detail = {}
        speed = {}
        distance = {}
        time = {}

        while True:
            np.random.seed()
            time[number] = 0
            speed[number] = int(np.random.normal((180/60), (60/60))) # miles per second
            headway = int(np.random.normal(15, 3))
            time_ticks += headway * 60
            time_standard = time_ticks
            #time_standard = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_ticks))

            for i in xrange(1, number+1):
                time[i] += headway * 60
                distance[i] = speed[i] * time[i]
                one_schedule_detail['speed'] = speed[i]
                one_schedule_detail['distance'] = distance[i]
                one_schedule_detail['headway'] = headway
                one_schedule[time_standard] = one_schedule_detail
                self.all_schedule[i] = one_schedule
            number += 1

            yield env.timeout(headway * 60)

    def genetate_all(self):
        return self.all_schedule




