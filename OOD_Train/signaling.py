#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    PyRailSim
    Copyright (C) 2019  Zezhou Wang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import defaultdict
from itertools import combinations, permutations

from observe import Observable, Observer

import infrastructure
from rail_networkx import all_simple_paths, shortest_path


class Aspect():
    """
    Aspect shows the meaning of the signals. 
    Could be compared with other aspects with more/less favorable comparison.
    """
    COLOR_SPD_MAP = {
        'r': 0.0, 
        'y': 20 / 3600, 
        'yy': 40 / 3600, 
        'g': 72 / 3600
        }

    def __init__(self, color, route=None):
        self.color = color
        self.route = route

    def __repr__(self):
        return 'Aspect: {}, \t route {}, target speed {} mph'.format(self.color, self.route, self.target_speed * 3600)

    @property
    def target_speed(self):
        return self.COLOR_SPD_MAP[self.color] if self.color else 0

    def __eq__(self, other):
        return self.color == other.color

    def __ne__(self, other):
        return self.color != other.color

    def __lt__(self, other):
        '''r < y < yy < g'''
        if self.color == 'r' and other.color != 'r':
            return True
        elif self.color == 'y' and (other.color == 'yy' or other.color == 'g'):
            return True
        elif self.color == 'yy' and (other.color == 'g'):
            return True
        else:
            return False

    def __gt__(self, other):
        '''g > yy > y > r'''
        if self.color == 'g' and other.color != 'g':
            return True
        elif self.color == 'yy' and (other.color == 'y' or other.color == 'r'):
            return True
        elif self.color == 'y' and (other.color == 'r'):
            return True
        else:
            return False

    def __le__(self, other):
        '''r <= y <= yy <= g'''
        if self.color == 'r':
            return True
        elif self.color == 'y' and (other.color != 'r'):
            return True
        elif self.color == 'yy' and (other.color == 'g' or other.color == 'yy'):
            return True
        elif self.color == 'g' and other.color == 'g':
            return True
        else:
            return False

    def __ge__(self, other):
        '''
        g >= yy >= y >= r
        '''
        if self.color == 'g':
            return True
        elif self.color == 'yy' and (other.color != 'g'):
            return True
        elif self.color == 'y' and (other.color == 'r' or other.color == 'y'):
            return True
        elif self.color == 'r' and other.color == 'r':
            return True
        else:
            return False


