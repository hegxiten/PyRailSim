#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('D:\\Users\\Hegxiten\\workspace\\Rutgers_Railway_security_research\\OOD_Train')

from infrastructure import Track, BigBlock
from system import System
from train import Train
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import numpy as np
import time
from signaling import Signal
import random

def string_diagram(sys, sys_dos, start_time, end_time):
    '''To draw the string diagram based on the schedule dictionary for all the trains. 
    '''
    colors = ['red','green','blue','black','orange','cyan','magenta']
    color_num = len(colors)
    x, y = process_data(sys)
    x_dos, y_dos = process_data(sys_dos)
    
    t_color = [colors[x.index(i)%color_num] for i in x]
    
    #plt.ion()
    plt.title('Stringline Diagram', size=35)
    hours = mdates.HourLocator()
    minutes = mdates.MinuteLocator()
    seconds = mdates.SecondLocator()
    dateFmt = mdates.DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_locator(hours)
    plt.gca().xaxis.set_minor_locator(minutes)
    plt.gca().xaxis.set_major_formatter(dateFmt)
    plt.xticks(rotation=90)
    plt.grid(color = "black")
    plt.legend()
    plt.xlabel('Time', size=30)
    plt.ylabel('Mile Post/miles',size=30)
    plt.tick_params(labelsize=23)
    start_time = int(start_time.timestamp())
    end_time = int(end_time.timestamp())

    sys_length = sys.block_intervals[-1][1]
    multi_track_blk_intervals = []
    for i,blk in enumerate(sys.blocks):
        if blk.track_number > 1:
            multi_track_blk_intervals.append(sys.block_intervals[i])

    dos_period = sys_dos.dos_period
    dos_interval = sys_dos.block_intervals[sys_dos.dos_pos]
    dos_period_ratio = [(dos_period[0] - start_time) / (end_time - start_time), (dos_period[1] - start_time) / (end_time - start_time)]
    
    plt.axis([(datetime.fromtimestamp(start_time)), \
            (datetime.fromtimestamp(end_time)), 0 , sys_length])

    

    plt.gca().axhspan(15,20,color='yellow',alpha=0.5)
    plt.gca().axhspan(30,35,color='yellow',alpha=0.5)
    #plt.gca().axvspan((datetime.fromtimestamp(start_time + 90 * 60)),(datetime.fromtimestamp(start_time + 150 * 60)),color='black',alpha=0.5)
    labels, label_colors = ['Siding Location'], ['yellow']
    #用label和color列表生成mpatches.Patch对象，它将作为句柄来生成legend
    patches = [mpatches.Patch(color=label_colors[i], label="{:s}".format(labels[i])) for i in range(len(label_colors)) ] 
    ax=plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width , box.height* 0.8])
    #下面一行中bbox_to_anchor指定了legend的位置
    ax.legend(handles=patches, bbox_to_anchor=(0.85,0.94), ncol=1) #生成legend    
    for n in range(len(x)-1):   
    #     #assert len(x[n]) == len(y[n]) == t_color[n]
        plt.plot([mdates.date2num(i) for i in x[n]], y[n],  color=t_color[n], alpha=0.5)
    # for n in range(len(x_dos) - 1):
    #     plt.plot([mdates.date2num(i) for i in x_dos[n]], y_dos[n], color=t_color[n])
    
    plt.gca().axhspan(dos_interval[0],dos_interval[1], dos_period_ratio[0], dos_period_ratio[1], color='blue',alpha=0.5)
    for mtbi in multi_track_blk_intervals:
        plt.gca().axhspan(mtbi[0],mtbi[1], color='yellow',alpha=0.5)

    plt.show()

