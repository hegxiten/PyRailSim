import time
import random
import numpy as np

class Train():
    def __init__(self, idx, rank, blk_interval, init_time, curr_track):
        self.curr_pos = 0
        self.init_speed = random.randint(2,10) / 100
        self.curr_speed = self.init_speed
        self.curr_blk = 0
        self.status = 1
        self.train_idx = idx
        self.rank = rank
        self.blk_time = [[init_time]]
        self.blk_interval = blk_interval
        self.time_pos_list = [[self.blk_time[0][0], self.blk_interval[0][0]]]  # not yet implemented interpolation
        self.curr_track = curr_track
        
    def stop(self):
        self.curr_speed = 0
        self.status = 0
     
    def start(self):
        self.curr_speed = self.init_speed
        self.status = 1
    
    def terminate(self, system):
        self.status = 2
        
    def proceed(self, system):
        self.start()
        self.curr_pos += self.curr_speed * system.refresh_time
        self.time_pos_list.append([system.sys_time, self.curr_pos])
    
    def stop_at_block_end(self, system, blk_idx):
        # interpolate the time moment when the train reaches exactly the block boundary
        if self.curr_speed > 0:
            interpolate_time = (self.blk_interval[blk_idx][1] - self.curr_pos) / self.curr_speed + system.sys_time
            self.curr_pos = self.blk_interval[blk_idx][1]
            self.time_pos_list.append([system.sys_time, self.curr_pos])
        if self.curr_speed == 0:
            self.curr_pos = self.curr_pos
        self.time_pos_list.append([system.sys_time, self.curr_pos])
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
        # If the train arrives at the end of whole track, the train will leave blocks.
        if self.curr_pos + self.curr_speed * system.refresh_time >= self.blk_interval[len(self.blk_interval) - 1][1]:    
            if not self.curr_pos == self.blk_interval[len(self.blk_interval) - 1][1]:
                self.leave_block(system, len(self.blk_interval) - 1)
            
        # The train will still stay in current block in next refresh time, so continue the system.
        elif self.curr_pos + self.curr_speed * system.refresh_time < self.blk_interval[self.curr_blk][1]:
            self.proceed(system)
        # If the next block has a train or there is a dos at the end of current block,
        # the train will stop at end of current block.
        elif (not system.blocks[self.curr_blk+1].has_available_track() or dos_pos == self.blk_interval[self.curr_blk][1]):
            self.stop_at_block_end(system, self.curr_blk)
        # If the train will enter the next block in next refresh time,
        # udpate the system info and the train info.
        elif self.curr_pos + self.curr_speed * system.refresh_time >= self.blk_interval[self.curr_blk][1]: 
            self.leave_block(system, self.curr_blk)
            next_block_ava_track = system.blocks[self.curr_blk + 1].find_available_track()
            self.enter_block(system, self.curr_blk+1, next_block_ava_track)
            self.curr_blk += 1
            self.proceed(system)

    def print_blk_time(self):
        print(self.blk_time)