class Signal(Observable, Observer):
    '''
    Base class of a Signal object.
    '''
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__()
        self.system = None
        self.sigpoint = sigpoint
        self._MP = MP
        self.port_idx = port_idx
        self._aspect = Aspect('r', route=self.route) # Default aspect is red/r

        self._next_enroute_sigpoint = None

    @property
    def governed_track(self):
        '''
            Concept of "Governed Track" for a signal:
              o-                  o- (<-This signal)   o-               
            0:P:1===============0:P:1================0:P:1============
             -o                  -o                   -o               
                                  |-> Governed track <-|
            "0:P:1" - port_0:SigPnt:port_1
            @return:
                The track object governed by this signal.
        '''
        return self.sigpoint.track_by_port.get(self.port_idx)

    @property
    def permitted_track(self):
        '''
            Concept of "Permitted Track" for a signal:
              o-                    o- (<-This signal, Aspect 'g')     o-               
            0:P:1=================0:P:1==============================0:P:1============
             -o                    -o                                 -o               
              |-> Permitted Track <-|-> --------Governed track-------<-|
            "0:P:1" - port_0:SigPnt:port_1

            If there is an active route, there is a track segment to which  
            this signal permits movement authority.
            @return:
                The Track object to which the current route of the signal permits.
        '''
        return self.sigpoint.track_by_port.get(self.route[1]) if self.route else None

    @property
    def facing_MP_direction_sign(self):
        '''
            Concept of "Direction" for a signal:
              o-                  o- (<-This signal)   o-               
            0:P:1===============0:P:1================0:P:1============
             -o                  -o                   -o               
            MP-0              MP-5               MP-10
                               -> Governed track <-
                               Signal direction: <---- (-1)
            "0:P:1" - port_0:SigPnt:port_1
            @return:
                The sign (+1/-1) of the direction w.r.t. the milepost ascending/descending
        '''
        if self.governed_track:     
            # The signal has a track segment to govern: infer from track milepost
            if max(self.governed_track.MP) == self.MP:
                return 1
            elif min(self.governed_track.MP) == self.MP:
                return -1
            else:
                raise ValueError('Undefined MP direction')
        else:
            # The signal has NO track segment to govern 
            # (still has a neighbor signal point)
            # infer from the neighbor signal point on the other side
            return -self.sigpoint.signal_by_port[
                self.sigpoint.opposite_port(self.port_idx)
                ].facing_MP_direction_sign

    @property
    def upwards(self):
        '''
            Concept of "upward traffic stream" for a signal:
             o-                o- (<-This signal) o-               
            0:P:1===============0:P:1================0:P:1============
            -o                -o                 -o               
            MP-0              MP-5               MP-10
                               Signal direction (-1): <----
                               Traffic stream:        <---- (upwards)
            "0:P:1" - port_0:SigPnt:port_1
            Trains bounding for MP-0 are considered "up-bounding trains".
            @return:
                The sign (+1/-1) of the direction w.r.t. the milepost ascending/descending
        '''
        return True if self.facing_MP_direction_sign == -1 else False
    
    @property
    def downwards(self):
        '''
            Concept of "downward traffic stream" for a signal:
             o-                o-                 o-               
            0:P:1===============0:P:1================0:P:1============
            -o                -o (<-This signal) -o
            MP-0              MP-5               MP-10
                               Signal direction (+1): ---->
                               Traffic stream:        ----> (downwards)
            "0:P:1" - port_0:SigPnt:port_1
            Trains bounding for MP-∞ are considered "down-bounding trains".
            @return:
                The sign (+1/-1) of the direction w.r.t. the milepost ascending/descending
        '''
        return True if self.facing_MP_direction_sign == 1 else False

    @property
    def route(self):
        return self.sigpoint.current_route_by_port.get(self.port_idx)

    @property
    def MP(self):
        if not self._MP:
            self._MP = self.sigpoint.MP
        return self._MP

    @MP.setter
    def MP(self, new_MP):
        print('Warning:\n\tSetting MilePost manually for {}!\n\t\
            Changing from old MP {} to new MP {}'
            .format(self, self._MP, new_MP))
        self._MP = new_MP

    @property
    def aspect(self):
        '''
        TODO: Refactoring Under Devo
        '''
        # print('\tcall aspect of {} route {}'.format(self.sigpoint,self.route))
        self._aspect.route = self.route
        if not self.route:
            self._aspect.color = 'r'
        elif self.is_cleared_signal_to_exit_system:  # exiting the system
            self._aspect.color = 'g'
        else:
            if self.number_of_blocks_cleared_ahead == 0:
                self._aspect.color = 'r'
            elif self.number_of_blocks_cleared_ahead == 1:
                if self.next_enroute_signal.is_cleared_signal_to_exit_system:
                    self._aspect.color = 'g'
                else:
                    self._aspect.color = 'y'
            elif self.number_of_blocks_cleared_ahead == 2:
                if self.next_enroute_signal.next_enroute_signal.is_cleared_signal_to_exit_system:
                    self._aspect.color = 'g'
                else:
                    self._aspect.color = 'yy'
            elif self.number_of_blocks_cleared_ahead >= 3:
                self._aspect.color = 'g'
            else:
                raise ValueError(
                    'signal aspect of {}, port: {} not defined ready'.format(
                        self.sigpoint, self.port_idx))
        return self._aspect

    @property
    def next_enroute_sigpoint(self):
        ''' 
            @return:
                The next sigpoint object of this signal to which 
                its current route is leading. 
        '''
        return self.permitted_track.get_shooting_point(self.sigpoint) \
            if self.permitted_track else None

    @property
    def next_enroute_signal(self):
        ''' 
            @return:
                The next Signal object of this signal to which 
                its current route is leading. 
        '''
        return self.next_enroute_sigpoint.signal_by_port[
            self.next_enroute_sigpoint_port] if self.permitted_track else None

    @property
    def next_enroute_sigpoint_port(self):
        ''' 
            @return:
                The next signal port of the sigpoint object to which 
                its current route is leading. 
        '''
        return self.permitted_track.get_shooting_port(point=self.sigpoint) \
            if self.permitted_track else None

    @property
    def is_cleared_signal_to_exit_system(self):
        return True if (self.route and not self.permitted_track) else False

    @property
    def curr_routing_paths(self):
        '''
            @return:
                The list of current routing paths that this signal is part of.
        '''
        _track_rp = []
        if self.permitted_track:
            # Signal has to be permissive to have an active routing path
            return self.permitted_track.curr_routing_paths
        elif self.governed_track:
            _track_rp = self.governed_track.curr_routing_paths
            # Signal has to be permissive to have an active routing path
            if self.governed_track.routing[1][0] == self.sigpoint:  
                return _track_rp
        return _track_rp

    @property
    def curr_enroute_tracks(self):
        '''
            @return:
                The list of track segments that consist of the current routing path of this signal.
        '''
        _curr_enroute_tracks = []
        if self.curr_routing_paths:
            for ((p1, p1port), (p2, p2port)) in self.curr_routing_paths:
                _curr_enroute_tracks.append(self.system.get_track_by_point_port_pairs(p1, p1port, p2, p2port))
        return _curr_enroute_tracks

    @property
    def number_of_blocks_cleared_ahead(self):
        '''
            @return:
                The number of empty/unoccupied track segments that ahead of this signal, 
                along the given current routing path.
        '''
        _number = 0
        if self.curr_enroute_tracks:
            if self.governed_track:
                _governed_trk_idx = self.curr_routing_paths.index(self.governed_track.routing)
            else:
                _governed_trk_idx = 0
            _tracks_ahead = self.curr_enroute_tracks[_governed_trk_idx + 1:]
            for i in range(len(_tracks_ahead)):
                if _tracks_ahead[i]:
                    if _tracks_ahead[i].is_occupied:
                        return _number
                    elif not _tracks_ahead[i].is_occupied:
                        _number += 1
                        continue
        return _number

    @property
    def tracks_to_enter(self):
        '''
            @return:
                The number of track segments diverging from this Signal that 
                are available for a train to enter. 
        '''
        return [self.sigpoint.track_by_port[p] 
                for p in self.sigpoint.available_ports_by_port[self.port_idx]]

    @property
    def following_sigpoints(self):
        '''
            @return:
                A list of signal points this signal can potentially permit (reach) to. 
        '''
        _sigpoints = []
        for t in self.tracks_to_enter:
            for p in [t.L_point, t.R_point]:
                if p != self.sigpoint:
                    _sigpoints.append(p)
        return _sigpoints

    def reachable(self, other):
        '''
            ########################################################
            Under Devo
            ########################################################
            Determine if another signal point/Signal/Track segment is reachable from this signal.
            @return:
                True/False
        '''
        def reachable_sigpoint(p):
            path_generator = all_simple_paths(self.system.G_origin, self.sigpoint, p)
            while True:
                try:
                    if next(path_generator)[1] in self.following_sigpoints:
                        return True
                except: break
            return False
        
        def reachable_track(t):
            if self.sigpoint in (t.L_point, t.R_point):
                if self.governed_track == t: return False
                for p in self.sigpoint.available_ports_by_port[self.port_idx]:
                    if t == self.sigpoint.track_by_port[p]: return True
            # include AutoPoint's bigblock instance entirely covering the signal
            for p in (t.L_point, t.R_point):
                if reachable_sigpoint(p) is True: return True
            return False
        
        if isinstance(other, InterlockingPoint):
            return reachable_sigpoint(other)
        if isinstance(other, Signal):
            if other.sigpoint != self.sigpoint:
                return reachable_sigpoint(other.sigpoint)
            else: return True \
                if other.port_idx in \
                    self.sigpoint.available_ports_by_port[self.port_idx] \
                else False
        if isinstance(other, infrastructure.Track) \
            or isinstance(other, infrastructure.BigBlock):
            return reachable_track(other)
        return False

    
    @abstractproperty
    def bblks_to_enter(self):
        raise NotImplementedError(  "Needed to be implemented in AutoSignal or \
            HomeSignal")

    @abstractproperty
    def ctrl_pnts_to_reach(self):
        raise NotImplementedError(  "Needed to be implemented in AutoSignal or \
            HomeSignal")

    #----------------deprecated----------------#
    def update(self, observable, update_message):
        raise NotImplementedError("Old-version function to be refactored")
        if observable.type == 'bigblock':
            self.change_color_to('r', False)
        elif observable.type == 'track':
            self.change_color_to('r', False)
        elif observable.type == 'home' and observable.port_idx != self.port_idx:
            if update_message.color != 'r':
                self.change_color_to('r', False)
        else: pass

    def change_color_to(self, color, isNotified=True):
        raise NotImplementedError("Old-version function to be refactored")
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)

