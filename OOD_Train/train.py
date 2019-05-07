import random
import numpy as np
from datetime import datetime, timedelta

class Train():
    def __init__(self, idx, rank, blk_interval, init_time, curr_track):
        self.curr_pos = 0
        self.max_speed = random.randint(10,20) / 1000
        self.curr_speed = self.max_speed
        self.acc = 2.78e-05
        self.curr_acc = self.acc
        self.curr_blk = 0
        self.status = 1
        self.train_idx = idx
        self.rank = rank
        self.blk_time = [[init_time]]
        self.blk_interval = blk_interval
        self.time_pos_list = [[self.blk_time[0][0], self.blk_interval[0][0]]]  # not yet implemented interpolation
        self.curr_track = curr_track

    def __lt__(self, other):
        if self.curr_pos > other.curr_pos:
            return True
        elif self.curr_pos < other.curr_pos:
            return False
        elif self.max_speed < other.max_speed:
            return False
        elif self.max_speed > other.max_speed:
            return True
        elif self.rank < other.rank:
            return False
        else:
            return True

    def stop(self):
        self.curr_speed = 0
        self.status = 0
     
    def start(self):
        self.curr_speed = self.max_speed
        self.status = 1
    
    def terminate(self, system):
        self.status = 2
        
    def proceed(self, system, dest=None):
        self.start()
        if not dest:
            self.curr_pos += self.curr_speed * system.refresh_time
        else:
            self.curr_pos = dest
        self.time_pos_list.append([system.sys_time+system.refresh_time, self.curr_pos])
        
    def proceed_acc(self, system, delta_s, dest=None):
        # if delta_s < 0:
        #     delta_s = 0
        if self.curr_speed + self.curr_acc * system.refresh_time > self.max_speed:
            self.curr_speed = self.max_speed
            self.curr_acc = 0
        else:
            self.curr_speed += self.curr_acc * system.refresh_time

        if not dest:
            self.curr_pos += delta_s
        else:
            self.curr_pos = dest
        self.time_pos_list.append([system.sys_time+system.refresh_time, self.curr_pos])
    
    def stop_at_block_end(self, system, blk_idx):
        # assert self.curr_pos + self.curr_speed * system.refresh_time >= self.blk_interval[self.curr_blk][1]
        if self.curr_speed > 0:
            interpolate_time = (self.blk_interval[blk_idx][1]-self.curr_pos)/self.curr_speed + system.sys_time
            self.curr_pos = self.blk_interval[blk_idx][1]
            self.time_pos_list.append([interpolate_time, self.curr_pos])
        if self.curr_speed == 0:
            self.curr_pos = self.curr_pos
        self.time_pos_list.append([system.sys_time+system.refresh_time, self.curr_pos])
        self.stop()
        
    def leave_block(self, system, blk_idx):
        system.blocks[blk_idx].free_track(self.curr_track)
        self.blk_time[blk_idx].append(system.sys_time)
        # interpolate the time moment when the train leaves the system
        if blk_idx == len(system.blocks)-1:
            interpolate_time = (self.blk_interval[blk_idx][1] - self.curr_pos) / self.curr_speed + system.sys_time
            self.curr_pos = self.blk_interval[blk_idx][1]
            self.time_pos_list.append([system.sys_time, self.curr_pos])
        
    def enter_block(self, system, blk_idx, next_block_ava_track):
        system.blocks[blk_idx].occupied_track(next_block_ava_track, self)
        self.curr_track = next_block_ava_track
        self.blk_time.append([system.sys_time])
    
    def update(self, system, dos_pos=-1):
        # update self.curr_pos
        # update self.curr_speed
        # if the train already at the end of the railway, do nothing. (no updates on (time,pos))
        if self.curr_pos == self.blk_interval[-1][1]:
            pass
        # If the train arrives at the end of all the blocks, the train will leave the system.
        elif self.is_leaving_system(self.curr_speed * system.refresh_time):
            self.leave_block(system, len(self.blk_interval) - 1)
            self.curr_blk = None
            self.proceed(system, dest=self.blk_interval[-1][1])
        # The train will still stay in current block in next refresh time, so continue the system.
        elif self.is_normal_proceed(self.curr_speed * system.refresh_time):
            self.curr_blk = self.curr_blk
            self.proceed(system)
        # If the next block has no available tracks 
        # the train will stop at end of current block.
        elif (not system.blocks[self.curr_blk+1].has_available_track()): 
            self.stop_at_block_end(system, self.curr_blk)
        # If or there is a dos at the end of current block
        # the train will stop at end of current block.
        elif self.is_during_dos(system, dos_pos):
            self.stop_at_block_end(system, self.curr_blk)
        #If next train is faster than this train, the postion of previous train is behind the start
        # of this block, let this train stop at the end of block.
        elif self.is_leaving_block(self.max_speed * system.refresh_time)\
            and self.rank < system.train_num - 1\
            and self.max_speed < system.trains[self.rank + 1].max_speed\
            and system.trains[self.rank + 1].curr_pos >=\
                system.block_intervals[system.trains[self.rank].curr_blk - 1][0]\
            and system.blocks[self.curr_blk].has_available_track():
                self.stop_at_block_end(system, self.curr_blk)
        # If the train will enter the next block in next refresh time,
        # update the system info and the train info.
        elif self.is_leaving_block(self.curr_speed * system.refresh_time): 
            self.leave_block(system, self.curr_blk)
            next_block_ava_track = system.blocks[self.curr_blk + 1].find_available_track()
            self.enter_block(system, self.curr_blk+1, next_block_ava_track)
            self.curr_blk += 1
            self.proceed(system)
   
    def select_move_model(self, system):
        # print("current block index: {}".format(self.curr_blk))
        if self.curr_blk == None:
            return 0
        curr_block = system.blocks[self.curr_blk]
        if self.curr_speed + self.curr_acc * system.refresh_time > self.max_speed:
            self.curr_acc = 0
            return self.max_speed * system.refresh_time
        break_distance = (self.curr_speed ** 2 - system.blocks[self.curr_blk].trgt_speed ** 2) / (2 * self.acc)
        
        # assert break_distance <= self.blk_interval[self.curr_blk][1] - self.curr_pos
        
        if self.curr_speed < curr_block.trgt_speed:
            self.curr_acc = self.acc
        elif self.curr_speed > curr_block.trgt_speed:
            if break_distance >= self.blk_interval[self.curr_blk][1] - self.curr_pos:
                self.curr_acc = - self.acc
            elif break_distance < self.blk_interval[self.curr_blk][1] - self.curr_pos:
                self.curr_acc = self.acc
        else:
            self.curr_acc = 0
        
        delta_s = self.curr_speed * system.refresh_time + 0.5 * self.curr_acc * system.refresh_time ** 2
        # print(delta_s)
        return delta_s

    def select_move_model_simple(self, system):
        # print("current block index: {}".format(self.curr_blk))
        if self.curr_blk == None:
            return 0
        curr_block = system.blocks[self.curr_blk]
        if self.curr_speed < 0 and self.curr_acc < 0:
            self.curr_speed = 0
        if self.curr_speed < curr_block.trgt_speed and self.curr_speed < self.max_speed:
            self.curr_acc = self.acc
        elif self.curr_speed > curr_block.trgt_speed and self.curr_speed > 0:
            self.curr_acc = -self.acc
        else:
            self.curr_acc = 0
        
        delta_s = self.curr_speed * system.refresh_time + 0.5 * self.curr_acc * system.refresh_time ** 2
        # print(delta_s)
        return delta_s

    def update_acc(self, system, dos_pos=-1):
        delta_s = self.select_move_model_simple(system)
        # update self.curr_pos
        # update self.curr_speed
        # if the train already at the end of the railway, do nothing. (no updates on (time,pos))
        if self.is_out_of_sys():
            pass
        # If the train arrives at the end of all the blocks, the train will leave the system.
        elif self.is_leaving_system(delta_s):
            self.leave_block(system, len(self.blk_interval) - 1)
            self.curr_blk = None
            self.proceed_acc(system, delta_s, dest=self.blk_interval[-1][1])
        # If or there is a dos at the end of current block
        # the train will stop at end of current block.
        elif self.is_during_dos(system, dos_pos):
            self.proceed_acc(system,delta_s)
        elif self.let_faster_train(system):
            if self.curr_speed > 0:
                self.curr_acc = -self.acc
            delta_s = self.curr_speed * system.refresh_time + 0.5 * self.curr_acc * system.refresh_time ** 2
            self.proceed_acc(system,delta_s)
        # The train will still stay in current block in next refresh time, so continue the system.
        elif self.is_normal_proceed(delta_s):
            self.proceed_acc(system, delta_s)
        # If the next block has no available tracks 
        # the train will stop at end of current block.
        elif self.is_stopped_by_previous_train(system, delta_s): 
            self.stop_at_block_end(system, self.curr_blk)
        # If the train will enter the next block in next refresh time,
        # update the system info and the train info.
        elif self.is_leaving_block(delta_s): 
            self.leave_block(system, self.curr_blk)
            next_block_ava_track = system.blocks[self.curr_blk + 1].find_available_track()
            self.enter_block(system, self.curr_blk+1, next_block_ava_track)
            self.curr_blk += 1
            self.proceed_acc(system, delta_s)
    
    def is_out_of_sys(self):
        '''
        Determined the train should stop or not because of the next block has a train.
        @return True or False
        '''
        return self.curr_pos == self.blk_interval[-1][1] and self.curr_blk == None
    
    def is_leaving_block(self, delta_s):
        return self.curr_pos + delta_s >= self.blk_interval[self.curr_blk][1]

    def is_stopped_by_previous_train(self, system, delta_s):
        '''
        Determined the train should stop or not because of the next block has a train.
        @return: True or False
        '''
        return self.is_leaving_block(delta_s) and (not system.blocks[self.curr_blk+1].has_available_track())

    def is_normal_proceed(self, delta_s):
        '''
        Whether the train is still in current block in next refresh time.
        @return: True or False
        '''
        return self.curr_pos + delta_s < self.blk_interval[self.curr_blk][1]

    def is_leaving_system(self, delta_s):
        '''
        Whether the train is leaving the last block of system
        @return: True or False
        '''
        return self.curr_pos + delta_s >= self.blk_interval[-1][1]

    def is_during_dos(self, system, dos_pos):
        '''
        Whether the train is during the dos pos and time period
        @return: True or False
        '''
        return dos_pos == self.curr_blk and system.dos_period[0] <= system.sys_time <= system.dos_period[1]

    def let_faster_train(self, system):
        '''
        If the next train is faster than self train,
        self train should let faster train go though.
        @return: True or False
        '''
        return self.rank < system.train_num - 1 and self.max_speed < system.trains[self.rank + 1].max_speed\
            and system.blocks[self.curr_blk].track_number > 1\
            and ((system.trains[self.rank + 1].curr_blk == self.curr_blk - 1\
                and system.blocks[self.curr_blk].has_available_track())\
            or system.trains[self.rank + 1].curr_blk == self.curr_blk)

    def print_blk_time(self):
        print(self.blk_time)