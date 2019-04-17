from train import Train
from block import Block
from system import System

sys = System([20] * 10)
i = 0
while sys.refresh_time < 1000:
    i += 1
    # print(i)
    # print("Train number: {}".format(sys.train_num))
    sys.refresh()

print(sys.train_num)
for t in sys.trains:
    t.print_blk_time()