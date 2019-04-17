from block import Block
from train import Train
import time
import numpy as np

exp_buffer, var_buffer = 5, 0.5

class System():
    def __init__(self, block_length, siding_index, dos_period=None, dos_pos=-1):
        self.blocks = []
        self.start_time = time.time()
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
        self.last_train_time = time.time()

    def generate_train(self):
        new_train = Train(self.train_num, self.block_intervals)
        self.trains.append(new_train)

    def refresh(self):
        headway = np.random.normal(exp_buffer, var_buffer)
        # If the time slot between now and the time of last train generation
        # is bigger than headway, it will generate a new train at start point.
        if time.time() - self.last_train_time >= headway:
            self.generate_train()

        for t in self.trains:
            next_block_has_train = self.blocks[t.curr_blk + 1].isOccupied
            if self.dos_period[0] <= time.time() - self.start_time <= self.dos_period[1]:
                t.update(next_block_has_train, self.dos_pos)

        