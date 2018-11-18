# from aetypes import end
# removed the outdated lib

import numpy as np
import time

# In order to avoid contingency and error, I repeated 1,000 simulations and got the average value
'''
interface are as follows: sampleNo is the number we repeat simulations; exp_MGT, var_MGT, exp_buffer, var_buffer is the expectation of MGT, the variance of MGT, the expectation of buffer time, the variance of buffer time. 
I make the assumption that jamming DoS lasts for X hours, and recovery needs Y hours;
'''
exp_MGT = 5000
exp_buffer = 15
var_MGT = 1500
var_buffer = 3
task_num = input('Please input the task number: ')
if task_num == 1 or task_num == 3:
    X = input('How many hours jamming DoS lasts: X=')
    Y = input('How many hours recovery needs: Y=')
if task_num == 4:
    err_train = input('Which number of train get in to the wrong way(from 1 to 50): ')

# Some variables
sampleNo = 100
sum_MGT = 0.0
n = 0
traffic = 0
num_of_direction = task_num
if num_of_direction == 3:
    num_of_direction += 1
'''
create normal distributions: MGT N(5000,1500) and variance N(15,3). Besides, all number in variance must be bigger than 3.
Assume n is the number of late trains, and V[i] is the random number in normal distributions variance N(15,3). 
(V[1]-3) + (V[2]-3) + ... + (V[n]-3) >= (X + Y) * 60
'''


def train_direction(direction):
    if direction == 0:
        return 'Eastbound '
    elif direction == 1:
        return 'Westbound '
    elif direction == 2:
        return 'Northbound'
    elif direction == 3:
        return 'Southbound'


np.random.seed()
weight = np.random.normal(exp_MGT, var_MGT, sampleNo).tolist()
variance = np.random.normal(exp_buffer, var_buffer, sampleNo).tolist()
prev_direction = 0
prev_prev_direction = 0
ticks = time.time()

while n < 50:
    next_direction = np.random.randint(0, num_of_direction)
    if next_direction != prev_direction:
        # if AB | BA | CD | DC
        if prev_direction + next_direction == 1 or prev_direction + next_direction == 5:
            # if current train has diff direction with prev
            if next_direction != prev_direction:
                if variance[n - 1] + variance[n] < 28:
                    ticks = ticks + (28 + 28 - variance[n - 1] - variance[n]) * 60
                else:
                    ticks = ticks + variance[n] * 60
            # if current train has same direction with prev
            elif next_direction == prev_direction:
                if (28 - variance[n - 1]) > (variance[n] - 3):
                    ticks = ticks + (28 + 3 - variance[n] - variance[n - 1]) * 60
                else:
                    ticks = ticks + variance[n] * 60
        # if AC | BD
        if prev_direction + next_direction == 2 or prev_direction + next_direction == 4:
            ticks = ticks
    # if (BC | CB | AD | DA) or (AA | BB | CC | DD)
    elif next_direction == prev_direction or prev_direction + next_direction == 3:
        if int(variance[n]) > 3:
            ticks = ticks + int(variance[n]) * 60
        else:
            ticks = ticks + 3 * 60

    if task_num == 1 or task_num == 3:
        traffic = 0.0
        i = 0
        while traffic < (X + Y) * 60:
            traffic = traffic + variance[i] - 3
            sum_MGT = sum_MGT + weight[i]
            i += 1

    prev_prev_direction = prev_direction
    prev_direction = next_direction
    n += 1

    if task_num == 4:
        if n == err_train:
            ticks = ticks + 2 * 60 * 60
            print ('\nThere is a 2 hours break because of cyber attack.\n')
    if task_num != 1:
        train_time = time.strftime("%Y.%m.%d %H:%M", time.localtime(ticks))
        print 'Train', n, train_time, train_direction(next_direction), int(weight[n]), 'Tons'


if task_num == 1 or task_num == 3:
    sum_MGT /= 50 * 1000000
    print '\nTraffic prediction/estimation in MGT under such DoS attack is:', sum_MGT