from infrastructure import Track,BigBlock
from system import System
from train import Train
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
def string_diagram(sys, start_time, end_time):
    '''To draw the string diagram based on the schedule dictionary for all the trains. 
    '''
    colors = ['red','green','blue','black','orange','cyan','magenta']
    color_num = len(colors)
    x, y = [], []
    for i in range(len(sys.trains)):
        x.append([])
        y.append([])
        for j in range(len(sys.trains[i].time_pos_list)):
            x[i].append(datetime.fromtimestamp(sys.trains[i].time_pos_list[j][0]))
            y[i].append(sys.trains[i].time_pos_list[j][1])
            # x[i].append(sys.trains[i].time_pos_list[j][0])
            # y[i].append(sys.trains[i].time_pos_list[j][1])

    assert len(x) == len(y)
    for i in range(len(x)):
        assert len(x[i]) == len(y[i])
    train_idx = list(range(len(x)))
    t_color = [colors[x.index(i)%color_num] for i in x]
    min_t, max_t = min([i[0] for i in x if i]), max([i[-1] for i in x if i])
    
    #plt.ion()
    plt.title('String Diagram')
    hours = mdates.HourLocator()
    minutes = mdates.MinuteLocator()
    seconds = mdates.SecondLocator()
    dateFmt = mdates.DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_locator(hours)
    plt.gca().xaxis.set_minor_locator(minutes)
    plt.gca().xaxis.set_major_formatter(dateFmt)
    plt.xticks(rotation=90)
    plt.grid(True, linestyle = "-.", color = "r", linewidth = "0.1")
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Mile Post/miles')
    start_time = int(start_time.timestamp())
    end_time = int(end_time.timestamp())
    plt.axis([(datetime.fromtimestamp(start_time - 500)), \
            (datetime.fromtimestamp(end_time + 500)), -5 , 55])
    #===============================================================================
    # time_length = end_time - start_time
    # step_size = 10
    # for start in range(1,time_length + 1, step_size):
    #     plt.axis([(datetime.fromtimestamp(start_time - 500)), \
    #         (datetime.fromtimestamp(end_time + 500)), -5 , 55])
         
    #     for n in range(len(x)-1):
    #         new_x_y = [[mdates.date2num(datetime.fromtimestamp(i)), j] for i, j in zip(x[n], y[n]) if i < start_time + start and i > start_time + start - 1 - step_size]
    #         new_x = []
    #         new_y = []
    #         for i , j in new_x_y:
    #             new_x.append(i)
    #             new_y.append(j)
    #         if(len(new_x) == 0):
    #             continue
    #         plt.plot(new_x, new_y, color=t_color[n])
    #         # print('==============')
    #         # print('Length of new_x: {}'.format(len(new_x)))
    #         # print('Length of new_y: {}'.format(len(new_y)))
    #     plt.pause(0.00001)
    #===============================================================================
    for n in range(len(x)):
        #assert len(x[n]) == len(y[n]) == t_color[n]
        plt.plot([mdates.date2num(i) for i in x[n]], y[n], color=t_color[n])
    plt.gca().axhspan(15,20,color='yellow',alpha=0.5)
    plt.gca().axhspan(30,35,color='yellow',alpha=0.5)
#     plt.gca().axvspan((datetime.fromtimestamp(start_time + 90 * 60)),(datetime.fromtimestamp(start_time + 150 * 60)),color='black',alpha=0.5)
    plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
    plt.rcParams['figure.dpi'] = 200
    import pylab; pylab.rcParams['figure.figsize'] = (15.0, 8.0)
    plt.show()
    #plt.ioff()
