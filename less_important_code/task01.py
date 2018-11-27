import numpy as np
import matplotlib.pyplot as plt

# In order to avoid contingency and error, I repeated 1,000 simulations and got the average value
'''
interface are as follows: sampleNo is the number we repeat simulations; exp_MGT, var_MGT, exp_buffer, var_buffer is the expectation of MGT, the variance of MGT, the expectation of buffer time, the variance of buffer time. 
I make the assumption that jamming DoS lasts for X hours, and recovery needs Y hours;
'''
exp_MGT = 5000
exp_buffer = 15
var_MGT = 1500
var_buffer = 3
X = 3
Y = 2
# Some variables
sampleNo = 100
sum_MGT = 0.0
n = 0
'''
create normal distributions: MGT N(5000,1500) and variance N(15,3). Besides, all number in variance must be bigger than 3.
Assume n is the number of late trains, and V[i] is the random number in normal distributions variance N(15,3). 
(V[1]-3) + (V[2]-3) + ... + (V[n]-3) >= (X + Y) * 60
'''
while n < 1000:
    np.random.seed()
    weight = np.random.normal(exp_MGT, var_MGT, sampleNo).tolist()
    variance = np.random.normal(exp_buffer, var_buffer, sampleNo).tolist()
    traffic = 0.0
    i = 0
    while traffic < (X + Y) * 60:
        traffic = traffic + variance[i] - 3
        sum_MGT = sum_MGT + weight[i]
        i += 1
    n += 1

sum_MGT /= 1000 * 1000000

plt.subplot(141)

print 'Traffic prediction/estimation in MGT under such DoS attack is:', sum_MGT
