from datetime import datetime, timedelta
from block import Block
import numpy as np
import random
from train import Train
from track import Track
from signal import Signal

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
        self.blocks[0].occupied_track(track_idx, new_train)

    def update_blk_right(self, i):
        for track in self.blocks[i].tracks:
            if self.dos_period[0] <= self.sys_time <= self.dos_period[1] and i == self.dos_pos:
                track.right_signal.update_signal('r')
            elif i + 1 < len(self.blocks) and not self.blocks[i + 1].has_available_track():
                track.right_signal.update_signal('r')
            elif i + 2 < len(self.blocks) and not self.blocks[i + 2].has_available_track():
                track.right_signal.update_signal('yy')
            elif i + 3 < len(self.blocks) and not self.blocks[i + 3].has_available_track():
                track.right_signal.update_signal('y')
            else:
                track.right_signal.update_signal('g')

        # 如果track数量超过1才考虑让车情况。（第一个blk暂不考虑为多track）
        if i > 0 and len(self.blocks[i].tracks) > 1:
            # 让车情况下的变灯。
            last_blk_has_train = False
            if not self.blocks[i - 1].has_available_track(): #后一个blk有车
                last_blk_has_train = True
            # if self.blocks[i].has_available_track():
            ava_track = -1
            prev_train_spd = 0
            if last_blk_has_train:
                ava_track = self.blocks[i].find_available_track()
                prev_train_spd = self.blocks[i - 1].tracks[0].train.max_speed
            
            # 找到速度最快火车的track
            max_train_track = ava_track
            for j, track in enumerate(self.blocks[i].tracks):
                if track.train != None and track.train.max_speed > prev_train_spd:
                    max_train_track = j

            for j, track in enumerate(self.blocks[i].tracks):
                if j != max_train_track:
                    track.right_signal.update_signal('r')

    def update_track_signal_color(self):
        for i in range(len(self.blocks)):
            self.update_blk_right(i)
            
    def refresh(self):
        self.update_track_signal_color()
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
