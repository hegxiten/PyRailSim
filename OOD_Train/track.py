from signal_light import AutoSignal, HomeSignal
from signal_light import Observable

class Track(Observable):
    def __init__(self, length, allow_sp, signalType):
        super.__init__()
        self.type = 'track'
        self.length = length
        self.left_signal = AutoSignal('right') if signalType == 'abs' else HomeSignal('right')
        self.right_signal = AutoSignal('left') if signalType == 'abs' else HomeSignal('left')
        self.train = None
        self.is_Occupied = False
        self.allow_sp = allow_sp

    def enter(self, train):
        assert self.is_Occupied == False
        self.train = train
        self.is_Occupied = True
        self.listener_updates()

    def leave(self):
        assert self.is_Occupied == True
        self.train = None
        self.is_Occupied = False