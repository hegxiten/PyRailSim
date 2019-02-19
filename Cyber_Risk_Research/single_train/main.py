'''
BUG log
1: when headway larger than 60, there would be a bug
2: in siding, trains do not stop
'''

# single_train
import sum
import time
from sum import single_train
import matplotlib.pyplot as plt

sum.networkX_write()

start = time.clock()
a = single_train('2018-01-01 00:00:00', '2018-01-10 00:00:00', True, '2018-01-01 07:00:00', '2018-01-01 09:30:00', 23, [20, 30, 40, 60, 80, 100], [20] * 5000)
print('pure python takes {}'.format(time.clock() - start))
# print a.generate_all()

# gene = b.generate_schedule() 
# write_csv(gene)

'''
# multi_dirc
from sum import multi_dirc
a = multi_dirc('2018-01-01 00:00:00', '2018-01-02 00:00:00', 200, [50, 100, 150])
print a.generate_all()
'''