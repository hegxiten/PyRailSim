#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

import threading
import logging
import time

from train import Train
from system import System
from infrastructure import Track, BigBlock


def string_diagram(frame, sys, fig, axes):
    '''To draw the string diagram based on the schedule dictionary for all the trains. 
    '''
    axes.clear()
    colors = ['red', 'green', 'blue', 'black', 'orange', 'cyan', 'magenta']
    color_num = len(colors)
    t_color = [colors[i % color_num] for i in range(len(sys.trains))]
    x, y = [], []
    for i in range(len(sys.trains)):
        x.append([
            mdates.date2num(datetime.fromtimestamp(j))
            for (j, _) in sys.trains[i].time_pos_list
        ])
        y.append([j for (_, j) in sys.trains[i].time_pos_list])
        axes.plot([
            mdates.date2num(datetime.fromtimestamp(j))
            for (j, _) in sys.trains[i].time_pos_list
        ], [j for (_, j) in sys.trains[i].time_pos_list],
                  color=t_color[i])

    # #     ===============================================================================
    #     time_length = sys.term_time - sys.init_time
    #     step_size = 10
    #     for start in range(1,time_length + 1, step_size):
    #         plt.axis([(datetime.fromtimestamp(sys.init_time - 500)), \
    #             (datetime.fromtimestamp(sys.term_time + 500)), -5 , 55])

    #         for n in range(len(x)-1):
    #             new_x_y = [[mdates.date2num(datetime.fromtimestamp(i)), j] for i, j in zip(x[n], y[n]) if i < sys.init_time + start and i > sys.init_time + start - 1 - step_size]
    #             new_x = []
    #             new_y = []
    #             for i , j in new_x_y:
    #                 new_x.append(i)
    #                 new_y.append(j)
    #             if(len(new_x) == 0):
    #                 continue
    #             plt.plot(new_x, new_y, color=t_color[n])
    #             # print('==============')
    #             # print('Length of new_x: {}'.format(len(new_x)))
    #             # print('Length of new_y: {}'.format(len(new_y)))
    #         plt.pause(0.00001)
    # #     ===============================================================================
    axes.axhspan(15, 20, color='yellow', alpha=0.5)
    axes.axhspan(30, 35, color='yellow', alpha=0.5)
    axes.axvspan((datetime.fromtimestamp(sys.init_time + 90 * 60)),
                 (datetime.fromtimestamp(sys.init_time + 150 * 60)),
                 color='black',
                 alpha=0.5)


def speed_curve(sys, train):
    '''To draw the speed curve based on a train's mileposts and speed . 
    '''
    colors = ['red', 'green', 'purple']
    mp, spd, spdlmt, tgt_spd = [], [], [], []
    for i in range(len(train.pos_spd_list)):
        mp.append(train.pos_spd_list[i][0])
        spd.append(abs(train.pos_spd_list[i][1] * 3600))
        spdlmt.append(train.pos_spd_list[i][2] * 3600)
        tgt_spd.append(train.pos_spd_list[i][3] * 3600)

    min_mp, max_mp = min(mp), max(mp)

    plt.ion()
    plt.title('Speed Curve')
    plt.xticks(rotation=90)
    plt.grid(True, linestyle="-.", color="r", linewidth="0.1")
    plt.legend()
    plt.xlabel('Mile Post/miles')
    plt.ylabel('MPH')
    plt.plot(mp, spd, color=colors[1])  # train speed
    plt.plot(mp, spdlmt, color=colors[0])  # train speed lmt
    plt.plot(mp, tgt_spd, '--', color=colors[2])  # train tgt speed

    plt.figure(figsize=(18, 16), dpi=80, facecolor='w', edgecolor='k')
    plt.rcParams['figure.dpi'] = 200
    import pylab
    pylab.rcParams['figure.figsize'] = (15.0, 8.0)
    plt.pause(0.01)
    # plt.ioff()


