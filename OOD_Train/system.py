from datetime import datetime, timedelta
from block import Block
import numpy as np
from train import Train
from track import Track
from signal import Signal

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
