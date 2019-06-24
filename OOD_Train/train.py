import random
import numpy as np
from datetime import datetime, timedelta
from infrastructure import Track, Block, BigBlock
from signaling import AutoSignal, HomeSignal, AutoPoint, ControlPoint

class Train():

    @staticmethod
    def abs_brake_distance(curr_spd, tgt_spd, brake_dcc):
        # speed in miles/sec, dcc in miles/(second)^2
        # return absolute miles
        if brake_dcc == 0:
            return 0
        else:
            return abs((tgt_spd) ** 2 - (curr_spd) ** 2)/(2*abs(brake_dcc)) \
                if abs(tgt_spd) < abs(curr_spd)\
                    else 0
        

    def __init__(self, idx, rank, system, init_time, init_segment, max_sp, max_acc, max_dcc, **kwargs):        
        ((_curr_prev_sigpoint,_prev_sigport),(_curr_sigpoint, _prev_sigport)) = init_segment
        self._curr_routing_path_segment = init_segment
        self._curr_MP = self.curr_sig.MP
        self.train_idx = idx
        self.rank = rank
        self.system = system
        self.system.trains.append(self)
        self.max_speed = max_sp
        self.max_acc = max_acc
        self.max_dcc = max_dcc
        self.length = 0                 if not kwargs.get('length') else kwargs.get('refresh_time')
        self._curr_speed = 0
        self._stopped = True
        self.time_pos_list = []
        if self.curr_track_head:
            if self not in self.curr_track_head.train:
                self.curr_track_head.train.append(self)

    def __repr__(self):
        return 'train index {}, current segment/direction {}'\
            .format(self.train_idx, self.curr_routing_path_segment)

    @property
    def terminated(self):
        return True if not self.curr_routing_path_segment[1][0] and\
            self.curr_rear_MP  else False

    @property
    def stopped(self):
        if self.terminated:
            self._stopped = True
        elif self.curr_speed == 0 and not self.curr_sig.permit_track:
            self._stopped = True
        else:
            self._stopped = False
        return self._stopped

    @property
    def curr_routing_path_segment(self):
        return self._curr_routing_path_segment

    @property
    def curr_track_head(self):
        return self.system.get_track_by_point_port_pairs\
            (self.curr_prev_sigpoint, self.curr_prev_sigport, self.curr_sigpoint, self.curr_sigport)

    @property
    def curr_tracks(self):
        # a list of track instances being occupied by self (in order from head to tail)
        pass
        return 

    @property
    def curr_occupied_routing(self):
        # a list of routing path tuples being occupied by self (in order from head to tail)
        pass 
        return

    @property
    def curr_bigblock_routing(self):
        return self.curr_track_head.bigblock.routing

    @property
    def curr_routing_path(self):
        return self.curr_track_head.curr_routing_path if self.curr_track_head else None

    @curr_routing_path_segment.setter
    def curr_routing_path_segment(self,new_segment):
        assert isinstance(new_segment, tuple) and len(new_segment) == 2
        self._curr_routing_path_segment = new_segment
    
    @property
    def curr_sigpoint(self):
        return self.curr_routing_path_segment[1][0]
    @property
    def curr_prev_sigpoint(self):
        return self.curr_routing_path_segment[0][0]    
    @property
    def curr_sigport(self):
        return self.curr_routing_path_segment[1][1]
    @property
    def curr_prev_sigport(self):
        return self.curr_routing_path_segment[0][1]
    
    @property
    def curr_sig(self):
        return self.curr_sigpoint.signal_by_port[self.curr_sigport] if not self.terminated else None

    @property
    def curr_rear_MP(self):
        if not self.length:
            return self.curr_MP
        else:
            if self.curr_track_head:
                if self.curr_sig.MP == max(self.curr_track_head):
                    return self.curr_MP - self.length
                else:
                    return self.curr_MP + self.length
            elif not self.curr_track_head:
                if not self.curr_prev_sigpoint:
                    if self.curr_sigpoint.MP == :
                        return self.curr_MP - self.length
                    else:
                        return self.curr_MP + self.length
                if not self.curr_sigpoint:  # terminating, passing the last signal point
                    if self.prev_sigpoint.MP == :

    @property
    def curr_MP(self):
        if self.curr_track_head:
            assert  min(self.curr_track_head.MP) <= self._curr_MP <= max(self.curr_track_head.MP)
        return self._curr_MP

    @curr_MP.setter
    def curr_MP(self, new_MP):
        if self.terminated:
            assert self.curr_prev_sigpoint
            self._curr_MP = self.curr_prev_sigpoint.signal_by_port[self.curr_prev_sigport].MP
        else:
            assert self.curr_sigpoint
            # calling the MP should consider switching lines with MP gaps
            if self.curr_sigpoint:
                if self.curr_track_head:     
                    # not initiating
                    if min(self.curr_track_head.MP) < new_MP < max(self.curr_track_head.MP):  
                        # within a track
                        self._curr_MP = new_MP
                    else:   
                        # entering a new track; crossing current signal point
                        # new track may have a separate MP system
                        _new_prev_sig_MP = self.curr_sigpoint.signal_by_port[self.curr_sig.route[1]].MP
                        _curr_sig_MP = self.curr_sigpoint.signal_by_port[self.curr_sig.route[0]].MP
                        self.cross_sigpoint(self.curr_sigpoint, self._curr_MP, new_MP)
                        self._curr_MP = _new_prev_sig_MP + (new_MP - _curr_sig_MP)
                else:
                    # initiating, cross the entry control point
                    _new_prev_sig_MP = self.curr_sigpoint.signal_by_port[self.curr_sig.route[1]].MP
                    _curr_sig_MP = self.curr_sigpoint.signal_by_port[self.curr_sig.route[0]].MP
                    self.cross_sigpoint(self.curr_sigpoint, self._curr_MP, new_MP)
                    self._curr_MP = new_MP - _curr_sig_MP + _new_prev_sig_MP
            else: 
                raise ValueError('Setting Undefined MP: current MP: {}, new MP: {}, current track: {}, current aspect: {}, permit track: {}'\
                    .format(self._curr_MP, new_MP, self.curr_track_head, self.curr_sig.aspect, self.curr_sig.permit_track))
        self.time_pos_list.append([self.system.sys_time + self.system.refresh_time, self._curr_MP])

    @property
    def curr_speed(self):
        return self._curr_speed

    @curr_speed.setter
    def curr_speed(self, new_speed):    # speed in unit of miles/second
        _old_speed = self._curr_speed
        if new_speed * _old_speed < 0:  
            # decelerating into a stop (speed value crossing zero)
            self._curr_speed = 0
        elif (self.curr_target_spd_abs - abs(new_speed)) * (self.curr_target_spd_abs - abs(_old_speed)) < 0:
            # decelerating or accelerating into current target speed (speed value crossing target speed absolute value)
            self._curr_speed = self.curr_target_spd_abs if _old_speed >= 0 else -self.curr_target_spd_abs 
        else:
            # normal deceleration or acceleration
            self._curr_speed = new_speed
        # TODO: check if brake calculation is needed to be implemented here or self.curr_acc
        assert self.curr_brake_distance_abs <= self.curr_dis_to_curr_sig_abs

    @property
    def curr_acc(self):     # acc in unit of miles/(second)^2
        if not self.stopped:
            if self.curr_prev_sigpoint:
                if self.curr_target_spd_abs > abs(self.curr_speed):        
                    return self.max_acc \
                        if self.curr_sig.MP > self.curr_prev_sigpoint.signal_by_port[self.curr_prev_sigport].MP \
                        else -self.max_acc
                elif self.curr_target_spd_abs == abs(self.curr_speed):
                    return 0
                elif self.curr_target_spd_abs < abs(self.curr_speed):
                    if self.hold_speed_before_dcc:
                        return 0
                    else:
                        return -self.max_dcc \
                            if self.curr_sig.MP > self.curr_prev_sigpoint.signal_by_port[self.curr_prev_sigport].MP \
                                else self.max_dcc
            elif not self.curr_prev_sigpoint:
                if self.curr_target_spd_abs > abs(self.curr_speed):
                    return self.max_acc \
                        if self.curr_sig.MP == min(self.curr_sig.permit_track.MP) \
                        else -self.max_acc
                elif self.curr_target_spd_abs == abs(self.curr_speed):
                    return 0
                else:
                    return -self.max_dcc \
                        if self.curr_sig.MP == min(self.curr_sig.permit_track.MP) \
                        else self.max_dcc

        else:   # either stopped or out of system
            return 0
                # TODO: check if brake calculation is needed to be implemented here or self.curr_speed.

    @property
    def curr_target_spd_abs(self): 
        _curr_sig_trgt_speed_abs = float('inf')
        _curr_track_head_allow_sp_abs = getattr(self.curr_track_head, 'allow_sp',float('inf'))
        _curr_sig_permit_track_allow_sp = float('inf')
        if self.curr_sig:
            _curr_sig_trgt_speed_abs = self.curr_sig.aspect.target_speed
            if self.curr_sig.permit_track:
                _curr_sig_permit_track_allow_sp = self.curr_sig.permit_track.allow_sp
        _tgt_spd = min( _curr_sig_trgt_speed_abs, \
                        _curr_track_head_allow_sp_abs, \
                        _curr_sig_permit_track_allow_sp)
        assert _tgt_spd >= 0.0
        return _tgt_spd

    @property
    def curr_brake_distance_abs(self):  # in miles
        return self.abs_brake_distance(self.curr_speed, self.curr_target_spd_abs, self.curr_acc)
        
    @property
    def curr_dis_to_curr_sig_abs(self):
        return abs(self.curr_sig.MP - self.curr_MP)

    @property
    def hold_speed_before_dcc(self):
        assert self.curr_target_spd_abs < abs(self.curr_speed)
        assert self.curr_sig
        
        delta_s = self.curr_speed * self.system.refresh_time
        if abs(self.curr_sig.MP - (self.curr_MP + delta_s)) > \
            self.abs_brake_distance(self.curr_speed, self.curr_target_spd_abs, self.max_dcc) and\
                abs(self.curr_sig.MP - self.curr_MP) > abs(delta_s):
            return True
        else:
            return False

    def __lt__(self, othertrain):
        if self.curr_MP > othertrain.curr_MP:
            return True
        elif self.curr_MP < othertrain.curr_MP:
            return False
        # when the MP is the same:
        elif self.max_speed > othertrain.max_speed:
            return True
        elif self.max_speed < othertrain.max_speed:
            return False
        # elif self.rank < othertrain.rank:
        #     return False
        else:
            return True

    def cross_sigpoint(self, sigpoint, curr_MP, new_MP):
        # not yet implemented interlockings with geographical spans
        
        assert self.curr_sig.route in sigpoint.current_routes
        assert self.curr_sig in [sig for p,sig in sigpoint.signal_by_port.items()]
        assert min(curr_MP, new_MP) <= self.curr_sig.MP <= max(curr_MP, new_MP)
        assert not self.stopped
        _route = getattr(self.curr_sig, 'route')
        _permit_track = getattr(self.curr_sig,'permit_track')
        _next_enroute_sigpoint = getattr(self.curr_sig,'next_enroute_sigpoint')
        _next_enroute_sigpoint_port = getattr(self.curr_sig, 'next_enroute_sigpoint_port')
        terminate = False if _next_enroute_sigpoint else True
        initiate = False if self.curr_prev_sigpoint else True
        
        if self.curr_speed != 0:
            timestamp = self.system.sys_time + abs(curr_MP - self.curr_sig.MP)/abs(self.curr_speed)
        else:
            timestamp = self.system.sys_time
        self.time_pos_list.append([timestamp, self.curr_sig.MP])

        if initiate:
            assert isinstance(sigpoint, ControlPoint)
            assert len(self.curr_sig.permit_track.train) == 0
            print('train {} initiated and moved into track {}'.format(self, _permit_track))
            self.curr_sig.permit_track.train.append(self)
            sigpoint.close_route(_route)
            self.curr_routing_path_segment = ((sigpoint, _route[1]), (_next_enroute_sigpoint, _next_enroute_sigpoint_port))
            
        elif terminate:
            assert isinstance(sigpoint, ControlPoint)
            self.curr_track_head.train.remove(self)
            sigpoint.close_route(_route)
            self.curr_routing_path_segment = ((sigpoint, _route[1]), (None, None))
            
        elif not initiate and not terminate:
            assert len(self.curr_sig.permit_track.train) == 0
            self.curr_sig.permit_track.train.append(self)
            self.curr_track_head.train.remove(self)
            #-------------------------------------------#
            #---when add length, need modification------#
            #-------------------------------------------#
            if isinstance(sigpoint, ControlPoint):
                sigpoint.close_route(_route)
            self.curr_routing_path_segment = ((sigpoint, _route[1]), (_next_enroute_sigpoint, _next_enroute_sigpoint_port))
            
        else:
            raise ValueError('train {} crossing signalpoint {} failed unexpectedly'\
                .format(self, sigpoint))
    
    def update_acc(self):
        if not self.stopped:
            delta_s = self.curr_speed * self.system.refresh_time + 0.5 * self.curr_acc * self.system.refresh_time ** 2
            self.curr_speed = self.curr_speed + self.curr_acc * self.system.refresh_time
            self.curr_MP += delta_s
        self.time_pos_list.append([self.system.sys_time+self.system.refresh_time, self.curr_MP])
            # # 下一个delta_s之后，要越界且还没有减速到target speed.
            # if self.curr_MP > self.curr_track_head.MP:
            #     set new curr_track_head
            #     curr_track_head = self.system.blocks[self.curr_track_head]     
            #     # 如果当前的blk是最后一个blk  
            #     if self.curr_track_head == len(self.system.blocks) - 1:
            #         curr_track_head.free_track(self.curr_track_head)
            #         return
            #     if self.curr_track_head == -1:
            #         self.curr_MP = self.system.block_intervals[-1][1]
            #         return 
            #     curr_track_head = curr_track_head.tracks[self.curr_track_head]
            #     signal_color = curr_track_head.right_signal.color
            #     trgt_spd = curr_track_head.allow_sp
            #     next_blk = self.system.blocks[self.curr_track_head + 1]

            #     # 如果不是红色，正常往前走delta_s, 速度变为traget speed, 并且变化curr_track_head, curr_track_head
            #     if signal_color != 'r':
            #         next_ava_track = next_blk.find_available_track()
            #         self.curr_track_head += 1
            #         curr_track_head.free_track(self.curr_track_head)
            #         next_blk.occupied_track(next_ava_track, self)
            #     # 如果信号灯为红色，立即停车，火车属性不做改变。
            #     if signal_color == 'r':
            #         self.curr_MP = self.system.block_intervals[self.curr_track_head][1]
            #         self.curr_speed = 0
                
            #     if self.curr_speed > trgt_spd:
            #         self.curr_speed = trgt_spd
        
        

    def stop(self):
        self.curr_speed = 0
        self.status = 0
     
    def start(self):
        self.curr_speed = self.max_speed
        self.status = 1
    
    def terminate(self):
        self.status = 2
        
    def proceed(self, dest=None):
        self.start()
        if not dest:
            self.curr_MP += self.curr_speed * self.system.refresh_time
        else:
            self.curr_MP = dest
        self.time_pos_list.append([self.system.sys_time+self.system.refresh_time, self.curr_MP])
        
    def proceed_a(self, delta_s, dest=None):
        # if delta_s < 0:
        #     delta_s = 0
        if self.curr_speed + self.curr_acc * self.system.refresh_time > self.max_speed:
            self.curr_speed = self.max_speed
            self.curr_acc = 0
        else:
            self.curr_speed += self.curr_acc * self.system.refresh_time

        if not dest:
            self.curr_MP += delta_s 
            #===================================================================
            # if self.curr_MP > self.system.block_intervals[self.curr_track_head][1]:
            #     self.curr_track_head+=1           
            #===================================================================
        else:
            self.curr_MP = dest
        self.time_pos_list.append([self.system.sys_time+self.system.refresh_time, self.curr_MP])
    
    def stop_at_block_end(self, blk_idx):
        # assert self.curr_MP + self.curr_speed * self.system.refresh_time >= self.self.system.block_intervals[self.curr_track_head][1]
        if self.curr_speed > 0:
            interpolate_time = abs(self.system.block_intervals[blk_idx][1]-self.curr_MP)/self.curr_speed + self.system.sys_time
            self.curr_MP = self.system.block_intervals[blk_idx][1]
            self.time_pos_list.append([interpolate_time, self.curr_MP])
        if self.curr_speed == 0:
            self.curr_MP = self.curr_MP
            self.time_pos_list.append([self.system.sys_time+self.system.refresh_time, self.curr_MP])
        self.stop()
        
    def leave_block(self, blk_idx):
        self.system.blocks[blk_idx].free_track(self.curr_track_head)
        self.blk_time[blk_idx].append(self.system.sys_time)
        # interpolate the time moment when the train leaves the system
        if blk_idx == len(self.system.blocks)-1:
            interpolate_time = (self.system.block_intervals[blk_idx][1] - self.curr_MP) / self.curr_speed + self.system.sys_time
            self.curr_MP = self.system.block_intervals[blk_idx][1]
            self.time_pos_list.append([self.system.sys_time, self.curr_MP])
        
    def enter_block(self, blk_idx, next_block_ava_track):
        self.system.blocks[blk_idx].occupied_track(next_block_ava_track, self)
        self.curr_track_head = next_block_ava_track
        
    def update(self, dos_pos=-1):
        # update self.curr_MP
        # update self.curr_speed
        # if the train already at the end of the railway, do nothing. (no updates on (time,pos))
        if self.curr_MP == self.system.block_intervals[-1][1]:
            pass
        # If the train arrives at the end of all the blocks, the train will leave the system.
        elif self.is_leaving_system(self.curr_speed * self.system.refresh_time):
            self.leave_block(len(self.system.block_intervals) - 1)
            self.curr_track_head = None
            self.proceed(dest=self.system.block_intervals[-1][1])
        # The train will still stay in current block in next refresh time, so continue the system.
        elif self.is_normal_proceed(self.curr_speed * self.system.refresh_time):
            self.curr_track_head = self.curr_track_head
            self.proceed(self.system)
        # If the next block has no available tracks 
        # the train will stop at end of current block.
        elif (not self.system.blocks[self.curr_track_head+1].is_Occupied()): 
            self.stop_at_block_end(self.curr_track_head)
        # If or there is a dos at the end of current block
        # the train will stop at end of current block.
        elif self.is_during_dos(dos_pos):
            self.stop_at_block_end(self.curr_track_head)
        #If next train is faster than this train, the postion of previous train is behind the start
        # of this block, let this train stop at the end of block.
        elif self.is_leaving_block(self.max_speed * self.system.refresh_time)\
            and self.rank < self.system.train_num - 1\
            and self.max_speed < self.system.trains[self.rank + 1].max_speed\
            and self.system.trains[self.rank + 1].curr_MP >=\
                self.system.block_intervals[self.system.trains[self.rank].curr_track_head - 1][0]\
            and self.system.blocks[self.curr_track_head].is_Occupied():
                self.stop_at_block_end(self.curr_track_head)
        # If the train will enter the next block in next refresh time,
        # update the system info and the train info.
        elif self.is_leaving_block(self.curr_speed * self.system.refresh_time): 
            self.leave_block(self.curr_track_head)
            next_block_ava_track = self.system.blocks[self.curr_track_head + 1].find_available_track()
            self.enter_block(self.curr_track_head+1, next_block_ava_track)
            self.curr_track_head += 1
            self.proceed(self.system)
   
    def select_move_model(self):
        # print("current block index: {}".format(self.curr_track_head))
        if self.curr_track_head == None:
            return 0
        curr_block = self.system.blocks[self.curr_track_head]
        if self.curr_speed + self.curr_acc * self.system.refresh_time > self.max_speed:
            self.curr_acc = 0
            return self.max_speed * self.system.refresh_time
        break_distance = (self.curr_speed ** 2 - self.system.blocks[self.curr_track_head].trgt_speed ** 2) / (2 * self.acc)
        
        # assert break_distance <= self.system.block_intervals[self.curr_track_head][1] - self.curr_MP
        
        if self.curr_speed < curr_block.trgt_speed:
            self.curr_acc = self.acc
        elif self.curr_speed > curr_block.trgt_speed:
            if break_distance >= self.system.block_intervals[self.curr_track_head][1] - self.curr_MP:
                self.curr_acc = - self.acc
            elif break_distance < self.system.block_intervals[self.curr_track_head][1] - self.curr_MP:
                self.curr_acc = self.acc
        else:
            self.curr_acc = 0
        
        delta_s = self.curr_speed * self.system.refresh_time + 0.5 * self.curr_acc * self.system.refresh_time ** 2
        # print(delta_s)
        return delta_s

    def cal_increment(self):
        # print("current block index: {}".format(self.curr_track_head))
        if self.curr_track_head == None:
            return 0
        curr_block = self.system.blocks[self.curr_track_head]
        if self.curr_speed < 0 and self.curr_acc < 0:
            self.curr_speed = 0
        if self.curr_speed < curr_block.trgt_speed and self.curr_speed < self.max_speed:
            self.curr_acc = self.acc
        elif self.curr_speed > curr_block.trgt_speed and self.curr_speed > 0:
            self.curr_acc = -self.acc
        else:
            self.curr_acc = 0
        
        delta_s = self.curr_speed * self.system.refresh_time + 0.5 * self.curr_acc * self.system.refresh_time ** 2
        # print(delta_s)
        return delta_s

    def update_a(self, dos_pos=-1):
        if not self.curr_track_head == None:
            assert  self.system.block_intervals[self.curr_track_head][0] <= self.curr_MP <= self.system.block_intervals[self.curr_track_head][1]
        delta_s = self.cal_increment()
        # update self.curr_MP
        # update self.curr_speed
        
        # IF the train already at the end of the railway and OUT OF THE SYSTEM 
        # Right now the self.curr_track_head == None
        # Do nothing. (no updates on (time,pos))
        # 看车是不是已经出了系统：
        if self.is_terminated():
            # print('1')
            pass
        # If the train is WITHIN the system;    如果车还在系统里，
        # If the train arrives at the end of the system, the train will leave the system.    如果车即将离开系统、位于系统末端（尾部block的末端）
        elif self.is_leaving_system(delta_s):
            # print('2')
            self.leave_block(len(self.system.block_intervals) - 1)
            self.curr_track_head = None
            self.proceed_acc(delta_s, dest=self.system.block_intervals[-1][1])
        # '''从这里往下的判断条件，不一定互斥，有重合的地方，所以有可能进错条件'''
        # If the train is WITHIN the system;    如果车还在系统里，
        # If the train is NOT at the end of the system;    如果车不在系统末端，
        # If there is a DoS at the end of its current block;    如果DoS的时间段与本车本区间block吻合，
        # the train will stop at end of current block.
        elif self.is_during_dos(dos_pos):
            # print('3')
            self.proceed_acc(delta_s)
            
        # If the train is WITHIN the system;    如果车还在系统里，
        # If the train is NOT at the end of the system;    如果车不在系统末端，
        # If there NO DoS at the end of the current block;    如果DoS时间地点都不吻合，
        # If the next block has no available tracks    如果下个blk没有track，
        # the train will stop at end of current block.    
        
        elif self.is_stopped_by_previous_train(delta_s): 
            # print('4')
            self.stop_at_block_end(self.curr_track_head)
            
        # If the train is WITHIN the system;    如果车还在系统里，
        # If the train is NOT at the end of the system;    如果车不在系统末端，
        # If there NO DoS at the end of the current block;    如果DoS时间地点都不吻合，
        # If the next block HAS available tracks;    如果下个blk有track，
        # If the train is determined to be passed by the train behind    如果判断在这个区间让后车，
        # the train will proceed with updated acceleration (to slow down and stop)
        # 但是这里有可能闯出现在的block。没有把条件写成互斥的形式。
        elif self.let_faster_train():
            # print('5')
            # if self.curr_MP > self.system.block_intervals[self.curr_track_head][1]:
            #     print("$$$$$$$$$$$")
            if self.curr_speed > 0:
                self.curr_acc = -self.acc
            delta_s = self.curr_speed * self.system.refresh_time + 0.5 * self.curr_acc * self.system.refresh_time ** 2
            if self.curr_MP + delta_s > self.system.block_intervals[self.curr_track_head][1]:
                if self.system.blocks[self.curr_track_head + 1].is_Occupied():
                    next_block_ava_track = self.system.blocks[self.curr_track_head + 1].find_available_track()
                    self.leave_block(self.curr_track_head)
                    self.curr_track_head += 1
                    self.enter_block(self.curr_track_head, next_block_ava_track)
                else:
                    self.stop_at_block_end(self.curr_track_head)
            self.proceed_acc(delta_s)
        # If the train is WITHIN the system;    如果车还在系统里，
        # If the train is NOT at the end of the system;    如果车不在系统末端，
        # If there NO DoS at the end of the current block;    如果DoS时间地点都不吻合，
        # If the next block HAS available tracks;    如果下个blk有track，
        # If the train NOT to stop and let the train behind to pass;   如果判断在这个区间不让后车
        # the train will proceed regularly. No special updates 
        elif self.is_normal_proceed(delta_s):
            # print('6')
            self.proceed_acc(delta_s)
        # If the train is WITHIN the system;    如果车还在系统里，
        # If the train is NOT at the end of the system;    如果车不在系统末端，
        # If there NO DoS at the end of the current block;    如果DoS时间地点都不吻合，
        # If the next block HAS available tracks;    如果下个blk有track，
        # If the train NOT to stop and let the train behind to pass;   如果判断在这个区间不让后车
        # If the train will not proceed regularly within a block;     如果不是在区间内正常行驶（如果马上要穿越区间blk）
        # the train will cross the border of two blocks.
        elif self.is_leaving_block(delta_s):
            #===================================================================
            # print('7')
            # print('train',self.train_idx,self.rank,self.curr_track_head)
            #===================================================================
            if self.system.blocks[self.curr_track_head + 1].is_Occupied():
                next_block_ava_track = self.system.blocks[self.curr_track_head + 1].find_available_track()
            self.leave_block(self.curr_track_head)
            self.enter_block(self.curr_track_head+1, next_block_ava_track)
            self.curr_track_head += 1
            self.proceed_acc(delta_s)
        
        # if (not self.curr_track_head == None) and self.curr_MP > self.system.block_intervals[self.curr_track_head][1]:
        #     self.curr_track_head += 1

        # What else?     剩余情况待分析。
        
    def is_terminated(self):
        '''
        Determined the train should stop or not because of the next block has a train.
        @return True or False
        '''
        return self.curr_MP == self.system.block_intervals[-1][1] and self.curr_track_head == None
    
    def is_leaving_block(self, delta_s):
        return self.curr_MP + delta_s > self.system.block_intervals[self.curr_track_head][1]

    def is_stopped_by_previous_train(self, delta_s):
        '''
        Determined the train should stop or not because of the next block has a train.
        @return: True or False
        '''
        return self.is_leaving_block(delta_s) and (not self.system.blocks[self.curr_track_head+1].is_Occupied())

    def is_normal_proceed(self, delta_s):
        '''
        Whether the train is still in current block in next refresh time.
        @return: True or False
        '''
        return self.curr_MP + delta_s < self.system.block_intervals[self.curr_track_head][1]

    def is_leaving_system(self, delta_s):
        '''
        Whether the train is leaving the last block of system
        @return: True or False
        '''
        return self.curr_MP + delta_s >= self.system.block_intervals[-1][1]

    def is_during_dos(self, dos_pos):
        '''
        Whether the train is during the dos pos and time period
        @return: True or False
        '''
        return dos_pos == self.curr_track_head and self.system.dos_period[0] <= self.system.sys_time <= self.system.dos_period[1]

    def let_faster_train(self):
        '''
        If the next train is faster than self train,
        self train should let faster train go though.
        @return: True or False
        '''
        return self.rank < self.system.train_num - 1 and self.max_speed < self.system.trains[self.rank + 1].max_speed\
            and ((self.system.trains[self.rank + 1].curr_track_head == self.curr_track_head - 1\
                and self.system.blocks[self.curr_track_head].is_Occupied())\
            or self.system.trains[self.rank + 1].curr_track_head == self.curr_track_head)

    
                
            
                    
                