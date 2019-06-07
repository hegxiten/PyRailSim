from signaling import AutoSignal, HomeSignal
from observe import Observable, Observer

class Track(Observable):
    def __init__(self, L_point, L_point_port, R_point, R_point_port, length=5, allow_sp=30):    # 30 as mph
        super().__init__()
        self.type = 'track'
        self.length = length
        self.L_point = L_point
        self.R_point = R_point
        self.entry_port_L = L_point_port
        self.entry_port_R = R_point_port
        self.train = None
        self.traffic_direction = None
        self.is_Occupied = False
        self.allow_sp = allow_sp
        self.track_ports = {}
        self.add_observer(L_point)
        self.add_observer(R_point)
        

    def let_in(self, train):
        assert self.is_Occupied == False
        self.train = train
        self.is_Occupied = True
        self.listener_updates()

    def let_out(self):
        assert self.is_Occupied == True
        self.train = None
        self.is_Occupied = False

class Block(Observable):

    def __init__(self, index, length, max_sp=0.02, track_number=1):
        self.index = index
        self.length = length
        self.max_sp = max_sp
        # There is track_number tracks in this block.
        self.track_number = track_number
        self.tracks = []
        if self.track_number > 1:
            for i in range(self.track_number):
                self.tracks.append(Track(self.length, self.max_sp, 'home'))
        else:
            self.tracks.append(Track(self.length, self.max_sp, 'abs'))

    def has_train(self):
        for tr in self.tracks:
            if tr.is_Occupied:
                return True
        return False

    def has_available_track(self):
        for tk in self.tracks:
            if not tk.is_Occupied:
                return True
        return False

    def find_available_track(self):
        assert self.has_available_track()
        for idx, tk in enumerate(self.tracks):
            if not tk.is_Occupied:
                return idx

    def occupied_track(self, idx, train):
        train.curr_blk = self.index
        train.curr_track = idx
        self.tracks[idx].enter(train)
    
    def free_track(self, idx):
        train = self.tracks[idx].train
        train.curr_blk = -1
        train.curr_track = 0
        self.tracks[idx].leave()
    
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