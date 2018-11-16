from train_delay_one_dric import train_delay_one_dric
from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import csv

class X_Y_maxDelayNum:
    'delay 1 dric'

    # the format of DoS time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    # ex: DoS_time = '2016-05-05 20:28:54'
    def __init__(self, DoS_time):
        self.DoS_time = DoS_time

    def drawA_B(self):
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
        print Z

        ax.plot_surface(listX, listY, Z, rstride=1, cstride=1) #, cmap='rainbow'

        plt.show()