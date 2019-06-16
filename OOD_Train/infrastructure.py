from signaling import AutoSignal, HomeSignal, AutoPoint, ControlPoint
from observe import Observable, Observer

import networkx as nx

class Track(Observable):
    def __init__(self, L_point, L_point_port, R_point, R_point_port, edge_key=0, length=5, allow_sp=30):    # 30 as mph
        super().__init__()
        self._train = []
        self._traffic_direction = None
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
    def traffic_direction(self):
        return self._traffic_direction

    @traffic_direction.setter
    def traffic_direction(self, new_direction):
        if new_direction:
            for (p, pport) in new_direction:
                assert p in [self.L_point, self.R_point]
                assert pport in [self.L_point_port, self.R_point_port]
            self._traffic_direction = new_direction
        else:
            self._traffic_direction = None
        

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
    
class BigBlock(Track):
    def __init__(self, L_cp, L_cp_port, R_cp, R_cp_port, edge_key=0, length=None, raw_graph=None, cp_graph=None):
        super().__init__(L_cp, L_cp_port, R_cp, R_cp_port, edge_key, length)
        assert isinstance(raw_graph, nx.MultiGraph)
        assert isinstance(cp_graph, nx.MultiGraph)
        self.type = 'bigblock'
        self._traffic_direction = None
        self.tracks = []
        self.port_by_sigpoint = {L_cp:L_cp_port, R_cp:R_cp_port}   
        self.length = self.R_point.MP - self.L_point.MP 
        self.MP = (self.L_point.MP, self.R_point.MP)
    
        self.add_observer(L_cp)
        self.add_observer(R_cp)

    def __repr__(self):
        return 'BigBlock MP: {} to MP: {} idx: {}'.format(self.L_point.MP, self.R_point.MP, self.edge_key)
    
    @property
    def traffic_direction(self):
        return self._traffic_direction
    
    @traffic_direction.setter
    def traffic_direction(self, new_direction):
        if isinstance(new_direction, tuple):
            assert len(new_direction) == 2
            self._traffic_direction = new_direction
            (start_point, start_port) = new_direction[0]
            for i in range(len(self.tracks)-1):
                (next_point, next_port) = (self.tracks[i].L_point, self.tracks[i].L_point_port) if start_point == self.tracks[i].R_point else (self.tracks[i].R_point, self.tracks[i].R_point_port)
                self.tracks[i].traffic_direction = ((start_point, start_port), (next_point, next_port))
                start_point, start_port = next_point, self.tracks[i+1].port_by_sigpoint[next_point]
            self.tracks[-1].traffic_direction = ((start_point, start_port), new_direction[1])
        else: 
            self._traffic_direction = None
            for t in self.tracks:
                t.traffic_direction = None

class Block(Observable):
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