class AutoSignal(Signal):
    '''
    Automatic Blocking Signal object, inherited from Signal.
    Serve as the intermediate signals within a BigBlock that governs individual track segments. 
    Used for single directional traffic control only. 
    Not used for granting movement authorities. 
    '''
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__(port_idx, sigpoint, MP)
        self.type = 'auto'

        self._bblks_to_enter = None
        self._ctrl_pnts_to_reach = None
    
    def __repr__(self):
        return 'AutoSig port:{} of {}'.format(
            str(self.port_idx).rjust(2, ' '), 
            self.sigpoint)

    @property
    def bblks_to_enter(self):
        if self._bblks_to_enter is None:
            self._bblks_to_enter = [self.sigpoint.bigblock]
        return self._bblks_to_enter

    @property
    def ctrl_pnts_to_reach(self):
        if self._ctrl_pnts_to_reach is None:    
            if self.downwards:
                self._ctrl_pnts_to_reach = [self.sigpoint.bigblock.R_point]
            elif self.upwards:
                self._ctrl_pnts_to_reach = [self.sigpoint.bigblock.L_point]
            else:
                raise Exception("Cannot specify the signal milepost direction: \n\t{}".format(self.__repr__))
        return self._ctrl_pnts_to_reach

class HomeSignal(Signal):
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__(port_idx, sigpoint, MP)
        self.sigpoint = None
        self.type = 'home'
        
        self._bblks_to_enter = None
        self._ctrl_pnts_to_reach = None
        self._governed_bigblock = None

    def __repr__(self):
        return 'HomeSig port:{} of {}'.format(
            str(self.port_idx).rjust(2, ' '), 
            self.sigpoint,)

    @property
    def bblks_to_enter(self): 
        if self._bblks_to_enter is None:
            self._bblks_to_enter = [self.sigpoint.bigblock_by_port[p] for p in self.sigpoint.available_ports_by_port[self.port_idx]]
        return self._bblks_to_enter

    @property
    def ctrl_pnts_to_reach(self): 
        if self._ctrl_pnts_to_reach is None:
            self._ctrl_pnts_to_reach = []
            for bblk in self.bblks_to_enter:
                for p in [bblk.L_point, bblk.R_point]:
                    if p != self.sigpoint:
                        self._ctrl_pnts_to_reach.append(p)
        return self._ctrl_pnts_to_reach

    @property
    def governed_bigblock(self): 
        if self._governed_bigblock is None:
            self._governed_bigblock = self.sigpoint.bigblock_by_port.get(self.port_idx)
        return self._governed_bigblock 


