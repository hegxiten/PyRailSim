from block import Block
from train import Train

class System():
    def __init__(self, block_length, siding_index, dos_period=None, dos_pos=-1):
        self.blocks = []
        for i in range(len(block_length)):
            if i in siding_index:
                self.blocks = Block(i, block_length[i], True)
            self.blocks = Block(i, block_length[i], False)
        self.trains = []
        self.dos_period = dos_period
        self.dos_pos = dos_pos
        self.train_num = 0
        self.block_intervals = []
        for i in range(len(block_length)):
            if i == 0:
                self.block_intervals.append([0, block_length[0]])
            else:
                self.block_intervals.append([block_length[i - 1], block_length[i]])

    def generate_train(self):
        new_train = Train(self.train_num, self.block_intervals)
        self.trains.append(new_train)

    def dos_happened(self):
        pass