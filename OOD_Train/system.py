import time

from block import Block
import numpy as np
from train import Train


exp_buffer, var_buffer = 10, 0.5

class System():
    def __init__(self, init_time, block_length, siding_index=[], dos_period=['2017-12-31 00:00:00', '2017-12-31 00:00:00'], dos_pos=-1, refresh_time=1):
        self.sys_time = time.mktime(time.strptime(init_time, "%Y-%m-%d %H:%M:%S"))  
        # CPU format time in seconds, transferable between numerical value and M/D/Y-H/M/S string values 
        self.blocks = []
        self.start_time = time.time()
        for i in range(len(block_length)):
            if i in siding_index:
                self.blocks.append(Block(i, block_length[i], True))
            self.blocks.append(Block(i, block_length[i], False))
        self.trains = []
        self.dos_period = [time.mktime(time.strptime(t, "%Y-%m-%d %H:%M:%S")) for t in dos_period if type(t) == str]
        self.dos_pos = dos_pos
        self.train_num = 0        
        self.block_intervals = []
        # interval is the two-element array containing mile posts of boundaries 
        for i in range(len(block_length)):
            if i == 0:
                self.block_intervals.append([0, block_length[0]])
            else:
                left = self.block_intervals[i - 1][1]
                right = left + block_length[i]
                self.block_intervals.append([left, right]) 
        self.last_train_time = self.sys_time
        self.refresh_time = refresh_time


    def generate_train(self):
        new_train = Train(self.train_num, self.block_intervals, self.sys_time)
        self.trains.append(new_train)
        self.train_num += 1
        self.last_train_time = self.sys_time

    def refresh(self):
        headway = 600#np.random.normal(exp_buffer, var_buffer)
        # If the time slot between now and the time of last train generation
        # is bigger than headway, it will generate a new train at start point.
        if self.train_num == 0:
            self.generate_train()


        if self.sys_time - self.last_train_time >= headway and not self.blocks[0].isOccupied:
            self.generate_train()

        for t in self.trains:
            if t.curr_blk >= len(self.blocks):
                continue
            if t.curr_blk < len(self.blocks) - 1:
                next_block_has_train = self.blocks[t.curr_blk + 1].isOccupied
            else:
                next_block_has_train = False

            #curr_time = time.ctime(int(self.sys_time))
            curr_time = self.sys_time

            if self.dos_period[0] <= self.sys_time <= self.dos_period[1]:
                t.update(self, next_block_has_train, curr_time, self.dos_pos)
            else:
                t.update(self, next_block_has_train, curr_time)
        self.sys_time += self.refresh_time

        