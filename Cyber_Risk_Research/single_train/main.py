'''
BUG log
1: when headway larger than 60, there would be a bug
2: in siding, trains do not stop
'''

# single_train
import sum
from sum import single_train
import matplotlib.pyplot as plt
# from sum import write_csv

sum.networkX_write()

a = single_train('2018-01-01 00:00:00', '2018-01-05 00:00:00', False, '2018-01-01 04:00:00', '2018-01-01 07:00:00', 23, [10, 20, 30, 40], [10] * 1000)
print(a.generate_all())

# gene = b.generate_schedule() 
# write_csv(gene)

'''
# multi_dirc
from sum import multi_dirc
a = multi_dirc('2018-01-01 00:00:00', '2018-01-02 00:00:00', 200, [50, 100, 150])
print a.generate_all()
'''