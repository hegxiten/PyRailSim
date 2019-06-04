from signal_light import AutoSignal, HomeSignal
from signal_light import Observable

class Track(Observable):
    def __init__(self, L_point, L_point_port, R_point, R_point_port, length=5, allow_sp=30):    # 30 as mph
        super.__init__()
        self.type = 'track'
        self.length = length
        self.L_point = L_point
        self.R_point = R_point
        self.entry_port_L = L_point_port
        self.entry_port_R = R_point_port
        self.train = None
        self.is_Occupied = False
        self.allow_sp = allow_sp
        self.track_ports = {self.L_point: L_point_port, self.R_point: R_point_port}
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