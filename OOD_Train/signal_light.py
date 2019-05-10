class Signal:
    def __init__(self, allow_sp):
        self.color = 'g'
        self.tgt_sp = 0
        self.allow_sp = allow_sp

    def update_signal(self, color):
        assert color in ['r', 'y', 'yy', 'g']
        if color == 'g':
            self.color = 'g'
            self.tgt_sp = self.allow_sp
        elif color == 'yy':
            self.color = 'yy'
            self.tgt_sp = self.allow_sp * 3 / 4
        elif color == 'y':
            self.color = 'y'
            self.tgt_sp = self.allow_sp / 2
        else:
            self.color = 'r'
            self.tgt_sp = 0