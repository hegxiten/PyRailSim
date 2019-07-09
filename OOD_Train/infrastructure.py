#!/usr/bin/python3
# -*- coding: utf-8 -*-
import networkx as nx
from observe import Observable, Observer
from signaling import AutoSignal, HomeSignal, AutoPoint, ControlPoint


class Track(Observable):
    @staticmethod
    def sign_routing(rp_seg):
        '''Return the sign (+/-) of traffic when input with a legal routing path segment
        of a track or bigblock (describing its current traffic direction)'''
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
        elif not rp_seg[0][0]:  # initiating
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == \
                    min(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == \
                    max(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')
        elif not rp_seg[1][0]:  # terminating
            if rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == \
                    max(rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(rp_seg[0][1])].MP):
                return 1
            elif rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == \
                    min(rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(rp_seg[0][1])].MP):
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
                 allow_sp=65):  # speed as mph
        super().__init__()
        self._train = []
        self._routing = None
        self.type = 'track'
        self.L_point, self.R_point = L_point, R_point
        self.L_point_port, self.R_point_port = L_point_port, R_point_port
        self.port_by_sigpoint = {L_point: L_point_port, R_point: R_point_port}

        self.edge_key = edge_key
        self.allow_sp = allow_sp / 3600
        self.add_observer(L_point)
        self.add_observer(R_point)

        self.system = system
        self.__bigblock = None
        self.__curr_routing_path = None

    def __repr__(self):
        return 'Track MP: {} to MP: {} idx: {}'.format(self.MP[0], self.MP[1],
                                                       self.edge_key)

    @property
    def MP(self):
        return (self.L_point.signal_by_port[self.L_point_port].MP,
                self.R_point.signal_by_port[self.R_point_port].MP)

    @property
    def length(self):
        return abs(self.MP[1] - self.MP[0])

    @property
    def train(self):
        return self._train

    @property
    def is_Occupied(self):
        return False if not self.train else True

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
        '''NOT RECOMMENDED: setting a routing property directly from a track when normal dispatching.
        It is always recommended to set routing property from its bigblock instance.
        '''
        if new_routing:
            for (p, pport) in new_routing:
                assert p in [self.L_point, self.R_point]
                assert pport in [self.L_point_port, self.R_point_port]
            self._routing = new_routing
        else:
            self._routing = None

    @property
    def curr_routing_path(self):
        for rp in self.system.curr_routing_paths:
            if self.routing in rp:
                return rp
        return None

    def shooting_point(self, point=None, port=None, sign_MP=None):
        if point is not None:
            assert point in (self.L_point, self.R_point)
            return self.L_point if point == self.R_point else self.R_point
        if port is not None:
            assert port in (self.L_point_port, self.R_point_port)
            return self.L_point if port == self.R_point_port else self.R_point
        if sign_MP is not None:
            assert sign_MP in (-1, +1)
            return self.L_point if sign_MP == -1 else self.R_point

    def shooting_port(self, point=None, port=None, sign_MP=None):
        if point is not None:
            assert point in (self.L_point, self.R_point)
            return self.L_point_port if point == self.R_point else self.R_point_port
        if port is not None:
            assert port in (self.L_point_port, self.R_point_port)
            return self.L_point_port if port == self.R_point_port else self.R_point_port
        if sign_MP is not None:
            assert sign_MP in (-1, +1)
            return self.L_point_port if sign_MP == -1 else self.R_point_port


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
        super().__init__(system, L_cp, L_cp_port, R_cp, R_cp_port, edge_key)
        assert isinstance(raw_graph, nx.MultiGraph)
        assert isinstance(cp_graph, nx.MultiGraph)
        self.type = 'bigblock'
        self._routing = None
        self.tracks = []
        self.add_observer(L_cp)
        self.add_observer(R_cp)

    def __repr__(self):
        return 'BigBlock MP: {} to MP: {} idx: {}'.format(
            self.MP[0], self.MP[1], self.edge_key)

    @property
    def train(self):
        _train = []
        for t in self.tracks:
            for tr in t.train:
                if tr not in _train:
                    _train.append(tr)
        return _train

    @property
    def routing(self):
        return self._routing

    @routing.setter
    def routing(self, new_routing):
        if isinstance(new_routing, tuple):
            assert len(new_routing) == 2
            if self._routing != new_routing:
                if self._routing:
                    # only when no trains in the bigblock, the bigblock is allowed
                    # to change to a reversed routing
                    assert not self.train
                    _curr_shooting_cp = self._routing[1][0]
                    _curr_shooting_port = self._routing[1][1]
                    assert _curr_shooting_cp == new_routing[0][0]
                    # if the bigblock is set with a reversed routing,
                    # close any signal routes leading into its old routing
                    # at the ControlPoint the old bigblock routing is shooting to.
                    for r in _curr_shooting_cp.current_routes:
                        if _curr_shooting_port == r[0]:
                            _curr_shooting_cp.close_route(r)
            self._routing = new_routing
            self.set_routing_for_tracks()
        else:
            self._routing = None
            for t in self.tracks:
                t.routing = None

    @property
    def curr_routing_path(self):
        for i in range(len(self.tracks) - 1):
            assert self.tracks[i].curr_routing_path == self.tracks[
                i + 1].curr_routing_path
        return self.tracks[0].curr_routing_path

    @property
    def self_routing_path(self):
        if self.routing:
            (start_point, _) = self.routing[0]
            reverse = True if start_point in (
                self.tracks[-1].L_point, self.tracks[-1].R_point) else False
            if not reverse:
                return [
                    getattr(self.tracks[i], 'routing')
                    for i in range(len(self.tracks))
                ]
            else:
                return [
                    getattr(self.tracks[i], 'routing')
                    for i in range(len(self.tracks) - 1, -1, -1)
                ]
        else:
            return None

    def set_routing_for_tracks(self):
        '''
            If a BigBlock has routing property, this method sets the routing
            property of its tracks by the same routing information.
            If this method is called, the routing is ensured consistant among
            tracks inside and their shared BigBlock.
            @return: None'''
        (start_point, start_port) = self.routing[0]
        reverse = True if start_point in (self.tracks[-1].L_point,
                                          self.tracks[-1].R_point) else False
        if not reverse:
            for i in range(len(self.tracks) - 1):
                (next_point, next_port) = (self.tracks[i].L_point, self.tracks[i].L_point_port) \
                    if start_point == self.tracks[i].R_point \
                    else (self.tracks[i].R_point, self.tracks[i].R_point_port)
                self.tracks[i].routing = ((start_point, start_port),
                                          (next_point, next_port))
                start_point, start_port = next_point, self.tracks[
                    i + 1].port_by_sigpoint[next_point]
            self.tracks[-1].routing = ((start_point, start_port),
                                       self.routing[1])
        else:
            for i in range(len(self.tracks) - 1, 0, -1):
                (next_point, next_port) = (self.tracks[i].L_point, self.tracks[i].L_point_port) \
                    if start_point == self.tracks[i].R_point \
                    else (self.tracks[i].R_point, self.tracks[i].R_point_port)
                self.tracks[i].routing = ((start_point, start_port),
                                          (next_point, next_port))
                start_point, start_port = next_point, self.tracks[
                    i - 1].port_by_sigpoint[next_point]
            self.tracks[0].routing = ((start_point, start_port),
                                      self.routing[1])

    #-----------------------------#

    def find_available_track(self):
        pass
        return
        for idx, tk in enumerate(self.tracks):
            if not tk.is_Occupied:
                return idx

    def free_track(self, idx):
        pass
        return
        train = self.tracks[idx].train
        train.curr_blk = -1
        train.curr_track = 0
        self.tracks[idx].leave()

    def let_in(self, train):
        pass
        return
        assert self.is_Occupied is False
        self._train.append(train)
        self.is_Occupied = True
        self.listener_updates()

    def let_out(self, train):
        pass
        return
        assert self.is_Occupied is True
        self._train.remove(train)
        self.is_Occupied = False
        self.listener_updates()
