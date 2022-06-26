from aetypes import end

import numpy as np
import matplotlib.pyplot as plt
import time

# In order to avoid contingency and error, I repeated 1,000 simulations and got the average value
'''
interface are as follows: sampleNo is the number we repeat simulations; exp_weight, var_weight, exp_buffer, var_buffer is the expectation of train weight, the variance of train weight, the expectation of buffer time, the variance of buffer time. 
I make the assumption that jamming DoS lasts for X hours, and recovery needs Y hours;
'''
exp_MGT = 5000
exp_buffer = 15
var_MGT = 1500
var_buffer = 3
num_of_direction = 2
X = 3
Y = 2

# Some variables
sampleNo = 100
sum_MGT = 0.0
n = 1
prev_direction = 0
'''
create normal distributions: MGT N(5000,1500) and variance N(15,3). Besides, all number in variance must be bigger than 3.
Assume n is the number of late trains, and V[i] is the random number in normal distributions variance N(15,3). 
(V[1]-3) + (V[2]-3) + ... + (V[n]-3) >= (X + Y) * 60
'''


def train_direction(direction):
    if direction == 0:
        return 'Eastbound'
    elif direction == 1:
        return 'Westbound'


while n <= 50:
    np.random.seed()
    weight = np.random.normal(exp_MGT, var_MGT, sampleNo).tolist()
    variance = np.random.normal(exp_buffer, var_buffer, sampleNo).tolist()

    next_direction = np.random.randint(0, num_of_direction)
    ticks = time.time()

    if next_direction != prev_direction:
        if variance[n - 1] + variance[n] < 28:
            ticks = ticks + (28 + 28 - variance[n - 1] - variance[n]) * 60
        else:
            ticks = ticks + variance[n] * 60
    elif next_direction == prev_direction:
        if (28 - variance[n - 1]) > (variance[n] - 3):
            ticks = ticks + (28 + 3 - variance[n] - variance[n - 1]) * 60
        else:
            ticks = ticks + variance[n] * 60

    prev_direction = next_direction
    n += 1

    train_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(ticks))
    print 'train', n-1, train_time, train_direction(next_direction), int(weight[n]), 'Tons'

