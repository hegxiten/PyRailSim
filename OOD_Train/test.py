from block import Block
from system import System
from train import Train
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import time
import random

def string_diagram(sys, start_time, end_time):
    '''To draw the string diagram based on the schedule dictionary for all the trains. 
    '''
    colors = ['red','green','blue','black','orange','cyan','magenta']
    color_num = len(colors)
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
    
    train_idx = list(range(len(x)))
    t_color = [colors[x.index(i)%color_num] for i in x]
    min_t, max_t = min([i[0] for i in x]), max([i[-1] for i in x])
    
    
    #plt.ion()
    plt.title('Result Analysis')
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

    for n in range(len(x)-1):
        #assert len(x[n]) == len(y[n]) == t_color[n]
        plt.plot([mdates.date2num(i) for i in x[n]], y[n], color=t_color[n])
    plt.gca().axhspan(15,20,color='yellow',alpha=0.5)
    plt.gca().axhspan(30,35,color='yellow',alpha=0.5)
    plt.gca().axvspan((datetime.fromtimestamp(start_time + 90 * 60)),(datetime.fromtimestamp(start_time + 150 * 60)),color='black',alpha=0.5)
    plt.show()
    #plt.ioff()
    

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
    # for i in range(5):
    sp_container = []
    acc_container = []
    for i in range(20):
        sp_container.append(random.randint(10,20) / 1000)
        acc_container.append(2.78e-05 * 0.3 * random.random() + 2.78e-05 * 0.85)
    headway = 300 * random.random() + 350
    sys = System(sim_init_time, [5] * 10, headway, sp_container, acc_container, [1,1,1,2,1,1,2,1,1,1], dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'], dos_pos=-1)
    sys_dos = System(sim_init_time, [5] * 10, headway, sp_container, acc_container, [1,1,1,2,1,1,2,1,1,1], dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'], dos_pos=4)
    sim_timedelta = sim_term_time - sim_init_time
    i = 0
    while (datetime.fromtimestamp(sys.sys_time) - sim_init_time).total_seconds() < sim_timedelta.total_seconds():
        i += 1
        sys.refresh()
        sys_dos.refresh()
    string_diagram(sys, sim_init_time, sim_term_time)
    string_diagram(sys_dos, sim_init_time, sim_term_time)

    delay = cal_delay(sys, sys_dos, 20)
    first_delay_train = first_delay_train_idx(delay)
    delay_avg = cal_delay_avg(delay)
    print("Test case 1, delay_avg = {}".format(delay_avg))

main()