def simulation_setup():
    sim_init_time = datetime.strptime('2018-01-10 10:00:00',
                                      "%Y-%m-%d %H:%M:%S")
    sim_term_time = datetime.strptime('2018-01-10 15:30:00',
                                      "%Y-%m-%d %H:%M:%S")
    sp_container = [random.uniform(0.01, 0.02) for i in range(20)]
    acc_container = [
        0.5 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15)
        for i in range(20)
    ]
    dcc_container = [
        0.2 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15)
        for i in range(20)
    ]
    headway = 200 * random.random() + 400
    sys = System(sim_init_time,
                 sp_container,
                 acc_container,
                 dcc_container,
                 term_time=sim_term_time,
                 dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],
                 dos_pos=-1,
                 headway=headway,
                 refresh_time=10)
    K166 = Train(
        system=sys,
        init_time=sys.sys_time,
        init_segment=((None, None), (sys.signal_points[10], 1)),
        max_sp=sys.sp_container[sys.train_num % len(sys.sp_container)],
        max_acc=sys.acc_container[sys.train_num % len(sys.acc_container)],
        max_dcc=sys.dcc_container[sys.train_num % len(sys.dcc_container)],
        length=1)
    T166 = Train(
        system=sys,
        init_time=sys.sys_time,
        init_segment=((None, None), (sys.signal_points[10], 1)),
        max_sp=sys.sp_container[sys.train_num % len(sys.sp_container)],
        max_acc=sys.acc_container[sys.train_num % len(sys.acc_container)],
        max_dcc=sys.dcc_container[sys.train_num % len(sys.dcc_container)],
        length=1)
    K165 = Train(
        system=sys,
        init_time=sys.sys_time,
        init_segment=((None, None), (sys.signal_points[0], 0)),
        max_sp=sys.sp_container[sys.train_num % len(sys.sp_container)],
        max_acc=sys.acc_container[sys.train_num % len(sys.acc_container)],
        max_dcc=sys.dcc_container[sys.train_num % len(sys.dcc_container)],
        length=1)
    T165 = Train(
        system=sys,
        init_time=sys.sys_time,
        init_segment=((None, None), (sys.signal_points[0], 0)),
        max_sp=sys.sp_container[sys.train_num % len(sys.sp_container)],
        max_acc=sys.acc_container[sys.train_num % len(sys.acc_container)],
        max_dcc=sys.dcc_container[sys.train_num % len(sys.dcc_container)],
        length=1)
    setattr(sys, 'K166', K166)
    setattr(sys, 'T166', T166)
    setattr(sys, 'K165', K165)
    setattr(sys, 'T165', T165)
    return sys


if __name__ == "__main__":
    sys = simulation_setup()

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main    : before simulator thread starts")
    sys_launch_thread = threading.Thread(
        target=sys.launch,
        kwargs={'launch_duration': (sys.term_time - sys.init_time)})
    logging.info("Main    : before running thread")
    sys_launch_thread.start()
    logging.info("Main    : wait for the thread to finish")
    sys_launch_thread.join()
    logging.info("Main    : all done")

# https://medium.com/@grvsinghal/speed-up-your-python-code-using-multiprocessing-on-windows-and-jupyter-or-ipython-2714b49d6fac

sys.launch(launch_duration=(sys.term_time - sys.init_time))

plt.rcParams['figure.dpi'] = 100  # set the canvas dpi as 100
fig = plt.figure(figsize=(8, 6))
ax1 = fig.add_subplot(1, 1, 1)
hours = mdates.HourLocator()
minutes = mdates.MinuteLocator()
seconds = mdates.SecondLocator()
dateFmt = mdates.DateFormatter("%H:%M")
fig.suptitle('String Diagram')
ax1.xaxis.set_major_locator(hours)
ax1.xaxis.set_minor_locator(minutes)
ax1.xaxis.set_major_formatter(dateFmt)
plt.xticks(rotation=90)
plt.grid(True, linestyle="-.", color="r", linewidth="0.1")
plt.legend()
plt.xlabel('Time')
plt.ylabel('Mile Post/miles')
plt.axis([(datetime.fromtimestamp(sys.init_time - 500)),
          (datetime.fromtimestamp(sys.term_time + 500)), -5, 55])
