#'''
# single_train
import sum
from sum import single_train
sum.networkX_write()

a = single_train('2018-01-01 00:00:00', '2018-01-03 00:00:00', [200, 400, 600, 800])
print a.generate_all()
#'''


'''
# multi_dirc
from sum import multi_dirc
a = multi_dirc('2018-01-01 00:00:00', '2018-01-02 00:00:00', 200, [50, 100, 150])
print a.generate_all()
'''