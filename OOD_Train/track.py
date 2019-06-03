from signal_light import AutoSignal, HomeSignal
from signal_light import Observable

class Track(Observable):
    def __init__(self, length, allow_sp, L_point, R_point):
        super.__init__()
        self.type = 'track'
        self.length = length
        self.entry_port_L = L_point.R_out_port
        self.entry_port_R = R_point.L_out_port
        self.train = None
        self.is_Occupied = False
        self.allow_sp = allow_sp
        self.add_observer(L_point)
        self.add_observer(R_point)

    def let_in(self, train):
        assert self.is_Occupied == False
        self.train = train
        self.is_Occupied = True
        self.listener_updates()

    def let_out(self):
        assert self.is_Occupied == True
        self.train = None
        self.is_Occupied = False