def speed_curve(sys, train):
    '''To draw the speed curve based on a train's mileposts and speed . 
    '''
    colors = ['red','green','purple']
    mp, spd, spdlmt, tgt_spd = [], [], [], []
    for i in range(len(train.pos_spd_list)):
        mp.append(train.pos_spd_list[i][0])
        spd.append(abs(train.pos_spd_list[i][1]*3600))
        spdlmt.append(train.pos_spd_list[i][2]*3600)
        tgt_spd.append(train.pos_spd_list[i][3]*3600)

    min_mp, max_mp = min(mp), max(mp)
    
    #plt.ion()
    plt.title('Speed Curve')
    plt.xticks(rotation=90)
    plt.grid(True, linestyle = "-.", color = "r", linewidth = "0.1")
    plt.legend()
    plt.xlabel('Mile Post/miles')
    plt.ylabel('MPH')
    plt.scatter(mp, spd, color=colors[1])  # train speed
    plt.scatter(mp, spdlmt, color=colors[0])  # train speed lmt
    plt.scatter(mp, tgt_spd, color=colors[2])  # train tgt speed
    
    plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
    plt.rcParams['figure.dpi'] = 200
    import pylab; pylab.rcParams['figure.figsize'] = (15.0, 8.0)
    plt.show()
    #plt.ioff()


def process_data(sys):
    x = []; y = []; 
    for i in range(len(sys.trains)-1):
        x.append([])
        y.append([])
        for j in range(len(sys.trains[i].time_pos_list)-1):
            x[i].append(datetime.fromtimestamp(sys.trains[i].time_pos_list[j][0]))
            y[i].append(sys.trains[i].time_pos_list[j][1])
            # x[i].append(sys.trains[i].time_pos_list[j][0])
            # y[i].append(sys.trains[i].time_pos_list[j][1])

    y = [i for _,i in sorted(zip([i[0] for i in x], y))]
    x = sorted(x, key = lambda x: x[0])
    assert len(x) == len(y)
    return x, y

def cal_delay(sys, sys_dos, delay_miles):
    x_sys = []
    y_sys = []

    no_delay_sorted_train = sorted(sys.trains, key=lambda train: train.train_idx)
    for i in range(len(no_delay_sorted_train)-1):
        x_sys.append([])
        y_sys.append([])
        for j in range(len(no_delay_sorted_train[i].time_pos_list)-1):
            x_sys[i].append(datetime.fromtimestamp(no_delay_sorted_train[i].time_pos_list[j][0]))
            y_sys[i].append(no_delay_sorted_train[i].time_pos_list[j][1])

    assert len(x_sys) == len(y_sys)

    x_sys_dos = []
    y_sys_dos = []
    delay_sorted_train = sorted(sys_dos.trains, key=lambda train: train.train_idx)
    for i in range(len(delay_sorted_train)-1):
        x_sys_dos.append([])
        y_sys_dos.append([])
        for j in range(len(delay_sorted_train[i].time_pos_list)-1):
            x_sys_dos[i].append(datetime.fromtimestamp(delay_sorted_train[i].time_pos_list[j][0]))
            y_sys_dos[i].append(delay_sorted_train[i].time_pos_list[j][1])

    assert len(x_sys_dos) == len(y_sys_dos)

    delay = []
    for i in range(len(x_sys) if len(x_sys) < len(x_sys_dos) else len(x_sys_dos)):
        time = x_sys[i]
        pos = y_sys[i]
        deley_idx = 0
        for j in range(len(pos)):
            if pos[j] > delay_miles:
                deley_idx = j
                break
        no_delay_time = time[deley_idx]

        time = x_sys_dos[i]
        pos = y_sys_dos[i]
        deley_idx = 0
        for j in range(len(pos)):
            if pos[j] > delay_miles:
                deley_idx = j
                break
        delay_time = time[deley_idx]
        delay.append(delay_time - no_delay_time if delay_time > no_delay_time else no_delay_time - delay_time)

    return delay

def first_delay_train_idx(delay):
    res = -1
    for i,d in enumerate(delay):
        if d.total_seconds() != 0:
            res = i
            break
    return res

def cal_delay_avg(delay):
    sum = 0
    for d in delay:
        sum += d.total_seconds()
    return time.strftime('%H:%M:%S', time.gmtime(sum / len(delay)))

