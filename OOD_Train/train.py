import time
import random
import numpy as np


refresh = 1

class Train():
    def __init__(self, rank, blk_interval, sys_time):
        self.pos = 0
        self.init_speed = random.randint(2,10) / 100
        self.curr_speed = self.init_speed
        self.curr_blk = 0
        self.status = 1
        self.rank = rank

        #self.blk_time = [[time.ctime(sys_time)]]
        self.blk_time = [[sys_time]]

        self.blk_interval = blk_interval
    '''
    def approach_block(self, blk_idx):
        # Approach is a status that the tn_th train is approaching the blk_idx_th block.
        # After the refresh time the train still does not enter the block.
        if self.curr_spd[tn] > 0:
            if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh < self.blk_interval[blk_idx][0]:
                #print 'approaching, MP: '+' train '+str(tn) +' '+ str(round(self.curr_mp[tn] + self.curr_spd[tn] * self.refresh))+' DoS has been: '+str(self.curr_duration[tn]-self.DoS_strt_t_ticks)  
                return True 
        if self.curr_spd[tn] < 0:
            if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh > self.blk_interval[blk_idx][1]:
                return True
    
    def leaving_block(self, blk_idx):
        # Leaving is a status that the tn_th train is leaving the blk_idx_th block.
        # Before and after the refresh time, the train had left the block.
        if self.curr_spd[tn] > 0 and self.curr_mp[tn] > self.blk_interval[blk_idx][1]: 
            #print 'leaving, MP: '+' train '+str(tn) +' '+ str(round(self.curr_mp[tn] + self.curr_spd[tn] * self.refresh))+' DoS has been: '+str(self.curr_duration[tn]-self.DoS_strt_t_ticks)  
            return True 
        if self.curr_spd[tn] < 0 and self.curr_mp[tn] < self.blk_interval[blk_idx][0]:
            return True
    
    def in_block(self, blk_idx):
        # In_block is a status that the tn_th train is in the blk_idx_th block.
        # Before and after the refresh time, the train is in the block.
        if self.curr_spd[tn] != 0: 
            if self.blk_interval[blk_idx][0] < self.curr_mp[tn] <= self.blk_interval[blk_idx][1]: 
                if self.blk_interval[blk_idx][0] < self.curr_mp[tn] + self.curr_spd[tn] * self.refresh <= self.blk_interval[blk_idx][1]:
                    #print 'within, MP: '+' train '+str(tn) +' '+ str(round(self.curr_mp[tn] + self.curr_spd[tn] * self.refresh))+' DoS has been: '+str(self.curr_duration[tn]-self.DoS_strt_t_ticks)  
                    return True    
    def enter_block(self, blk_idx):
        # Enter is a status that the tn_th train is entering the blk_idx_th block.
        # Before the refresh time, the train was not in the block.
        # After the refresh time, the train was in the block.
        if self.blk_interval[blk_idx][0] < self.pos <= self.blk_interval[blk_idx][1]:
            new_pos = self.pos + self.curr_speed * refresh 
            if self.blk_interval[blk_idx + 1][0] < new_pos <= self.blk_interval[blk_idx + 1][1]:
                return True 
    
    def skip_block(self, blk_idx):
        # Skip is a status that the tn_th train is skiping the blk_idx_th block.
        # Before the refresh time, the train was appoarching the block.
        # After the refresh time, the train was leaving the block.
        if not self.blk_interval[blk_idx][0] < self.curr_mp[tn] < self.blk_interval[blk_idx][1]:
            if self.curr_spd[tn] > 0:
                if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh > self.blk_interval[blk_idx][1]:
                    if self.curr_mp[tn] < self.blk_interval[blk_idx][0]:
                        print ('Warning: refresh too short, DoS got skipped')
                        return True 
            if self.curr_spd[tn] < 0:
                if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh < self.blk_interval[blk_idx][0]:
                    if self.curr_mp[tn] > self.blk_interval[blk_idx][1]: 
                        print ('Warning: refresh too short, DoS got skipped')
                        return True
    
    def exit_block(self, blk_idx):
        # Exit is a status that the tn_th train is exiting the blk_idx_th block.
        # Before the refresh time, the train was in the block.
        # After the refresh time, the train was not in the block.
        if self.blk_interval[blk_idx][0] < self.curr_mp[tn] <= self.blk_interval[blk_idx][1]: 
            if not self.blk_interval[blk_idx][0] < self.curr_mp[tn] + self.curr_spd[tn] * self.refresh < self.blk_interval[blk_idx][1]:
                return True 
    '''
    def stop(self):
        self.speed = 0
        self.status = 0
    
    def restart(self):
        self.curr_speed = self.init_speed
        self.status = 1
    
    def update(self, system, next_block_has_train, curr_time, dos_pos=-1):
        if self.pos >= self.blk_interval[len(self.blk_interval) - 1][1]:
            return
        if self.pos + self.curr_speed * refresh < self.blk_interval[self.curr_blk][1]:
            self.pos = self.pos + self.curr_speed * refresh
        elif next_block_has_train:
            self.pos = self.blk_interval[self.curr_blk][1]
        elif dos_pos == self.blk_interval[self.curr_blk][1]:
            self.pos = self.blk_interval[self.curr_blk][1]
        else:
            self.blk_time[self.curr_blk].append(curr_time)
            if len(self.blk_time) < len(system.blocks):
                self.blk_time.append([curr_time])
            system.blocks[self.curr_blk].isOccupied = False
            if self.curr_blk < len(system.blocks)-1:
                self.curr_blk += 1
                system.blocks[self.curr_blk].isOccupied = True
            else:
                self.blk_time.pop(-1)
            self.pos = self.pos + self.curr_speed * refresh

    def print_blk_time(self):
        print(self.blk_time)