class InterlockingPoint(Observable, Observer):
    '''
    Base Class, a.k.a SignalPoint/Sigpoint
    ''' 

    def __init__(self, system, idx, MP=None):
        super().__init__()
        self.system = system
        self.MP = MP
        self.idx = idx
        self.ports = []

        self._non_mutex_routes_by_route = None
        self._mutex_routes_by_route = None
        self.banned_ports_by_port = defaultdict(list)

        self.neighbor_nodes = []
        self.track_by_port = {}

        self._current_routes = []
        self._curr_train_with_route = {}

    @abstractproperty
    def available_ports_by_port(self): pass

    @abstractproperty
    def all_valid_routes(self): pass

    @abstractproperty
    def current_routes(self): pass

    @abstractproperty
    def non_mutex_routes_by_route(self): pass

    @property
    def mutex_routes_by_route(self):
        if self._mutex_routes_by_route is None:
            self._mutex_routes_by_route = defaultdict(list)
            for valid_route in self.all_valid_routes:
                _all_valid_routes = self.all_valid_routes.copy()
                _all_valid_routes.remove(valid_route)
                self._mutex_routes_by_route[valid_route].extend(_all_valid_routes)
            for route, non_mutex_route_list in self.non_mutex_routes_by_route.items():
                if non_mutex_route_list in self._mutex_routes_by_route[route]:
                    self._mutex_routes_by_route[route].remove(non_mutex_route_list)
        return self._mutex_routes_by_route

    @property
    def current_route_by_port(self):
        _current_route_by_port = {}
        for r in self.current_routes:
            _current_route_by_port[r[0]] = r
        return _current_route_by_port

    @property
    def curr_train_with_route(self):
        return self._curr_train_with_route

    @property
    def current_invalid_routes(self):
        _current_invalid_routes = []
        # collect all banned routes in a permutation list of 2-element tuples
        for p, bplist in self.banned_ports_by_port.items():
            for bp in bplist:
                if (p, bp) not in _current_invalid_routes:
                    _current_invalid_routes.append((p, bp))
                if (bp, p) not in _current_invalid_routes:
                    _current_invalid_routes.append((bp, p))
        # collect all mutex routes according to currently openned routes
        for r in self.current_routes:
            for vr in self.all_valid_routes:
                if vr not in self.non_mutex_routes_by_route[r] \
                    and vr not in _current_invalid_routes:
                    _current_invalid_routes.append(vr)
        # collect all routes currently under trains
        for r in self.locked_routes_due_to_train:
            if r not in _current_invalid_routes:
                _current_invalid_routes.append(r)
        return _current_invalid_routes

    @property
    def locked_routes_due_to_train(self):
        _locked_routes = []
        for _, r in self.curr_train_with_route.items():
            _locked_routes.append(r)
            _locked_routes.extend(self.mutex_routes_by_route.get(r))
        return _locked_routes

    @abstractproperty
    def banned_paths(self):
        raise NotImplementedError("Needed to be implemented in AutoPoint or CtrlPoint")


