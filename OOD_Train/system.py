from block import Block
from train import Train
import time
import numpy as np

exp_buffer, var_buffer = 10, 0.5

class System():
    def __init__(self, block_length, siding_index=[], dos_period=[-1, -1], dos_pos=-1):
        self.blocks = []
        for i in range(len(block_length)):
            if i in siding_index:
                self.blocks.append(Block(i, block_length[i], True))
            self.blocks.append(Block(i, block_length[i], False))
        self.trains = []
        self.dos_period = dos_period
        self.dos_pos = dos_pos
        self.train_num = 0
        self.block_intervals = []
        for i in range(len(block_length)):
            if i == 0:
                self.block_intervals.append([0, block_length[0]])
            else:
                left = self.block_intervals[i - 1][1]
                right = left + block_length[i]
                self.block_intervals.append([left, right])
        self.last_train_time = time.time()
        self.refresh_time = 0

    def generate_train(self):
        self.train_num += 1
        new_train = Train(self.train_num, self.block_intervals)
        self.trains.append(new_train)
        self.last_train_time = time.time()

    def refresh(self):
        headway = np.random.normal(exp_buffer, var_buffer)
        # If the time slot between now and the time of last train generation
        # is bigger than headway, it will generate a new train at start point.
        if self.train_num == 0:
            self.generate_train()

        if time.time() - self.last_train_time >= headway:
            self.generate_train()

        for t in self.trains:
            if t.curr_blk < len(self.blocks) - 1:
                next_block_has_train = self.blocks[t.curr_blk + 1].isOccupied
            else:
                next_block_has_train = False

            if self.dos_period[0] <= self.refresh_time <= self.dos_period[1]:
                t.update(next_block_has_train, self.dos_pos)
            else:
                t.update(next_block_has_train)
        self.refresh_time += 1

        