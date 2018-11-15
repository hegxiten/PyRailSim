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

#'''
# Class: write_csv
import pickle
from write_csv import write_csv
from write_csv2 import write_csv2
from train_delay_two_dric import train_delay_two_dric

b = train_delay_two_dric(3, 2, '2018-01-02 00:00:00')
gene1, gene2 = b.print_diff()
pickle.dump(gene2, open("pickle.txt", "w"))
write_csv(gene1)
write_csv2(gene2)
#'''

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
from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from X_Y_maxDelayNum import X_Y_maxDelayNum
from write_csv import write_csv
import csv

a = X_Y_maxDelayNum('2018-01-01 00:00:00')
gene = a.drawA_B()
write_csv(gene)
fig = plt.figure()
ax = Axes3D(fig)

X = [0, 1.1, 1.8, 3.1, 4.0]
Y = [2, 2.4, 4.3, 3.5, 2.5]
X, Y = np.meshgrid(X, Y)
Z = [2, 2.4, 4.3, 3.5, 2.5]

csvFile = open("train_schedule.csv", "r")
reader = csv.reader(csvFile)

result = {}
for item in reader:
    if reader.line_num == 1:
        continue
    X.append(item[0])
    Y.append(item[1])
    X, Y = np.meshgrid(X, Y)
    Z.append(item[2])

csvFile.close()
print(result)

ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='rainbow')

plt.draw()
plt.pause(10)
plt.savefig('3D.jpg')
plt.close()
#'''