class AutoPoint(InterlockingPoint):
    def __init__(self, system, idx, MP=None):
        super().__init__(system, idx, MP)
        self.type = 'at'
        self.ports = [0, 1]
        
        self._non_mutex_routes_by_route = {}
        self.banned_ports_by_port = {0: [0], 1: [1]}
        # build up signals
        self.signal_by_port = { 0: AutoSignal(0, self, MP=self.MP),
                                1: AutoSignal(1, self, MP=self.MP)}
        # register the AutoPoint's ownership over the signals
        for _, sig in self.signal_by_port.items():
            sig.sigpoint = self
            sig.system = self.system

    def __repr__(self):
        return 'AutoPnt{}'.format(
            str(self.idx).rjust(2, ' '),)

    @property
    def bigblock(self):
        return [t.bigblock for _,t in self.track_by_port.items()][0]

    @property
    def all_valid_routes(self): return [(0, 1), (1, 0)]

    @property
    def non_mutex_routes_by_route(self): return self._non_mutex_routes_by_route

    @property
    def available_ports_by_port(self): return {0: [1], 1: [0]}  # define legal routes

    @property
    def current_routes(self):
        for p, t in self.track_by_port.items():
            # only AutoPoints can assign current routes like this because
            # AutoPoints have only 0, 1 as their ports
            if t.routing:
                if p == 0 and p == t.routing[1][1]:
                    self._current_routes = [(0, 1)]
                elif p == 0 and p == t.routing[0][1]:
                    self._current_routes = [(1, 0)]
        return self._current_routes

    @property
    def banned_paths(self): return []

    def opposite_port(self, port):
        '''
            Return the signal port on the other side of the given port of an 
            AutoSignal. Method restricted to AutoSignal instances
        '''
        for p in self.ports:
            if p != port:
                return p

