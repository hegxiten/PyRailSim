from datetime import datetime, timedelta
from block import Block
import numpy as np
import random
from train import Train

class System():
    def __init__(self, init_time, *args, **kwargs):
        """
        Parameters
        ----------
        :_blk_length_list: list (**kw)
            A list of block lengths for each block.
        :tracks: list (**kw)
            A list of total number of tracks per block.
        :dos_period: list or tuple (**kw)
            2-element list or tuple showing the starting and finishing time of DoS attacks.
        :headway: (**kw)
            Traffic headway in seconds for unidirectional trains. 500 by default.
        :dos_pos: int (**kw)
            Index of block to be attacked by DoS. -1 by default (no DoS).
        :refresh_time: int (**kw)
            Seconds between two consecutive traverse calculations of the simulation.
        :sp_containter: list (**kw)
            A list of randomized speed values for trains to initialize by. Uniform range.
        :add_container: list (**kw)
            A list of randomized acceleration values for trains to initialize by. Uniform range.
        """
        _blk_length_list = [5] * 10     if not kwargs.get('blk_length_list') else kwargs.get('blk_length_list')
        _blk_number = len(_blk_length_list)
        
        self.sys_time = init_time.timestamp()   # CPU format time in seconds, transferable between numerical value and M/D/Y-H/M/S string values 
        self.trains, self.train_num = [], 0
        self.blocks = [Block(i, _blk_length_list[i], kwargs.get('tracks')[i]) for i in range(_blk_number)]
        self.dos_period = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp() for t in kwargs.get('dos_period') if type(t) == str]
        self.headway = 500  if not kwargs.get('headway') else kwargs.get('headway')
        self.dos_pos = -1   if not kwargs.get('dos_pos') else kwargs.get('dos_pos')
        self.last_train_init_time = self.sys_time
        self.sp_container = args[0]     if args else [random.uniform(0.01, 0.02) for i in range(20)]
        self.acc_container = args[1]    if args else [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
        self.refresh_time = 1           if not kwargs.get('refresh_time') else kwargs.get('refresh_time')
        self.block_intervals = []
        # interval is the two-element array containing mile posts of boundaries 
        for i in range(_blk_number):
            if i == 0:
                self.block_intervals.append([0, _blk_length_list[0]])
            else:
                left = self.block_intervals[i - 1][1]
                right = left + _blk_length_list[i]
                self.block_intervals.append([left, right]) 
        
    def generate_train(self, track_idx):
        new_train = Train(self.train_num, 
                          self.train_num, 
                          self.block_intervals, 
                          self.sys_time, 
                          track_idx, 
                          self.sp_container[self.train_num % len(self.sp_container)], 
                          self.acc_container[self.train_num % len(self.acc_container)])
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

    def print_blk_status(self):
        print("#===================================")
        for blk in self.blocks:
            print(blk.has_available_track())

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
        
if __name__ =='__main__':
    sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
    sim_term_time = datetime.strptime('2018-01-10 15:30:00', "%Y-%m-%d %H:%M:%S")
    sp_container = [random.uniform(0.01, 0.02) for i in range(20)]
    acc_container = [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
    headway = 200 * random.random() + 400
    sys = System(sim_init_time, sp_container, acc_container,
                 dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],  
                 headway=headway, 
                 tracks=[1,1,1,2,1,1,2,1,1,1], 
                 dos_pos=-1)
