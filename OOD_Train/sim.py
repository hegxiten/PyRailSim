from block import Block
from system import System
from train import Train
import matplotlib.pyplot as plt
import time
import numpy as np

sys_init_time = '2018-01-01 00:00:00'
numerical_init_time = time.mktime(time.strptime('2018-01-01 00:00:00', "%Y-%m-%d %H:%M:%S"))
sys = System(sys_init_time, [5] * 10)
i = 0
while sys.sys_time - numerical_init_time  < 10000:
    i += 1
    # print(i)
    # print("Train number: {}".format(sys.train_num))
    sys.refresh()

for t in sys.trains:
    t.print_blk_time()

    
def string_diagram():
        '''
        To draw the string diagram based on the schedule dictionary for all the trains. 
        '''
        # draw the train working diagram
        '''begin comment__train stringline diagram'''
        x = []; y = []
        for t in range(len(sys.trains)-1):
            x.append([])
            y.append([])
        
        for i in range(len(sys.trains)-1):
            for j in range(len(sys.trains[i].blk_time)-1):
                x[i].append(sys.trains[i].blk_time[j][0])
                y[i].append(sys.blk_intervals[j][0])
                x[i].append(sys.trains[i].blk_time[j][1])
                y[i].append(sys.blk_intervals[j][1])
        for tn in self.all_schedule[tn]:  #t_stamp_std is all the time stamps
            x[tn-1].append((time.mktime(time.strptime(t_stamp_std, "%Y-%m-%d %H:%M:%S"))-self.strt_t_ticks)/3600)
            y[tn-1].append(self.all_schedule[tn][t_stamp_std]['coord_mp(miles)'])
            #print x[tn-1]
        
        y[tn-1] = [n for (m,n) in sorted(zip(x[tn-1],y[tn-1]))] 
        x[tn-1] = sorted(x[tn-1])
            
            
            #self.tn_by_rank  = {v : rk for rk, v in self.rank.items()}
        
        plt.title('Result Analysis')
        for n in range(len(x)-1):
            if n % 4 == 0:
                plt.plot(x[n], y[n], color='green')
            if n % 4 == 1:
                plt.plot(x[n], y[n], color='blue')
            if n % 4 == 2:
                plt.plot(x[n], y[n], color='red')
            if n % 4 == 3:
                plt.plot(x[n], y[n], color='black')

        plt.legend()
        plt.xlabel('time /hours')
        plt.ylabel('coord_mp /miles')
        plt.show()
        '''end comment__train stringline diagram'''

