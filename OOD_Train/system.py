import time

from block import Block
import numpy as np
from train import Train


exp_buffer, var_buffer = 10, 0.5

class System():
    def __init__(self, init_time, blk_length_list, siding_dict={}, dos_period=['2017-12-31 00:00:00', '2017-12-31 00:00:00'], dos_pos=-1, refresh_time=1):
        self.sys_time = time.mktime(time.strptime(init_time, "%Y-%m-%d %H:%M:%S"))  
        # CPU format time in seconds, transferable between numerical value and M/D/Y-H/M/S string values 
        self.blocks = []
        for i in range(len(blk_length_list)):
            if i in siding_dict.keys():
                self.blocks.append(Block(i, blk_length_list[i], siding_dict[i]))
            self.blocks.append(Block(i, blk_length_list[i]))
        self.trains = []
        self.dos_period = [time.mktime(time.strptime(t, "%Y-%m-%d %H:%M:%S")) for t in dos_period if type(t) == str]
        self.dos_pos = dos_pos
        self.train_num = 0        
        self.block_intervals = []
        # interval is the two-element array containing mile posts of boundaries 
        for i in range(len(blk_length_list)):
            if i == 0:
                self.block_intervals.append([0, blk_length_list[0]])
            else:
                left = self.block_intervals[i - 1][1]
                right = left + blk_length_list[i]
                self.block_intervals.append([left, right]) 
        self.last_train_init_time = self.sys_time
        self.refresh_time = refresh_time


    def generate_train(self):
        new_train = Train(self.train_num, self.train_num, self.block_intervals, self.sys_time)
        self.trains.append(new_train)
        self.train_num += 1
        self.last_train_init_time = self.sys_time

    def refresh(self):
        headway = 600#np.random.normal(exp_buffer, var_buffer)
        # If the time slot between now and the time of last train generation
        # is bigger than headway, it will generate a new train at start point.
        if self.train_num == 0:
            self.generate_train()
            
        if self.sys_time - self.last_train_init_time >= headway and not self.blocks[0].isOccupied:
            self.generate_train()

        for t in self.trains:
            t.update(self, self.dos_pos)
        self.sys_time += self.refresh_time

        