def main():
    sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
    sim_term_time = datetime.strptime('2018-01-10 15:30:00', "%Y-%m-%d %H:%M:%S")
    sp_container = [random.uniform(0.005, 0.025) for i in range(20)]
    acc_container = [random.uniform(2.78e-05*0.85 * 2, 2.78e-05*1.15*2) for i in range(20)]
    headway = 200 * random.random() + 400
    sys = System(sim_init_time, sp_container, acc_container,
                 dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],  
                 headway=headway, 
                 tracks=[1,1,1,2,1,1,2,1,1,1], 
                 dos_pos=-1)
    sys_dos = System(sim_init_time, sp_container, acc_container,
                 dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],  
                 headway=headway, 
                 tracks=[1,1,1,2,1,1,2,1,1,1], 
                 dos_pos=4)
    sim_timedelta = sim_term_time - sim_init_time
    i = 0
    while (datetime.fromtimestamp(sys.sys_time) - sim_init_time).total_seconds() < sim_timedelta.total_seconds():
        i += 1
        sys.refresh()
        sys_dos.refresh()

    delay = cal_delay(sys, sys_dos, 20)
    print("Test case 1, train delays = {}".format([d.total_seconds() for d in delay]))
    first_delay_train = first_delay_train_idx(delay)
    print("Test case 1, first delayed train = {}".format(first_delay_train))
    delay_avg = cal_delay_avg(delay)
    print("Test case 1, delay_avg = {}".format(delay_avg))
    
    print("Slowest Train Speed = {} mph".format(min(sp_container)*3600))
    print("Fastest Train Speed = {} mph".format(max(sp_container)*3600))
    print("Minimum Train Acc = {} mph/min".format(min(acc_container)*3600*60))
    print("Maximum Train Acc = {} mph/min".format(max(acc_container)*3600*60))

    
    string_diagram(sys, sys_dos, sim_init_time, sim_term_time)

if __name__ == '__main__':
    sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
    sim_term_time = datetime.strptime('2018-01-10 15:30:00', "%Y-%m-%d %H:%M:%S")
    sp_container = [random.uniform(0.01, 0.02) for i in range(20)]
    acc_container = [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
    dcc_container = [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
    headway = 200 * random.random() + 400
    sys = System(sim_init_time, sp_container, acc_container, dcc_container,
                dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],  
                dos_pos=-1,
                headway=headway, 
                refresh_time=1)

    # K166 = Train(idx=sys.train_num, 
    #                   rank=sys.train_num, 
    #                   system=sys, 
    #                   init_time=sys.sys_time, 
    #                   init_segment=((sys.signal_points[1],1), (sys.signal_points[2], 0)),
    #                   max_sp=sys.sp_container[sys.train_num % len(sys.sp_container)], 
    #                   max_acc=sys.acc_container[sys.train_num % len(sys.acc_container)], 
    #                   max_dcc=sys.dcc_container[sys.train_num % len(sys.dcc_container)])

    T166 = Train(idx=sys.train_num, 
                    rank=sys.train_num, 
                    system=sys, 
                    init_time=sys.sys_time, 
                    init_segment=((None, None),(sys.signal_points[10],1)),
                    max_sp=sys.sp_container[sys.train_num % len(sys.sp_container)], 
                    max_acc=sys.acc_container[sys.train_num % len(sys.acc_container)], 
                    max_dcc=sys.dcc_container[sys.train_num % len(sys.dcc_container)],
                    length=1)

    T165 = Train(idx=sys.train_num, 
                    rank=sys.train_num, 
                    system=sys, 
                    init_time=sys.sys_time, 
                    init_segment=((None, None),(sys.signal_points[0],0)),
                    max_sp=T166.max_speed*1.6, 
                    max_acc=sys.acc_container[sys.train_num % len(sys.acc_container)], 
                    max_dcc=sys.dcc_container[sys.train_num % len(sys.dcc_container)],
                    length=1)

    sys.signal_points[10].open_route((1,0))
    for n in range(3600):
        T166.update_acc()
        T165.update_acc()
        sys.sys_time+=sys.refresh_time
    speed_curve(sys, T166)
    