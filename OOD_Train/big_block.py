from block import Block
from signal_light import Observable, Observer
from track import Track

class BigBlock(Track):
    # 当前写的方法是针对单track的连续blk形成的BigBlock，后续需要将此类进行改变，
    # 将其改成能够容纳多track的block
    def __init__(self, L_cp, L_cp_port, R_cp, R_cp_port, sgl_blk_num=None):
        super().__init__(L_cp, L_cp_port, R_cp, R_cp_port)
        self.type = 'bigblock'
        self.direction = 'neutral'
        self.blocks = []
        # 将每个block加入到bigblock中的列表里，并且添加block为bigblock的观察者
        # 目前block的长度写死了，固定为10，后期可以改为参数
        for i in range(sgl_blk_num):
            self.blocks.append(Block(index=i, length=10))
            self.add_observer(self.blocks[i].tracks[0].entry_signal_L)
            self.add_observer(self.blocks[i].tracks[0].entry_signal_R)
        
        # 去掉bigblock的最左和最右的两盏信号灯，这两盏灯存在于cp中的特殊灯。
        self.blocks[0].tracks[0].entry_signal_L = None
        self.blocks[-1].tracks[0].entry_signal_R = None

        # bigblock中的邻居信号灯进行订阅
        # 未对站界block(firt and last)及其信号进行操作      
        for i in range(1, len(sgl_blk_num) - 1):    # excluding the first and last block
            # 朝向左侧的临近灯的订阅关系建立
            current_R_entry_signal = self.blocks[i].tracks[0].entry_signal_R
            successive_R_entry_signal = self.blocks[i - 1].tracks.entry_signal_R
            successive_R_entry_signal.add_observer(current_R_entry_signal)

            # 朝向右侧的临近灯的订阅关系建立
            current_L_entry_signal = self.blocks[i].tracks[0].entry_signal_L
            successive_L_entry_signal = self.blocks[i + 1].tracks[0].entry_signal_L
            successive_L_entry_signal.add_observer(current_L_entry_signal)
    
    # 下面的还没写好，具体如何操作更新和发报问题。
    def update(self, Observable, obj):
        if Observable.type == 'cp':
            self.direction = Observable.direction
            self.listener_updates(self)