from block import Block
from system import System
from train import Train
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
  
def string_diagram(sys):
    '''To draw the string diagram based on the schedule dictionary for all the trains. 
    '''
    color_num, colors = 5, ['red','green','blue','black','orange','cyan','magenta']
    x = []; y = []; 
    for i in range(len(sys.trains)-1):
        x.append([])
        y.append([])
        for j in range(len(sys.trains[i].time_pos_list)-1):
            x[i].append(datetime.fromtimestamp(sys.trains[i].time_pos_list[j][0]))
            y[i].append(sys.trains[i].time_pos_list[j][1])

    y = [i for _,i in sorted(zip([i[0] for i in x], y))]
    x = sorted(x, key = lambda x: x[0])
    assert len(x) == len(y)
    
    train_idx = list(range(len(x)))
    t_color = [colors[x.index(i)%color_num] for i in x]
    min_t, max_t = min([i[0] for i in x]), max([i[-1] for i in x])
    timestamp_list = []
    for i in x:
        timestamp_list+=i
    timestamp_list = sorted(list(set(timestamp_list)))
    trains = {}
    
    plt.ion()
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
    
    for t in timestamp_list:
        plt
        for n in range(len(x)-1):
            assert len(x[n]) == len(y[n])
            if t in x[n]:
                idx_to_trunc = x[n].index(t)
                plt.plot([mdates.date2num(i) for i in x[n][:idx_to_trunc]], y[n][:idx_to_trunc], color=t_color[n])
                
    
    
    plt.ioff()
    plt.show()
    '''end comment__train stringline diagram'''

def main():
    sim_init_time = datetime.strptime('2018-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
    sim_term_time = datetime.strptime('2018-01-01 03:00:00', "%Y-%m-%d %H:%M:%S")
    sys = System(sim_init_time, [5] * 10, [1,1,1,2,1,1,1,1,1,1], dos_period=['2018-01-01 00:30:00', '2018-01-01 01:30:00'], dos_pos=-1)
    sim_timedelta = sim_term_time - sim_init_time
    i = 0
    while (datetime.fromtimestamp(sys.sys_time) - sim_init_time).total_seconds() < sim_timedelta.total_seconds():
        i += 1
        sys.refresh()
    string_diagram(sys)

main()