import time
import random
import numpy as np

class Train():
    def __init__(self, idx, rank, blk_interval, init_time, refresh_time):
        self.curr_pos = 0
        self.curr_time = init_time
        self.init_speed = random.randint(2,10) / 100
        self.curr_speed = self.init_speed
        self.curr_blk = 0
        self.status = 1
        self.train_idx = idx
        self.rank = rank
        #self.blk_time = [[time.ctime(init_time)]]
        self.blk_time = [[self.curr_time]]
        self.blk_interval = blk_interval
        self.refresh_time = refresh_time
        self.time_pos_list = [[self.blk_time[0][0], self.blk_interval[0][0]]]  # not yet implemented interpolation
        
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
        if self.blk_interval[blk_idx][0] < self.curr_pos <= self.blk_interval[blk_idx][1]:
            new_pos = self.curr_pos + self.curr_speed * refresh 
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
        self.curr_speed = 0
        self.status = 0
    
    def start(self):
        self.curr_speed = self.init_speed
        self.status = 1
    
    def terminate(self):
        self.status = 2
        
    def proceed(self, system):
        self.start()
        self.curr_pos += self.curr_speed * self.refresh_time
        self.curr_time += self.refresh_time
        self.time_pos_list.append([self.curr_time, self.curr_pos])
    
    def stop_at_block_end(self, system, blk_idx):
        # interpolate the time moment when the train reaches exactly the block boundary
        if self.curr_speed > 0:
            interpolate_time = (self.blk_interval[blk_idx][1] - self.curr_pos) / self.curr_speed + self.curr_time
            self.curr_pos = self.blk_interval[blk_idx][1]
            self.curr_time = interpolate_time
            self.time_pos_list.append([self.curr_time, self.curr_pos])
        self.curr_pos = self.curr_pos
        self.curr_time += self.refresh_time
        self.time_pos_list.append([self.curr_time, self.curr_pos])
        self.stop()
        
    def leave_block(self, system, blk_idx):
        system.blocks[blk_idx].isOccupied = False
        self.blk_time[blk_idx].append(self.curr_time)
        
    def enter_block(self, system, blk_idx):
        system.blocks[blk_idx].isOccupied = True
        self.blk_time.append([self.curr_time])
    
    def update(self, system, next_block_has_train, curr_time, dos_pos=-1):
        if self.curr_pos + self.curr_speed * self.refresh_time >= self.blk_interval[len(self.blk_interval) - 1][1]:    
            self.leave_block(system, len(self.blk_interval) - 1)
        elif self.curr_pos + self.curr_speed * self.refresh_time < self.blk_interval[self.curr_blk][1]:
            self.proceed(system)
        elif (next_block_has_train or dos_pos == self.blk_interval[self.curr_blk][1]):
            self.stop_at_block_end(system, self.curr_blk)
        elif self.curr_pos + self.curr_speed * self.refresh_time >= self.blk_interval[self.curr_blk][1]: 
            if self.curr_blk < len(system.blocks)-1:
                self.leave_block(system, self.curr_blk)            
                self.enter_block(system, self.curr_blk+1)
                self.curr_blk += 1
                self.proceed(system)
            elif self.curr_pos + self.curr_speed * self.refresh_time < self.blk_interval[self.curr_blk][1]: 
                self.proceed(system)
            else: 
                self.leave_block(system, self.curr_blk)

    def print_blk_time(self):
        print(self.blk_time)