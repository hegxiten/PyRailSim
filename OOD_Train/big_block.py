from block import Block
from signal_light import Observable, Observer

class BigBlock(Observable, Observer):
    # 当前写的方法是针对单track的连续blk形成的BigBlock，后续需要将此类进行改变，
    # 将其改成能够容纳多track的block
    def __init__(self, sgl_blk_num):
        super().__init__()
        self.type = 'bigblock'
        self.direction = 'neutral'
        self.blocks = []
        # 将每个block加入到bigblock中的列表里，并且添加block为bigblock的观察者
        # 目前block的长度写死了，固定为10，后期可以改为参数
        for i in range(sgl_blk_num):
            self.blocks.append(Block(i, 10))
            self.add_observer(self.blocks[i].tracks[0].left_signal)
            self.add_observer(self.blocks[i].tracks[0].right_signal)
        
        # 去掉bigblock的最左和最右的两盏信号灯，这两盏灯存在于cp中的特殊灯。
        self.blocks[0].tracks[0].left_signal = None
        self.blocks[-1].tracks[0].right_signal = None

        # bigblock中的邻居信号灯进行订阅
        for i in range(1, len(sgl_blk_num) - 1):
            # 朝向左侧的临近灯的订阅关系建立
            next_right_signal = self.blocks[i].tracks[0].right_signal
            prev_right_signal = self.blocks[i - 1].tracks.right_signal
            next_right_signal.add_observer(prev_right_signal)
            self.blocks[i].tracks[0].add_observer(prev_right_signal)

            # 朝向右侧的临近灯的订阅关系建立
            curr_left_signal = self.blocks[i].tracks[0].left_signal
            next_left_signal = self.blocks[i + 1].tracks[0].left_signal
            curr_left_signal.add_observer(next_left_signal)
            self.blocks[i - 1].tracks[0].add_observer(curr_left_signal)
        
    def update(self, Observable, obj):
        if Observable.type == 'cp':
            self.direction = Observable.direction
            self.listener_updates(self)