from train import Train
from block import Block
from system import System

sys = System([20] * 10)
i = 0
while sys.refresh_time < 200000:
    i += 1
    # print(i)
    sys.refresh()

print(sys.train_num)
for t in sys.trains:
    t.print_blk_time()
    print('pos: ' + str(t.pos))