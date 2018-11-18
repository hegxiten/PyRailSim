from train_delay_one_dric import train_delay_one_dric
from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import csv


fig = plt.figure()
ax = Axes3D(fig)

list_delayNum = []
for X in range(0, 20):
    Ya = []
    for Y in range(0, 20):
        a = train_delay_one_dric(X, Y, '2018-01-02 00:00:00')
        b, c, d = a.print_diff()
        Ya.append(d)
    list_delayNum.append(Ya)
print np.array(list_delayNum)


listX = np.arange(0, 20)
listY = np.arange(0, 20)
#listX, listY = np.meshgrid(listX, listY)
print np.meshgrid(listX, listY)

#Z = list_delayNum
Z = np.array(list_delayNum)

ax.plot_surface(listX, listY, Z, rstride=1, cstride=1, cmap='rainbow') #, cmap='rainbow'

plt.show()