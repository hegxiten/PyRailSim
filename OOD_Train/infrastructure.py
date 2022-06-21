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
import sys
sys.path.append(
    'D:\\Users\\Hegxiten\\workspace\\Rutgers_Railway_security_research\\OOD_Train'
)

from observe import Observable, Observer



class Track(Observable):
    @staticmethod
    def sign_routing(rp_seg):
        '''
            :rp_seg: 2-element-tuple: ((Point, Port),(Point, Port)) 
                Routing path segment of a train, describing its direction.
            @return: 
                The sign (+1/-1) of traffic when input with a legal routing
                path segment of a track/bigblock (describing traffic direction)'''
        if not rp_seg:  # no routing information (dormant track/bigblock)
            return 0
        elif rp_seg[0][0] and rp_seg[1][0]:
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP > \
                    rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP < \
                    rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return -1
            else:
                raise ValueError('Undefined MP direction')
        
        # initiating
        elif not rp_seg[0][0]:
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == \
                    min(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(
                                                            rp_seg[1][1])].MP):
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == \
                    max(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(
                                                            rp_seg[1][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')
        # terminating
        elif not rp_seg[1][0]:
            if rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == \
                    max(rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(
                                                            rp_seg[0][1])].MP):
                return 1
            elif rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == \
                    min(rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(
                                                            rp_seg[0][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')

    def __init__(self,
                 system,
                 L_point,
                 L_point_port,
                 R_point,
                 R_point_port,
                 edge_key=0,
                 allow_spd=65,  # speed as mph
                 yard=None,
                 **kwargs):  
        super().__init__()
        self._trains = []
        self._routing = None
        self.type = 'track'
        self.edge_key = edge_key
        self.allow_spd = allow_spd / 3600
        
        self.L_point, self.R_point = L_point, R_point
        self.L_point_port, self.R_point_port = L_point_port, R_point_port
        self.port_by_sigpoint = {L_point: L_point_port, R_point: R_point_port}
        self.add_observer(L_point)
        self.add_observer(R_point)

        self.system = system
        self.yard = yard
        if self.yard:
            if self not in self.yard.tracks:
                self.yard.tracks.append(self)
        lambda_defaultmainline = lambda l_port, r_port: True if l_port == 1 and r_port == 0 else False
        self.mainline = lambda_defaultmainline(self.L_point_port, self.R_point_port) \
            if kwargs.get('mainline') is None \
            else kwargs.get('mainline')
        
        self.mainline_weight = float('inf') if self.mainline == False else 0
        self.tracks = []
        self.__bigblock = None
        self.__curr_routing_path = None

    def __repr__(self):
        return 'Track <MP:{0}~{1}> <{2} port:{3}~{4} port:{5}> key:{6}'\
            .format(str("%.1f" % round(self.MP[0], 1)).rjust(5, ' '), 
                    str("%.1f" % round(self.MP[1], 1)).ljust(5, ' '), 
                    self.L_point,
                    str(self.L_point_port).rjust(2, ' '),
                    self.R_point, 
                    str(self.R_point_port).rjust(2, ' '),
                    str(self.edge_key).rjust(2, ' '),)

    @property
    def MP(self):
        return (self.L_point.signal_by_port[self.L_point_port].MP,
                self.R_point.signal_by_port[self.R_point_port].MP)

    @property
    def length(self):
        return abs(self.MP[1] - self.MP[0])

    @property
    def trains(self):
        return self._trains

    @property
    def is_occupied(self):
        return False if not self.trains else True

    @property
    def bigblock(self):
        return self.__bigblock

    @bigblock.setter
    def bigblock(self, bblk):
        assert isinstance(bblk, BigBlock)
        self.__bigblock = bblk

    @property
    def routing(self):
        assert self.sign_routing(self._routing) == self.bigblock.sign_routing(
            self.bigblock.routing)
        return self._routing

    @routing.setter
    def routing(self, new_routing):
        '''
            WARNING: 
                Setting a routing property directly from a track in normal 
                dispatching mode is NOT RECOMMENDED.
                Please set routing property by track's parental bigblock instance.'''
        if new_routing:
            for (p, pport) in new_routing:
                assert p in [self.L_point, self.R_point]
                assert pport in [self.L_point_port, self.R_point_port]
            self._routing = new_routing
        else:
            self._routing = None

    @property
    def curr_routing_paths(self):
        for rp in self.system.curr_routing_paths:
            if self.routing in rp:
                return rp
        return []

    def __lt__(self, other):
        '''
            Implement __lt__ to sort yards based on their MilePost.
            If MilePosts are the same, compare key in Graphs.
            MP system of self and other has to be the same: same corridor.'''
        if getattr(self, 'mainline', False) is True:
            if getattr(self, 'mainline', False) is False:
                return True
        if self.MP == other.MP:
            if self.edge_key < other.edge_key:
                return True
        if self.length == other.length:
            if max(self.MP) <= min(other.MP): return True
            if min(other.MP) < max(self.MP) < max(other.MP): return True
        if self.length < other.length:
            if max(self.MP) <= min(other.MP): return True
            if min(other.MP) < max(self.MP) < max(other.MP): return True
            if min(other.MP) <= min(self.MP):
                if min(self.MP) - min(other.MP) < max(other.MP) - max(self.MP):
                    return True
        if self.length > other.length:
            if max(self.MP) <= min(other.MP): return True
            if min(other.MP) < max(self.MP) < max(other.MP): return True
            if min(self.MP) < min(other.MP):
                if min(other.MP) - min(self.MP) > max(self.MP) - max(other.MP):
                    return True

    def get_shooting_point(self, point=None, port=None, sign_MP=None):
        '''
            Example: 
                [port_0:CP_A:port_1 ----> port_0:CP_B:port_1]
            Given CP_A or port_1, 
            @return: 
                CP_B
        '''
        if point is not None:
            assert point in (self.L_point, self.R_point)
            return self.L_point if point == self.R_point else self.R_point
        if port is not None:
            assert port in (self.L_point_port, self.R_point_port)
            return self.L_point if port == self.R_point_port else self.R_point
        if sign_MP is not None:
            assert sign_MP in (-1, +1)
            return self.L_point if sign_MP == -1 else self.R_point
        return None

    def get_shooting_port(self, point=None, port=None, sign_MP=None):
        '''
            Example: 
                [port_0:CP_A:port_1 ----> port_0:CP_B:port_1]
            Given CP_A or port_1, 
            @return: 
                port_0
        '''
        if point is not None:
            assert point in (self.L_point, self.R_point)
            return self.L_point_port \
                if point == self.R_point else self.R_point_port
        if port is not None:
            assert port in (self.L_point_port, self.R_point_port)
            return self.L_point_port \
                if port == self.R_point_port else self.R_point_port
        if sign_MP is not None:
            assert sign_MP in (-1, +1)
            return self.L_point_port \
                if sign_MP == -1 else self.R_point_port
        return None


class BigBlock(Track):
    def __init__(self,
                 system,
                 L_cp,
                 L_cp_port,
                 R_cp,
                 R_cp_port,
                 edge_key=0,
                 raw_graph=None,
                 cp_graph=None):
        super().__init__(system, L_cp, L_cp_port, R_cp, R_cp_port, edge_key=edge_key)
        self.type = 'bigblock'
        self._routing = None
        self.tracks = []
        self.add_observer(L_cp)
        self.add_observer(R_cp)

    def __repr__(self):
        return 'BgBlk <MP:{0}~{1}> <{2} port:{3}~{4} port:{5}> key:{6}'\
            .format(str("%.1f" % round(self.MP[0], 1)).rjust(5, ' '), 
                    str("%.1f" % round(self.MP[1], 1)).ljust(5, ' '), 
                    self.L_point,
                    str(self.L_point_port).rjust(2, ' '),
                    self.R_point, 
                    str(self.R_point_port).rjust(2, ' '),
                    str(self.edge_key).rjust(2, ' '),)

    @property
    def trains(self):
        _trains = []
        for t in self.tracks:
            for tr in t.trains:
                if tr not in _trains:
                    _trains.append(tr)
        return _trains

    @property
    def routing(self):
        return self._routing

    @routing.setter
    def routing(self, new_routing):
        if isinstance(new_routing, tuple):
            assert len(new_routing) == 2
            if self._routing != new_routing:
                if self._routing is not None:
                    # Only if when no trains in the BigBlock, the BigBlock is OK
                    # to change to a reversed routing
                    assert not self.trains
                    _curr_shooting_cp = self._routing[1][0]
                    _curr_shooting_port = self._routing[1][1]
                    assert _curr_shooting_cp == new_routing[0][0]
                    # If the BigBlock is set with a reversed routing,
                    # close any signal routes leading into its old routing
                    # at the CtrlPoint the old bigblock routing is shooting to.
                    for r in _curr_shooting_cp.current_routes:
                        if _curr_shooting_port == r[0]:
                            _curr_shooting_cp.close_route(r)
            self._routing = new_routing
            self.set_routing_for_tracks()
        else:
            # Closing the routing by setting the property None, together with its tracks
            self._routing = None
            for t in self.tracks:
                t.routing = None

    @property
    def curr_routing_paths(self):
        for i in range(len(self.tracks) - 1):
            assert self.tracks[i].curr_routing_paths == self.tracks[i + 1].curr_routing_paths
        return self.tracks[0].curr_routing_paths

    @property
    def individual_routing_paths_list(self):
        '''
            @return:
                A list of routing objects for the individual tracks within the BigBlock 
        '''
        if self.routing:
            (start_point, start_port) = self.routing[0]
            individual_routing = [
                    getattr(self.tracks[i], 'routing')
                    for i in range(len(self.tracks))
                ]
            reverse = True \
                if start_point in (self.tracks[-1].L_point, self.tracks[-1].R_point) \
                else False
            return individual_routing if not reverse else list(reversed(individual_routing))
        return []

    def set_routing_for_tracks(self):
        '''
            If a BigBlock has routing property, this method sets the routing
            property of its tracks by the same routing information.
            If this method is called, the routing is unified among all tracks inside 
            plus their parental BigBlock.
            @return: 
                None
        '''
        assert self.routing is not None
        (start_point, start_port) = self.routing[0]
        reverse = True \
            if start_point in (self.tracks[-1].L_point, self.tracks[-1].R_point) \
            else False
        if not reverse:
            for i in range(len(self.tracks) - 1):
                (next_point, next_port) = ( self.tracks[i].L_point, 
                                            self.tracks[i].L_point_port) \
                    if start_point == self.tracks[i].R_point \
                    else (self.tracks[i].R_point, self.tracks[i].R_point_port)
                self.tracks[i].routing = ((start_point, start_port),(next_point, next_port))
                start_point, start_port = next_point, self.tracks[i + 1].port_by_sigpoint[next_point]
            self.tracks[-1].routing = ((start_point, start_port),self.routing[1])
        else:
            for i in range(len(self.tracks) - 1, 0, -1):
                (next_point, next_port) = ( self.tracks[i].L_point, 
                                            self.tracks[i].L_point_port) \
                    if start_point == self.tracks[i].R_point \
                    else (self.tracks[i].R_point, self.tracks[i].R_point_port)
                self.tracks[i].routing = ((start_point, start_port),(next_point, next_port))
                start_point, start_port = next_point, self.tracks[i - 1].port_by_sigpoint[next_point]
            self.tracks[0].routing = ((start_point, start_port),self.routing[1])


class Yard(Observable, Observer):
    __lt__ = Track.__lt__
    
    def __init__(self,sys):
        self.system = sys
        self.tracks = []

    @property
    def MP(self):
        return (min([t.MP for t in self.tracks]), max([t.MP for t in self.tracks])) \
            if self.tracks \
            else (None,None)
        
    @property
    def available_tracks(self):
        count = 0
        for trk in self.tracks:
            if not trk.trains:
                count += 1
        return count

    @property
    def all_trains(self):
        _all_trains = []
        for trn_list in [trk.trains for trk in self.tracks]:
            _all_trains.extend(trn_list)
        return _all_trains