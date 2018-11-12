
# Class: train_delay
from train_delay_two_dric import train_delay
a = train_delay(3, 2, '2016-05-05 20:28:54')
a.print_diff()



'''
# Class: generate_train
from generate_train import generate_train
a = generate_train(5000, 1500, 15, 3, '2016-05-05 20:28:54', '2016-05-05 23:28:54')
print a.print_schedule()
'''

'''
# Class: write_csv
from write_csv import write_csv
from generate_train import generate_train

a = generate_train(5000, 1500, 15, 3, '2016-05-05 20:28:54', '2016-05-05 23:28:54')
gene = a.generate_schedule()

write_csv(gene)
'''