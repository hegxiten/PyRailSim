from block import Block
from system import System
from train import Train
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
  
def string_diagram(sys):
    '''
    To draw the string diagram based on the schedule dictionary for all the trains. 
    '''
    # draw the train working diagram
    '''begin comment__train stringline diagram'''
    x = []; y = []
    for i in range(len(sys.trains)-1):
        x.append([])
        y.append([])
        for j in range(len(sys.trains[i].time_pos_list)-1):
            
            x[i].append(sys.trains[i].time_pos_list[j][0])
            #x[i].append(datetime.fromtimestamp(sys.trains[i].time_pos_list[j][0]).strftime("%Y-%m-%d %H:%M:%S"))
            y[i].append(sys.trains[i].time_pos_list[j][1])


        y[i] = [n for (m,n) in sorted(zip(x[i],y[i]))] 
        # x[i] = sorted(x[i])


    plt.title('Result Analysis')
    for n in range(len(x)-1):
        if n % 5 == 0:
            plt.plot(x[n], y[n], color='green')
        if n % 5 == 1:
            plt.plot(x[n], y[n], color='blue')
        if n % 5 == 2:
            plt.plot(x[n], y[n], color='red')
        if n % 5 == 3:
            plt.plot(x[n], y[n], color='black')
        if n % 5 == 4:
            plt.plot(x[n], y[n], color='orange')

    plt.gcf().autofmt_xdate()
    plt.grid(True, linestyle = "-.", color = "r", linewidth = "0.1")
    plt.legend()
    plt.xlabel('Time/secs')
    plt.ylabel('Mile Post/miles')
    plt.show()
    '''end comment__train stringline diagram'''

def main():


    sys_init_time = datetime.strptime('2018-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
    sys_term_time = datetime.strptime('2018-01-01 03:00:00', "%Y-%m-%d %H:%M:%S")
    sys = System(sys_init_time, [5] * 10, [1,1,1,2,1,1,1,1,1,1], dos_period=['2018-01-01 00:30:00', '2018-01-01 01:30:00'], dos_pos=-1)

    i = 0
    while (datetime.fromtimestamp(sys.sys_time) - sys_init_time).total_seconds()  < (sys_term_time - sys_init_time).total_seconds():
        i += 1
        sys.refresh()

    for t in sys.trains:
        t.print_blk_time()
        
    string_diagram(sys)

main()