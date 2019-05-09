from signal import Signal

class Track:
    def __init__(self, length, allow_sp):
        self.length = length
        self.left_signal = Signal(allow_sp)
        self.right_signal = Signal(allow_sp)
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