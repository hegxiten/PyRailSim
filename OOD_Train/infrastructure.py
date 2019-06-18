from signaling import AutoSignal, HomeSignal, AutoPoint, ControlPoint
from observe import Observable, Observer

import networkx as nx

class Track(Observable):
    def __init__(self, L_point, L_point_port, R_point, R_point_port, edge_key=0, length=5, allow_sp=30):    # 30 as mph
        super().__init__()
        self._train = []
        self._routing = None
        self.type = 'track'
        self.length = length
        self.L_point, self.R_point = L_point, R_point
        self.L_point_port, self.R_point_port = L_point_port, R_point_port
        self.edge_key = edge_key
        self.allow_sp = allow_sp
        self.port_by_sigpoint = {L_point:L_point_port, R_point:R_point_port}   
        self.add_observer(L_point)
        self.add_observer(R_point)

        self.R_point.MP = self.L_point.MP + self.length
        self.MP = (self.L_point.MP, self.R_point.MP)
        self.__bigblock = None
    
    def __repr__(self):
        return 'Track MP: {} to MP: {} idx: {}'.format(self.L_point.MP, self.R_point.MP, self.edge_key)

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
        assert isinstance(bblk,BigBlock)
        self.__bigblock = bblk

    @property
    def routing(self):
        return self._routing

    @routing.setter
    def routing(self, new_routing):
        if new_routing:
            for (p, pport) in new_routing:
                assert p in [self.L_point, self.R_point]
                assert pport in [self.L_point_port, self.R_point_port]
            self._routing = new_routing
        else:
            self._routing = None
            
class BigBlock(Track):
    def __init__(self, L_cp, L_cp_port, R_cp, R_cp_port, edge_key=0, length=None, raw_graph=None, cp_graph=None):
        super().__init__(L_cp, L_cp_port, R_cp, R_cp_port, edge_key, length)
        assert isinstance(raw_graph, nx.MultiGraph)
        assert isinstance(cp_graph, nx.MultiGraph)
        self.type = 'bigblock'
        self._routing = None
        self.tracks = []
        self.port_by_sigpoint = {L_cp:L_cp_port, R_cp:R_cp_port}   
        self.length = self.R_point.MP - self.L_point.MP 
        self.MP = (self.L_point.MP, self.R_point.MP)
    
        self.add_observer(L_cp)
        self.add_observer(R_cp)

    def __repr__(self):
        return 'BigBlock MP: {} to MP: {} idx: {}'.format(self.L_point.MP, self.R_point.MP, self.edge_key)
    
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
            self._routing = new_routing
            self.set_routing_for_tracks()
        else: 
            self._routing = None
            for t in self.tracks:
                t.routing = None
    
    def set_routing_for_tracks(self):
        (start_point, start_port) = self.routing[0]
        reverse = True if start_point in self.tracks[-1].port_by_sigpoint.keys() else False
        if not reverse:
            for i in range(len(self.tracks)-1):
                (next_point, next_port) = (self.tracks[i].L_point, self.tracks[i].L_point_port) if start_point == self.tracks[i].R_point else (self.tracks[i].R_point, self.tracks[i].R_point_port)
                self.tracks[i].routing = ((start_point, start_port), (next_point, next_port))
                start_point, start_port = next_point, self.tracks[i+1].port_by_sigpoint[next_point]
            self.tracks[-1].routing = ((start_point, start_port), self.routing[1])
        else:
            for i in range(len(self.tracks)-1, 0, -1):
                (next_point, next_port) = (self.tracks[i].L_point, self.tracks[i].L_point_port) if start_point == self.tracks[i].R_point else (self.tracks[i].R_point, self.tracks[i].R_point_port)
                self.tracks[i].routing = ((start_point, start_port), (next_point, next_port))
                start_point, start_port = next_point, self.tracks[i-1].port_by_sigpoint[next_point]
            self.tracks[0].routing = ((start_point, start_port), self.routing[1])

class Block(Observable):
    #old Block
    def __init__(self, index, length, max_sp=0.02, track_number=1):
        self.index = index
        self.length = length
        self.max_sp = max_sp
        # There is track_number tracks in this block.
        self.track_number = track_number
        self.tracks = []
        if self.track_number > 1:
            for i in range(self.track_number):
                self.tracks.append(Track(self.length, self.max_sp, 'home'))
        else:
            self.tracks.append(Track(self.length, self.max_sp, 'abs'))

    def has_train(self):
        pass
        return
        for tr in self.tracks:
            if tr.is_Occupied:
                return True
        return False

    def is_Occupied(self):
        pass
        return
        for tk in self.tracks:
            if not tk.is_Occupied:
                return True
        return False

    def find_available_track(self):
        pass
        return
        assert self.is_Occupied()
        for idx, tk in enumerate(self.tracks):
            if not tk.is_Occupied:
                return idx

    def occupied_track(self, idx, train):
        pass
        return
        train.curr_blk = self.index
        train.curr_track = idx
        self.tracks[idx].enter(train)
    
    def free_track(self, idx):
        pass
        return
        train = self.tracks[idx].train
        train.curr_blk = -1
        train.curr_track = 0
        self.tracks[idx].leave()

class OldTrack(object):
    
    def has_train(self):
        return True if len(self.train) != 0 else False

    def find_available_track(self):
        pass
        return
        assert self.is_Occupied()
        for idx, tk in enumerate(self.tracks):
            if not tk.is_Occupied:
                return idx

    def occupied_track(self, idx, train):
        pass
        return
        train.curr_blk = self.index
        train.curr_track = idx
        self.tracks[idx].enter(train)
    
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
        assert self.is_Occupied == False
        self._train.append(train)
        self.is_Occupied = True
        self.listener_updates()

    def let_out(self, train):
        pass
        return
        assert self.is_Occupied == True
        self._train.remove(train)
        self.is_Occupied = False
        self.listener_updates()