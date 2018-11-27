'''
# Class: train_delay_one_dric
from train_delay_one_dric import train_delay_one_dric
a = train_delay_one_dric(3, 2, '2018-01-02 00:00:00')
a.print_diff()
'''

'''
# Class: train_delay_two_dric
from train_delay_two_dric import train_delay
a = train_delay(3, 2, '2018-01-03 00:00:00')
a.print_diff()
'''


'''
# Class: generate_train
from generate_train import generate_train
a = generate_train(5000, 1500, 15, 3, '2018-01-01 00:00:00', '2019-01-01 00:00:00')
print a.print_schedule()
'''

'''
# Class: write_csv
import pickle
from write_csv import write_csv
from write_csv2 import write_csv2
from train_delay_two_dric import train_delay_two_dric

b = train_delay_two_dric(3, 2, '2018-01-02 00:00:00')
gene1, gene2 = b.print_diff()
#pickle.dump(gene2, open("pickle.txt", "w"))
write_csv(gene1)
write_csv2(gene2)
'''

'''
from write_csv_delay import write_csv_delay
from generate_train import generate_train
from train_delay_two_dric import train_delay

a = generate_train(5000, 1500, 15, 3, '2018-01-01 00:00:00', '2018-02-01 00:00:00')
gene = a.generate_schedule()
print(len(gene))

write_csv_delay(gene)

a = train_delay(3, 2, '2018-01-02 00:00:00')
a.print_diff()
#write_csv(gene, int(gene[1][0]), len(gene), 'update')

'''

'''
from X_Y_maxDelayNum import X_Y_maxDelayNum
a = X_Y_maxDelayNum('2018-01-02 00:00:00')
a.drawA_B()
#'''

'''
# Class: (X+Y)_(delay)
import pickle
from max_delay import max_delay
from xy_maxdelay import xy_maxdelay

b = xy_maxdelay(3, 2, '2018-01-02 00:00:00')
a = b.print_diff()
#pickle.dump(gene2, open("pickle.txt", "w"))
max_delay(a)
'''

'''
from networkX import drawnet
a = drawnet()

'''

'''
from generate_train_one_dric import generate_train_one_dric
a = generate_train_one_dric(1500,500,15,3,'2018-01-01 00:00:00','2018-01-02 00:00:00')
b = a.generate_schedule()
print b
'''

#'''
from simpy_generate_train_two_dric import simpy_generate_train_two_dric
a = simpy_generate_train_two_dric(5000,1500,15,3,'2018-01-01 00:00:00','2018-01-01 03:00:00')
b = a.generate_schedule()
print b
#'''