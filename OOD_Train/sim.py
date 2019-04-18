from block import Block
from system import System
from train import Train
import matplotlib.pyplot as plt
import time
import numpy as np

sys_init_time = '2018-01-01 00:00:00'
numerical_init_time = time.mktime(time.strptime('2018-01-01 00:00:00', "%Y-%m-%d %H:%M:%S"))
sys = System(sys_init_time, [5] * 10)
i = 0
while sys.sys_time - numerical_init_time  < 10000:
    i += 1
    # print(i)
    # print("Train number: {}".format(sys.train_num))
    sys.refresh()

for t in sys.trains:
    t.print_blk_time()
