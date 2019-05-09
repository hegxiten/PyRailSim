from datetime import datetime, timedelta
from block import Block
import numpy as np
from train import Train

class System():
    def __init__(self, init_time, blk_length_list, headway, sp_container, acc_container, tracks=[], dos_period=['2017-01-01 02:00:00', '2017-01-01 02:30:00'], dos_pos=-1, refresh_time=1):
        self.sys_time = init_time.timestamp()  
        # CPU format time in seconds, transferable between numerical value and M/D/Y-H/M/S string values 
        self.blocks = []
        for i in range(len(blk_length_list)):
            self.blocks.append(Block(i, blk_length_list[i], tracks[i]))
        self.trains = []
        self.dos_period = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp() for t in dos_period if type(t) == str]
        self.dos_pos = dos_pos
        self.train_num = 0
        self.block_intervals = []
        self.headway = headway
        self.sp_container = sp_container
        self.acc_container = acc_container

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

    def generate_train(self, track_idx):
        new_train = Train(self.train_num, self.train_num, self.block_intervals, self.sys_time, track_idx, self.sp_container[self.train_num % len(self.sp_container)], self.acc_container[self.train_num % len(self.acc_container)])
        self.trains.append(new_train)
        self.train_num += 1
        self.last_train_init_time = self.sys_time
        new_train.enter_block(self, 0, track_idx)

    def update_block_trgt_speed(self):
        # update the trgt_speed of every block.

        for i in range(len(self.blocks)):
            if self.dos_period[0] <= self.sys_time <= self.dos_period[1] and i == self.dos_pos:
                self.blocks[i].set_stop_speed()
            elif i + 1 < len(self.blocks) and not self.blocks[i + 1].has_available_track():
                self.blocks[i].set_stop_speed()
            elif i + 2 < len(self.blocks) and not self.blocks[i + 2].has_available_track():
                self.blocks[i].set_approaching_speed()
            elif i + 3 < len(self.blocks) and not self.blocks[i + 3].has_available_track():
                self.blocks[i].set_middle_approaching_speed()
            else:
                self.blocks[i].set_clear_speed()

    def refresh(self):
        self.update_block_trgt_speed()
        headway = self.headway#np.random.normal(exp_buffer, var_buffer)
        # If the time slot between now and the time of last train generation
        # is bigger than headway, it will generate a new train at start point.
        if self.train_num == 0:
            track_idx = self.blocks[0].find_available_track()
            self.generate_train(track_idx)
            
        if self.sys_time - self.last_train_init_time >= headway and self.blocks[0].has_available_track():
            track_idx = self.blocks[0].find_available_track()
            self.generate_train(track_idx)

        for t in self.trains:
            t.update_acc(self, self.dos_pos)
        self.trains.sort()
        for i, tr in enumerate(self.trains):
            tr.rank = i
        self.sys_time += self.refresh_time
