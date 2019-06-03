from signal_light import AutoSignal, HomeSignal
from signal_light import Observable

class Track(Observable):
    def __init__(self, length, allow_sp, L_point, R_point):
        super.__init__()
        self.type = 'track'
        self.length = length
        self.entry_signal_L = AutoSignal(facing_direction='left') if L_point.type == 'at' else HomeSignal(facing_direction='left')
        self.entry_signal_R = AutoSignal(facing_direction='right') if R_point.type == 'at' else HomeSignal(facing_direction='right')
        self.train = None
        self.is_Occupied = False
        self.allow_sp = allow_sp
        self.add_observer(self.entry_signal_L)
        self.add_observer(self.entry_signal_R)

    def let_in(self, train):
        assert self.is_Occupied == False
        self.train = train
        self.is_Occupied = True
        self.listener_updates()

    def let_out(self):
        assert self.is_Occupied == True
        self.train = None
        self.is_Occupied = False