class CtrlPoint(InterlockingPoint):
    def __init__(self,
                 system,
                 idx,
                 ports,
                 MP=None,
                 banned_ports_by_port=defaultdict(list),
                 non_mutex_routes_by_route=defaultdict(list)):
        super().__init__(system, idx, MP)
        self.type = 'cp'
        self.ports = ports
        self.banned_ports_by_port = banned_ports_by_port
        self._non_mutex_routes_by_route = non_mutex_routes_by_route
        self._current_routes = []
        self.bigblock_by_port = {}
        # available options for routes, dict[port] = list(options)
        self._available_ports_by_port = None
        

        self.signal_by_port = {}  # build up signals
        for i in self.ports:
            self.signal_by_port[i] = HomeSignal(i, self, MP)
        
        for _, sig in self.signal_by_port.items(
        ):  # add the ownership of signals
            sig.sigpoint = self
            sig.system = self.system

    def __repr__(self):
        return 'CtrlPnt{}'.format(
            str(self.idx).rjust(2, ' '),)

    @property
    def vertex(self):
        for i in self.ports:
            if not self.track_by_port.get(i):
                return True
        return False
    
    @property
    def non_mutex_routes_by_route(self): return self._non_mutex_routes_by_route
    
    @property
    def available_ports_by_port(self): 
        if self._available_ports_by_port is None:
            self._available_ports_by_port = defaultdict(list)
            for i in self.ports:
                for j in self.ports:
                    if j not in self.banned_ports_by_port.get(i, []):
                        self._available_ports_by_port[i].append(j)
        return self._available_ports_by_port  # define legal routes

    @property
    def all_valid_routes(self):
        # available options for routes, list of routes
        _all_valid_routes = []
        for p, plist in self.available_ports_by_port.items():
            for rp in plist:
                if (p, rp) not in _all_valid_routes:
                    _all_valid_routes.append((p, rp))
                if (rp, p) not in _all_valid_routes:
                    _all_valid_routes.append((rp, p))
        return _all_valid_routes

    @property
    def current_routes(self):
        for r1, r2 in permutations(self._current_routes, 2):
            assert r1 not in self.mutex_routes_by_route[r2]
            assert r2 not in self.mutex_routes_by_route[r1]
            assert r1[1] not in self.banned_ports_by_port[r1[0]]
            assert r2[1] not in self.banned_ports_by_port[r2[0]]
        return self._current_routes

    @current_routes.setter
    def current_routes(self, new_route_list):
        assert isinstance(new_route_list, list)
        for i in new_route_list:
            assert i in self.all_valid_routes
        self._current_routes = new_route_list

    @property
    def banned_paths(self):
        def collect_banned_paths(skeleton=False):
            _banned_collection = []
            for p in self.ports:
                if not self.banned_ports_by_port.get(p): continue
                for bp in self.banned_ports_by_port[p]:
                    if skeleton == False:
                        one_end = \
                        self.track_by_port[p].get_shooting_point(point=self) \
                        if self.track_by_port.get(p) else None
                        the_other_end = \
                        self.track_by_port[bp].get_shooting_point(point=self) \
                        if self.track_by_port.get(bp) else None
                    if skeleton == True:
                        one_end = \
                        self.bigblock_by_port[p].get_shooting_point(point=self) \
                        if self.bigblock_by_port.get(p) else None
                        the_other_end = \
                        self.bigblock_by_port[bp].get_shooting_point(point=self) \
                        if self.bigblock_by_port.get(bp) else None
                    if (one_end, self, the_other_end) not in _banned_collection:
                        _banned_collection.append((one_end,self,the_other_end))
                    if (the_other_end, self, one_end) not in _banned_collection:
                        _banned_collection.append((the_other_end,self,one_end))
            return _banned_collection
        _banned_path = []
        _banned_path.extend(collect_banned_paths(skeleton=False))
        _banned_path.extend(collect_banned_paths(skeleton=True))
        return _banned_path
    
    def open_route(self, route):
        if route not in self.current_routes:
            # if not in all_valid routes, the route to open is banned
            if route not in self.all_valid_routes:
                raise Exception(
                    'illegal route for {}: banned/non-existing routes'
                    .format(self))
            elif route in self.all_valid_routes:
                # in all_valid_routes: the route to open is not banned;
                # the route-to-open is still possible to conflict with 
                # existing routes
                if route not in self.current_invalid_routes:
                    self.current_routes.append(route)
                    self.set_bigblock_routing_by_CtrlPoint_route(route)
                    print('\troute {} of {} is opened'.format(route, self))
                else:
                    # try to close conflicting routes if possible
                    conflict_routes_of_route_to_open = []
                    for cr in self.current_routes:
                        if route not in self.non_mutex_routes_by_route[cr]:
                            conflict_routes_of_route_to_open.append(cr)
                    try:
                        for cr in conflict_routes_of_route_to_open:
                            self.close_route(cr)
                        self.current_routes.append(route)
                        self.set_bigblock_routing_by_CtrlPoint_route(route)
                        print('\troute {} of {} is opened'.format(route, self))
                    except:
                        print('\troute {} of {} failed to open because \
                                conflicting routes are protected')
                    finally:
                        pass
                # CtrlPoint port traffic routing: route[0] -> route[1]
                # BigBlock routing:
                #   (somewhere, someport) -> (self, route[0]) and
                #   (self, route[1]) to (somewhere, someport)

    def close_route(self, route=None):
        def close_single_route(route):
            assert route in self.current_routes
            _impacted_bblk = self.bigblock_by_port.get(route[0])
            _impacted_trns = [] if not _impacted_bblk \
                else [  t for t in _impacted_bblk.trains
                        if t not in self.curr_train_with_route]
            if not _impacted_trns or \
                all([t.curr_route_cancelable for t in _impacted_trns]):
                self.current_routes.remove(route)
                if self.bigblock_by_port.get(route[0]):
                    if not self.bigblock_by_port.get(route[0]).trains:
                        self.cancel_bigblock_routing_by_port(route[0])
                print('\troute {} of {} is closed'.format(route, self))
            else:
                raise Exception('\troute {} of {} protected: failed to close'.
                                format(route, self))
        if route:
            close_single_route(route)
        else:
            for r in self.current_routes:
                close_single_route(r)

    def find_route_for_port(self, port, dest_pointport=None):
        def candidate_ports(port, dest_pointport=None):
            if not dest_pointport:
                return [i for i in self.available_ports_by_port[port]]
            if dest_pointport:
                all_routes = self.system.dispatcher.all_routes_generator(self, 
                                    port, dest_pointport[0], dest_pointport[1])
                _candi = []
                for r in all_routes:
                    if set(_candi) == set(self.available_ports_by_port[port]):
                        return _candi
                    if r[1][0][1] not in _candi:
                        _candi.append(r[1][0][1])
                return _candi
        _candidate_ports = candidate_ports(port, dest_pointport)
        trns = [len(self.bigblock_by_port[p].trains) 
                if self.bigblock_by_port.get(p) else 0 
                for p in _candidate_ports]
        final_selection = [p for p in _candidate_ports]
        for p in _candidate_ports:
            _candi_bblk = self.bigblock_by_port.get(p)
            _candi_track = self.track_by_port.get(p)
            if not _candi_bblk or not _candi_track:
                continue
            elif not _candi_bblk.routing:
                continue
            elif _candi_bblk.routing != ((self, p), (_candi_bblk.get_shooting_point(
                    point=self), _candi_bblk.get_shooting_port(port=p))):
                if _candi_bblk.trains:
                    final_selection.remove(p)
                    continue
            elif _candi_bblk.routing == ((self, p), (_candi_bblk.get_shooting_point(
                    point=self), _candi_bblk.get_shooting_port(port=p))):
                if len(_candi_bblk.trains) != min(trns):
                    final_selection.remove(p)
                    continue
        
        if not final_selection: return None
        else:
            for p in final_selection:
                if not self.bigblock_by_port.get(p): return (port, p)
                if len(self.bigblock_by_port[p].trains) == min(trns): 
                    return (port, p)
            return (port, final_selection[0])

    def set_bigblock_routing_by_CtrlPoint_route(self, route):
        assert route
        (x, y) = route
        _in_port, _in_bblk = x, self.bigblock_by_port.get(x)
        _out_port, _out_bblk = y, self.bigblock_by_port.get(y)
        if _in_bblk and _out_bblk:
            _in_bblk.routing = ((_in_bblk.get_shooting_point(point=self),
                                 _in_bblk.get_shooting_port(point=self)), (self, x))
            _out_bblk.routing = ((self, y),
                                 (_out_bblk.get_shooting_point(point=self),
                                  _out_bblk.get_shooting_port(point=self)))

        elif (not _in_bblk) and _out_bblk:
            _out_bblk.routing = ((self, y),
                                 (_out_bblk.get_shooting_point(point=self),
                                  _out_bblk.get_shooting_port(point=self)))
        elif _in_bblk and (not _out_bblk):
            _in_bblk.routing = ((_in_bblk.get_shooting_point(point=self),
                                 _in_bblk.get_shooting_port(point=self)), (self, x))

    def cancel_bigblock_routing_by_port(self, port):
        assert port in self.ports
        _port, _bblk = port, self.bigblock_by_port.get(port)
        if _bblk:
            _bblk.routing = None

    def opposite_port(self, port):
        assert port in self.ports
        assert len(self.ports) == 2
        for p in self.ports:
            if p != port:
                return p


if __name__ == '__main__':
    pass