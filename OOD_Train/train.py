#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import numpy as np
from datetime import datetime, timedelta
from infrastructure import Track, BigBlock
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
    
    @staticmethod
    def sign_MP(rp_seg):
        # return the sign (+/-) of speed when input with
        # a legit routing path segment of a train
        if rp_seg[0][0] and rp_seg[1][0]:
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP > rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP < rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return -1
            else:
                raise ValueError('Undefined MP direction')
        elif not rp_seg[0][0]:
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == min(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == max(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')
        elif not rp_seg[1][0]:
            if rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == max(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return 1
            elif rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == min(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')

    def __init__(self, idx, rank, system, init_time, init_segment, max_sp, max_acc, max_dcc, **kwargs):        
        ((_curr_prev_sigpoint,_prev_sigport),(_curr_sigpoint, _prev_sigport)) = init_segment
        self.length = 0         if not kwargs.get('length') else kwargs.get('length')
        self.system = system
        self._curr_routing_path_segment = init_segment
        self._curr_occuping_routing_path = [self._curr_routing_path_segment]
        self._curr_MP = self.curr_sig.MP
        self._rear_curr_MP = self.curr_MP - self.length * self.sign_MP(self.curr_routing_path_segment)
        self.train_idx = idx
        self.rank = rank
        self.system.trains.append(self)
        self.max_speed = max_sp
        self.max_acc = max_acc
        self.max_dcc = max_dcc

        self._curr_speed = 0
        # initial speed limit, considering both cases: with current track and without current tracks
        self._curr_spd_lmt_abs = min(20/3600, self.curr_track.allow_sp) if self.curr_track \
            else min(20/3600, float('inf'))
        self._stopped = True
        
        self.time_pos_list = []
        self.rear_time_pos_list = []
        self.pos_spd_list = []
        
        if self.curr_track:
            if self not in self.curr_track.train:
                self.curr_track.train.append(self)

    def __repr__(self):
        return 'train index {}, current occupying sections: {}, head MP: {}, rear MP {}'\
            .format(self.train_idx, self.curr_occuping_routing_path, \
                str("%.2f" % round(self.curr_MP,2)).rjust(5,' '), str("%.2f" % round(self.rear_curr_MP,2)).rjust(5,' '))
    
    @property
    def terminated(self):
        '''
        Status property show if the train has exited the confined rail network
        @return True or False
        '''
        return True if (not self.curr_routing_path_segment[1][0] and not self.rear_curr_track) else False

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
    def curr_track(self):
        return self.system.get_track_by_point_port_pairs\
            (self.curr_prev_sigpoint, self.curr_prev_sigport, self.curr_sigpoint, self.curr_sigport)

    @property
    def rear_curr_track(self):
        return self.system.get_track_by_point_port_pairs\
            (self.rear_curr_prev_sigpoint, self.rear_curr_prev_sigport, self.rear_curr_sigpoint, self.rear_curr_sigport)

    @property
    def curr_occuping_routing_path(self):
        # a list of routing path tuples being occupied by self (in order from head to rear)
        return self._curr_occuping_routing_path

    @property
    def curr_tracks(self):
        # a list of track instances being occupied by self (in order from head to rear)
        _curr_tracks = []
        for r in self.curr_occuping_routing_path:
            _track = self.system.get_track_by_point_port_pairs(r[0][0],r[0][1],r[1][0],r[1][1])
            if _track:
                _curr_tracks.append(_track)
        return _curr_tracks

    @property
    def curr_bigblock_routing(self):
        return self.curr_track.bigblock.routing

    @property
    def curr_routing_path(self):
        # only describes the routing for the head section. Not considering the length.
        return self.curr_track.curr_routing_path if self.curr_track else None

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
    def rear_curr_sigpoint(self):
        return self.curr_occuping_routing_path[-1][1][0]
    @property
    def rear_curr_prev_sigpoint(self):
        return self.curr_occuping_routing_path[-1][0][0]    
    @property
    def rear_curr_sigport(self):
        return self.curr_occuping_routing_path[-1][1][1]
    @property
    def rear_curr_prev_sigport(self):
        return self.curr_occuping_routing_path[-1][0][1]

    @property
    def curr_sig(self):
        return self.curr_sigpoint.signal_by_port[self.curr_sigport] \
            if self.curr_sigpoint \
            else None
    @property
    def rear_curr_sig(self):
        return self.rear_curr_sigpoint.signal_by_port[self.rear_curr_sigport] \
            if self.rear_curr_sigpoint \
            else None
    
    @property
    def curr_MP(self):
        if self.curr_track:
            assert  min(self.curr_track.MP) <= self._curr_MP <= max(self.curr_track.MP)
        return self._curr_MP

    @curr_MP.setter
    def curr_MP(self, new_MP):
        _delta_s = new_MP - self._curr_MP
        if self.terminated:
            assert self.curr_prev_sigpoint
            self._curr_MP = self.curr_prev_sigpoint.signal_by_port[self.curr_prev_sigport].MP
        else:
            # calling the MP should consider switching lines with MP gaps
            if self.curr_sigpoint:
                if self.curr_track:
                    # not initiating
                    if min(self.curr_track.MP) < new_MP < max(self.curr_track.MP):  
                        # within a track
                        self._curr_MP = self._curr_MP + _delta_s
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
                    self._curr_MP = _new_prev_sig_MP + (new_MP - _curr_sig_MP)
            else: 
                # head out of the system, dragging the rear out
                self._curr_MP = self._curr_MP + _delta_s
        self.rear_curr_MP = self.rear_curr_MP + _delta_s        
        # setting the new rear MP using the same delta_s
        self.time_pos_list.append([self.system.sys_time, self.curr_MP])

    @property
    def rear_curr_MP(self):
        if self.rear_curr_track:
            assert  min(self.rear_curr_track.MP) <= self._rear_curr_MP <= max(self.rear_curr_track.MP)
        return self._rear_curr_MP
    
    @rear_curr_MP.setter
    def rear_curr_MP(self, new_rear_MP):
        if not self.length:
            self._rear_curr_MP = self.curr_MP
        else:
            _delta_s = new_rear_MP - self._rear_curr_MP
            if self.rear_curr_sigpoint:
                if self.rear_curr_track:
                    # not initiating
                    if min(self.rear_curr_track.MP) < new_rear_MP < max(self.rear_curr_track.MP):  
                        # rear within a track
                        self._rear_curr_MP = self._rear_curr_MP + _delta_s
                    else:
                        assert len(self.curr_occuping_routing_path) >= 2
                        _rear_route = (self.curr_occuping_routing_path[-1][1][1], self.curr_occuping_routing_path[-2][0][1])
                        # rear entering a new track; crossing current rear signal point
                        # new track of the train rear may have a separate MP system
                        _new_rear_prev_sig_MP = self.rear_curr_sigpoint.signal_by_port[_rear_route[1]].MP
                        _rear_curr_sig_MP = self.rear_curr_sigpoint.signal_by_port[_rear_route[0]].MP
                        self.rear_cross_sigpoint(self.rear_curr_sigpoint, self._rear_curr_MP, new_rear_MP)
                        self._rear_curr_MP = _new_rear_prev_sig_MP + (new_rear_MP - _rear_curr_sig_MP)
                else:
                    # initiating, rear cross the entry control point
                    assert len(self.curr_occuping_routing_path) >= 2
                    if (new_rear_MP - self.rear_curr_sig.MP) * (self._rear_curr_MP - self.rear_curr_sig.MP) < 0:
                        # rear entering a new track because the train fully entered track; 
                        # crossing current rear signal point new track of the train rear may have a separate MP system
                        _rear_route = (self.curr_occuping_routing_path[-1][1][1], self.curr_occuping_routing_path[-2][0][1])
                        _new_rear_prev_sig_MP = self.rear_curr_sigpoint.signal_by_port[_rear_route[1]].MP
                        _rear_curr_sig_MP = self.rear_curr_sigpoint.signal_by_port[_rear_route[0]].MP
                        self.rear_cross_sigpoint(self.rear_curr_sigpoint, self._rear_curr_MP, new_rear_MP)
                        self._rear_curr_MP = _new_rear_prev_sig_MP + (new_rear_MP - _rear_curr_sig_MP)
                    else:
                        # not crossing current rear signal point (the entry ControlPoint)
                        self._rear_curr_MP += _delta_s
            else: 
                raise ValueError('Setting Undefined rear MP: current rear MP: {}, new rear MP: {}, current rear track: {}'\
                    .format(self._rear_curr_MP, new_rear_MP, self.rear_curr_track))
        self.rear_time_pos_list.append([self.system.sys_time, self.rear_curr_MP])

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
            print('train {} initiated entering into track {}'.format(self, _permit_track))
            self.curr_spd_lmt_abs = self.curr_target_spd_abs
            self.curr_sig.permit_track.train.append(self)
            sigpoint.curr_train_with_route[self] = _route
            sigpoint.close_route(_route)
            self.curr_routing_path_segment = ((sigpoint, _route[1]), (_next_enroute_sigpoint, _next_enroute_sigpoint_port))
            self.curr_occuping_routing_path.insert(0,self.curr_routing_path_segment)

        elif not initiate and not terminate:
            assert len(self.curr_sig.permit_track.train) == 0
            self.curr_spd_lmt_abs = self.curr_target_spd_abs
            self.curr_sig.permit_track.train.append(self)
            sigpoint.curr_train_with_route[self] = _route
            if isinstance(sigpoint, ControlPoint):
                sigpoint.close_route(_route)
            self.curr_routing_path_segment = ((sigpoint, _route[1]), (_next_enroute_sigpoint, _next_enroute_sigpoint_port))
            self.curr_occuping_routing_path.insert(0,self.curr_routing_path_segment)

        elif terminate:
            assert isinstance(sigpoint, ControlPoint)
            self.curr_spd_lmt_abs = self.curr_target_spd_abs
            sigpoint.curr_train_with_route[self] = _route
            sigpoint.close_route(_route)
            self.curr_routing_path_segment = ((sigpoint, _route[1]), (None, None))
            self.curr_occuping_routing_path.insert(0,self.curr_routing_path_segment)
        
        else:
            raise ValueError('train {} crossing signalpoint {} failed unexpectedly'\
                .format(self, sigpoint))

    def rear_cross_sigpoint(self, sigpoint, rear_curr_MP, new_rear_MP):
        # not yet implemented interlockings with geographical spans
        
        assert self in sigpoint.curr_train_with_route.keys()
        assert self.rear_curr_sig in [sig for p,sig in sigpoint.signal_by_port.items()]
        assert min(rear_curr_MP, new_rear_MP) <= self.rear_curr_sig.MP <= max(rear_curr_MP, new_rear_MP)
        assert not self.stopped

        if self.curr_speed != 0:
            timestamp = self.system.sys_time + abs(rear_curr_MP - self.rear_curr_sig.MP)/abs(self.curr_speed)
        else:
            timestamp = self.system.sys_time
        self.rear_time_pos_list.append([timestamp, self.rear_curr_sig.MP])    
        del sigpoint.curr_train_with_route[self]
        if self.rear_curr_track:
            self.rear_curr_track.train.remove(self)
        self.curr_occuping_routing_path.pop(-1)
        #---------dispatching logic may need to modify here 
        #---------to determine if further bigblock actions are needed    
    
    @property
    def curr_speed(self):
        return self._curr_speed

    @curr_speed.setter
    def curr_speed(self, new_speed):    # speed in unit of miles/second
        _old_speed = self._curr_speed
        if new_speed * _old_speed >=0:
            if abs(new_speed) > abs(_old_speed):
                if (self.curr_spd_lmt_abs - abs(new_speed)) * (self.curr_spd_lmt_abs - abs(_old_speed)) < 0:
                    # accelerating into current speed limit (speed value crossing speed limit absolute value)
                    self._curr_speed = self.curr_spd_lmt_abs if _old_speed >= 0 else -self.curr_spd_lmt_abs 
                else:
                    # normal deceleration or acceleration
                    self._curr_speed = new_speed
            elif abs(new_speed) < abs(_old_speed):
                if (self.curr_target_spd_abs - abs(new_speed)) * (self.curr_target_spd_abs - abs(_old_speed)) < 0:
                    # decelerating into current target speed (speed value crossing target speed absolute value)
                    self._curr_speed = self.curr_target_spd_abs if _old_speed >= 0 else -self.curr_target_spd_abs 
                else:
                    # normal deceleration or acceleration
                    self._curr_speed = new_speed
            else:
                self._curr_speed = new_speed
        else:
            # decelerating into a stop (speed value crossing zero)
            self._curr_speed = 0
        assert self.curr_brake_distance_abs <= self.curr_dis_to_curr_sig_abs
        # TODO: check if brake calculation is needed to be implemented here or self.curr_acc
    @property
    def curr_acc(self):     # acc in unit of miles/(second)^2
        _direction_sign = self.sign_MP(self.curr_routing_path_segment)
        if self.stopped:    # either stopped or out of system
            return 0
        else:
            assert abs(self.curr_speed) <= self.curr_spd_lmt_abs
            if abs(self.curr_speed) == self.curr_spd_lmt_abs:
                if self.curr_target_spd_abs >= self.curr_spd_lmt_abs:
                    return 0
                else:
                    if self.hold_speed_before_dcc(self.curr_MP, self.curr_sig.MP, self.curr_speed, self.curr_target_spd_abs):
                        return 0
                    else:
                        return self.max_dcc * (-1) * _direction_sign
            else:
                if self.curr_target_spd_abs >= self.curr_spd_lmt_abs:
                    return self.max_acc * _direction_sign
                elif abs(self.curr_speed) < self.curr_target_spd_abs < self.curr_spd_lmt_abs:
                    return self.max_acc * _direction_sign
                
                # elif self.curr_target_spd_abs <= abs(self.curr_speed) < self.curr_spd_lmt_abs:
                #     if self.acc_before_dcc(self.curr_MP, self.curr_sig.MP, self.curr_speed, self.curr_target_spd_abs):
                #         return self.max_acc * _direction_sign
                #     elif self.hold_speed_before_dcc(self.curr_MP, self.curr_sig.MP, self.curr_speed, self.curr_target_spd_abs):
                #         return 0
                #     else:
                #         return self.max_dcc * (-1) * _direction_sign
                    
                # TODO: check if brake calculation is needed to be implemented here or self.curr_speed.

    @property
    def curr_target_spd_abs(self): 
        # if exit the system, target speed is inf.
        _curr_sig_trgt_speed_abs = float('inf')
        _curr_track_allow_sp_abs = getattr(self.curr_track, 'allow_sp',float('inf'))
        _curr_sig_permit_track_allow_sp = float('inf')
        if self.curr_sig:                       # waiting to initiate
            _curr_sig_trgt_speed_abs = self.curr_sig.aspect.target_speed
            if self.curr_sig.permit_track:      # initiating
                _curr_sig_permit_track_allow_sp = self.curr_sig.permit_track.allow_sp
        _tgt_spd = min( _curr_sig_trgt_speed_abs, \
                        _curr_track_allow_sp_abs, \
                        _curr_sig_permit_track_allow_sp)
        assert _tgt_spd >= 0.0
        return _tgt_spd

    @property
    def curr_spd_lmt_abs(self): 
        assert self._curr_spd_lmt_abs > 0
        return self._curr_spd_lmt_abs
    
    @curr_spd_lmt_abs.setter
    def curr_spd_lmt_abs(self, spd_lmt):
        if self.curr_track:
            self._curr_spd_lmt_abs = self.curr_track.allow_sp \
            if spd_lmt > self.curr_track.allow_sp \
            else spd_lmt
        else:
            self._curr_spd_lmt_abs = spd_lmt

    @property
    def curr_brake_distance_abs(self):  # in miles
        return self.abs_brake_distance(self.curr_speed, self.curr_target_spd_abs, self.max_dcc)
        
    @property
    def curr_dis_to_curr_sig_abs(self):
        return abs(self.curr_sig.MP - self.curr_MP) if self.curr_sig else float('inf')
            
    def hold_speed_before_dcc(self, MP, tgt_MP, spd, tgt_spd):
        delta_s = spd * self.system.refresh_time
        if abs(tgt_MP - (MP + delta_s)) > \
            self.abs_brake_distance(spd, tgt_spd, self.max_dcc) and abs(tgt_MP - MP) > abs(delta_s):
                if abs(tgt_MP - (MP + delta_s*2)) > self.abs_brake_distance(spd, tgt_spd, self.max_dcc) and\
                    abs(tgt_MP - MP) > 2 * abs(delta_s):
                    return True
        return False
    
    def acc_before_dcc(self, MP, tgt_MP, spd, tgt_spd):
        assert self.curr_sig
        if self.hold_speed_before_dcc(MP, tgt_MP, spd, tgt_spd):
            _direction_sign = self.sign_MP(self.curr_routing_path_segment)
            delta_s = spd * self.system.refresh_time + 0.5 * (_direction_sign*self.max_acc) * self.system.refresh_time**2
            delta_spd = (_direction_sign * self.max_acc) * self.system.refresh_time
            delta_s_extra = (spd+delta_spd) * self.system.refresh_time + + 0.5 * (_direction_sign*self.max_acc) * self.system.refresh_time**2
            if abs(tgt_MP - (MP + delta_s)) > self.abs_brake_distance(spd + delta_spd, tgt_spd, self.max_dcc) \
                and abs(tgt_MP - MP) > abs(delta_s):
                    if abs(tgt_MP - (MP + delta_s_extra)) > self.abs_brake_distance(spd + 2*delta_spd, tgt_spd, self.max_dcc) \
                        and abs(tgt_MP - MP) > abs(delta_s_extra):
                        return True
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

    def update_acc(self):
        
        if not self.stopped:
            delta_s = self.curr_speed * self.system.refresh_time + 0.5 * self.curr_acc * self.system.refresh_time ** 2
            self.curr_speed = self.curr_speed + self.curr_acc * self.system.refresh_time
            self.curr_MP += delta_s
        else:
            self.time_pos_list.append([self.system.sys_time, self.curr_MP])
            self.rear_time_pos_list.append([self.system.sys_time, self.rear_curr_MP])
        self.pos_spd_list.append([self.curr_MP, self._curr_speed, self.curr_spd_lmt_abs, self.curr_target_spd_abs])

    def is_during_dos(self, dos_pos):
        '''
        Whether the train is during the dos pos and time period
        @return: True or False
        '''
        return dos_pos == self.curr_track and self.system.dos_period[0] <= self.system.sys_time <= self.system.dos_period[1]

    def let_faster_train(self):
        '''
        If the next train is faster than self train,
        self train should let faster train go though.
        @return: True or False
        '''
        return self.rank < self.system.train_num - 1 and self.max_speed < self.system.trains[self.rank + 1].max_speed\
            and ((self.system.trains[self.rank + 1].curr_track == self.curr_track - 1\
                and self.system.blocks[self.curr_track].is_Occupied())\
            or self.system.trains[self.rank + 1].curr_track == self.curr_track)

    
                
            
                    
                