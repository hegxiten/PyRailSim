import numpy as np
from collections import defaultdict


class train_delay:
    'delay'

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def print_diff(self):
        # some interfaces
        exp_MGT = 5000
        exp_buffer = 15
        var_MGT = 1500
        var_buffer = 3

        # Some variables
        sampleNo = 100
        sum_MGT = 0.0

        # create weight and variance according to N(5000, 1500) & N(15, 3)
        weight = np.random.normal(exp_MGT, var_MGT, sampleNo).tolist()
        variance = np.random.normal(exp_buffer, var_buffer, sampleNo).tolist()

        # transfer str into int, store it into map
        temp = 0
        i = 0
        d = defaultdict(list)
        while i < 50:
            w = int(weight[i])
            d[i].append(w)
            v = int(variance[i])
            temp = temp + v
            d[i].append(temp)
            i += 1
        print d

        # get the number of trains which delayed
        i = 0
        np.random.seed()
        traffic = 0.0
        while traffic < (self.X + self.Y) * 60:
            traffic = traffic + variance[i] - 3
            sum_MGT = sum_MGT + weight[i]
            i += 1

        # after Dos attack, the schedule of trains
        n = 0
        e = defaultdict(list)
        while n <= i:
            e[n].append(d[n][0])
            e[n].append((self.X + self.Y) * 60 + 3 * n)
            n += 1
        print e

        # print delay result
        n = 0
        while n < i:
            print 'Train', n + 1, 'was delayed', e[n][1] - d[n][1], 'mins.'
            n += 1
