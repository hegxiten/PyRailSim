from signal_light import AutoSignal, HomeSignal

class Track:
    def __init__(self, length, allow_sp, signalType):
        self.length = length
        # TODO: 参数含义待定
        self.left_signal = AutoSignal('right') if signalType == 'abs' else HomeSignal('right')
        self.right_signal = AutoSignal('left') if signalType == 'abs' else HomeSignal('left')
        self.train = None
        self.is_Occupied = False
        self.allow_sp = allow_sp

    def enter(self, train):
        assert self.is_Occupied == False
        self.train = train
        self.is_Occupied = True

    def leave(self):
        assert self.is_Occupied == True
        self.train = None
        self.is_Occupied = False