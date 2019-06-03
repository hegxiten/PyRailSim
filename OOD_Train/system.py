from datetime import datetime, timedelta
from block import Block
import numpy as np
import random
from train import Train
from track import Track
from signal_light import AutoSignal, HomeSignal
from big_block import BigBlock
from control_point import ControlPoint, AutoPoint

import networkx as nx

class System(nx.Graph):
    def __init__(self, init_time, *args, **kwargs):
        super().__init__()
        """
        Parameters
        ----------
        :_blk_length_list: list (**kw)
            A list of block lengths for each block.
        :tracks: list (**kw)
            A list of total number of tracks per block.
        :dos_period: list or tuple (**kw)
            2-element list or tuple showing the starting and finishing time of DoS attacks.
        :headway: (**kw)
            Traffic headway in seconds for unidirectional trains. 500 by default.
        :dos_pos: int (**kw)
            Index of block to be attacked by DoS. -1 by default (no DoS).
        :refresh_time: int (**kw)
            Seconds between two consecutive traverse calculations of the simulation.
        :sp_containter: list (**kw)
            A list of randomized speed values for trains to initialize by. Uniform range.
        :add_container: list (**kw)
            A list of randomized acceleration values for trains to initialize by. Uniform range.
        """
        _blk_length_list = [5] * 10     if not kwargs.get('blk_length_list') else kwargs.get('blk_length_list')
        _blk_number = len(_blk_length_list)

        self.sys_time = init_time.timestamp()   # CPU format time in seconds, transferable between numerical value and M/D/Y-H/M/S string values 
        self.trains, self.train_num = [], 0
        self.tracks = kwargs.get('tracks')      # self.track list determines the current topology
        # list of big blocks
       
        self.big_block_list = []
        # list of control points
        self.cp_list = []
        self.network_constructor()
        # network_constructor initializes self.big_block_list & self.cp and create graph instance
        self.blocks = [Block(i, _blk_length_list[i], max_sp=0.01, track_number=kwargs.get('tracks')[i]) for i in range(_blk_number)]
        self.register(self.blocks)
        # register method links the observation relationships
        self.dos_period = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp() for t in kwargs.get('dos_period') if type(t) == str]
        self.headway = 500  if not kwargs.get('headway') else kwargs.get('headway')
        self.dos_pos = -1   if not kwargs.get('dos_pos') else kwargs.get('dos_pos')
        self.last_train_init_time = self.sys_time
        self.sp_container = args[0]     if args else [random.uniform(0.01, 0.02) for i in range(20)]
        self.acc_container = args[1]    if args else [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
        self.refresh_time = 1           if not kwargs.get('refresh_time') else kwargs.get('refresh_time')
        self.block_intervals = []
        # interval is the two-element array containing mile posts of boundaries, generated below in the loops
        for i in range(_blk_number):
            if i == 0:
                self.block_intervals.append([0, _blk_length_list[0]])
            else:
                left = self.block_intervals[i - 1][1]
                right = left + _blk_length_list[i]
                self.block_intervals.append([left, right]) 
    
    def register(self, blocks):
        # 将临近siding的blk的左灯或者右灯变为homesignal
        multi_track_blk = []
        for i, blk in enumerate(blocks):
            if blk.track_number > 1:
                multi_track_blk.append(i)
            if i > 0 and blocks[i - 1].track_number > 1:
                blk.tracks[0].left_signal = HomeSignal('right')
                blk.tracks[0].left_signal.hs_type = 'B'
            if i < len(blocks) - 1 and blocks[i + 1].track_number > 1:
                blk.tracks[0].right_signal = HomeSignal('left')
                blk.tracks[0].right_signal.hs_type = 'B'
        # 订阅过程
        # 右灯注册，前一个blk右灯注册后一个blk的右灯，跳过siding
        # ABS订阅ABS
        for i in range(len(blocks) - 1):
            if blocks[i + 1].track_number <= 1:
                curr_light = blocks[i].tracks[0].right_signal
                next_light = blocks[i + 1].tracks[0].right_signal
                next_light.add_observer(curr_light)
        # 左灯注册，后一个blk左灯注册前一个blk的左灯，跳过siding
        # ABS订阅ABS
        for i in range(len(blocks)):
            if i > 0 and blocks[i - 1].track_number <= 1:
                curr_light = blocks[i].tracks[0].left_signal
                last_light = blocks[i - 1].tracks[0].left_signal
                last_light.add_observer(curr_light)
        # 大blk中的homesignal订阅: single_track_blk右灯注册进入multi_track_blk的home左灯
        # ABS订阅HS
        curr_mul_tk_blk_idx = 0
        for i in range(len(blocks)):
            if curr_mul_tk_blk_idx == len(multi_track_blk):
                break
            if i not in multi_track_blk:
                sgl_blk_tk = blocks[i].tracks[0]
                mul_blk = blocks[multi_track_blk[curr_mul_tk_blk_idx]]
                for tk_idx in range(mul_blk.track_number):
                    mul_blk.tracks[tk_idx].left_signal.add_observer(sgl_blk_tk.right_signal)
            else:
                mul_blk = blocks[i]
                sgl_blk_tk = blocks[i - 1].tracks[0]
                for tk_idx in range(mul_blk.track_number):
                    sgl_blk_tk.right_signal.add_observer(mul_blk.tracks[tk_idx].left_signal)
                    sgl_blk_tk.left_signal.add_observer(mul_blk.tracks[tk_idx].left_signal)
                curr_mul_tk_blk_idx += 1
        # 大blk中的homesignal订阅: single_track_blk左灯注册进入multi_track_blk的home右灯        
        # ABS订阅HS
        curr_mul_tk_blk_idx = len(multi_track_blk) - 1
        for i in range(len(blocks) - 1,0,-1):
            print(i)
            if curr_mul_tk_blk_idx == -1:
                break
            if i not in multi_track_blk:
                sgl_blk_tk = blocks[i].tracks[0]
                mul_blk = blocks[multi_track_blk[curr_mul_tk_blk_idx]]
                for tk_idx in range(mul_blk.track_number):
                    mul_blk.tracks[tk_idx].right_signal.add_observer(sgl_blk_tk.left_signal)
            else:
                mul_blk = blocks[i]
                sgl_blk_tk = blocks[i + 1].tracks[0]
                for tk_idx in range(mul_blk.track_number):
                    sgl_blk_tk.left_signal.add_observer(mul_blk.tracks[tk_idx].right_signal)
                    sgl_blk_tk.right_signal.add_observer(mul_blk.tracks[tk_idx].right_signal)
                curr_mul_tk_blk_idx -= 1
        
        ##############################################################################
        # 最左和最右的block中两盏灯为homesinal
        self.blocks[0].tracks[0].right_signal = HomeSignal('left')
        self.blocks[0].tracks[0].right_signal.hs_type = 'B'
        self.blocks[len(self.blocks) - 1].tracks[0].left_signal = HomeSignal('right')
        self.blocks[len(self.blocks) - 1].tracks[0].left_signal.hs_type = 'B'

        most_left_home_signal = self.blocks[0].tracks[0].right_signal
        most_right_home_singal = self.blocks[len(self.blocks) - 1].tracks[0].left_signal

        # 取出最左和最有的multi_blk_index
        first_right = len(blocks)
        first_left = -1
        if len(multi_track_blk) != 0:
            first_right = multi_track_blk[0]
            first_left = multi_track_blk[-1]
        
        # 将左边第一个multi_blk_index之前的blk的左灯全部注册到最左边第一个右灯上。
        for i in range(first_right):
            curr_left_signal = blocks[i].tracks[0].left_signal
            most_left_home_signal.add_observer(curr_left_signal)

        # 将右边第一个multi_blk_index之后的blk的右灯全部注册到最右边第一个左灯上。
        for i in range(len(blocks) - 1, first_left, -1):
            curr_right_signal = blocks[i].tracks[0].right_signal
            most_right_home_singal.add_observer(curr_right_signal)
        ##############################################################################

        ##### 普通ABS测试
        # self.blocks[0].tracks[0].right_signal.change_color_to('g')
        # self.blocks[len(self.blocks) - 1].tracks[0].right_signal.change_color_to('r')
        ##### 头尾HS测试
        # self.blocks[0].tracks[0].right_signal.change_color_to('g')
        # self.blocks[9].tracks[0].left_signal.change_color_to('g')
        ##### multi_track_blk附近的HS测试 （B）
        # self.blocks[4].tracks[0].left_signal.change_color_to('g')
        ##### multi_track_blk的某个track灯为非红测试
        self.blocks[4].tracks[0].right_signal.change_color_to('r')
        
    def network_constructor(self):
        # 初始化self.big_block_list和self.cp
        # 将self.tracks中连续的数字建立为一个big block
        # 双指针法来完成连续相同数字的big block初始化
        # 输入的是一个每个track个数的列表 TODO: 输入改为networkx的ebunch格式
        # construct the nbunch and ebunch list for Graph
        self.nbunch = []
        self.ebunch = []
        for i in range(len(self.tracks) + 1):
            if i == 0:
                self.nbunch.append(ControlPoint(1,self.tracks[i+1]))
            elif 0 < i < len(self.tracks):
                if self.tracks[i-1] == self.tracks[i] == 0：
                    self.nbunch.append(AutoPoint())
                else:
                    self.nbunch.append(ControlPoint(self.tracks[i-1],self.tracks[i]))
            elif i == len(self.tracks):
                self.nbunch.append(ControlPoint(self.tracks[i-1],1))

        prev_tk = self.tracks[0]
        curr_tk = self.tracks[1]
        same_tk_len = 1
        for i in range(1, len(self.tracks)):
            prev_tk = self.tracks[i - 1]
            curr_tk = self.tracks[i]
            if self.tracks[i] != self.tracks[i - 1] or i == len(self.tracks) - 1:
                # 遇到与前一个block的track数目不同，创建新的big block和control point
                big_blk = BigBlock(same_tk_len)
                self.big_block_list.append(big_blk)
                curr_cp = ControlPoint(prev_tk, curr_tk)
                self.cp_list.append(curr_cp)
                same_tk_len = 0
            else:
                i += 1
        # TODO:将bigblock与cp进行订阅

    def generate_train(self, track_idx):
        new_train = Train(self.train_num, 
                          self.train_num, 
                          self, 
                          self.sys_time, 
                          track_idx, 
                          self.sp_container[self.train_num % len(self.sp_container)], 
                          self.acc_container[self.train_num % len(self.acc_container)])
        self.trains.append(new_train)
        self.train_num += 1
        self.last_train_init_time = self.sys_time
        self.blocks[0].occupied_track(track_idx, new_train)

    def update_blk_right(self, i):
        for track in self.blocks[i].tracks:
            if self.dos_period[0] <= self.sys_time <= self.dos_period[1] and i == self.dos_pos:
                track.right_signal.update_signal('r')
            elif i + 1 < len(self.blocks) and not self.blocks[i + 1].has_available_track():
                track.right_signal.update_signal('r')
            elif i + 2 < len(self.blocks) and not self.blocks[i + 2].has_available_track():
                track.right_signal.update_signal('yy')
            elif i + 3 < len(self.blocks) and not self.blocks[i + 3].has_available_track():
                track.right_signal.update_signal('y')
            else:
                track.right_signal.update_signal('g')

        # 如果track数量超过1才考虑让车情况。（第一个blk暂不考虑为多track）
        if i > 0 and len(self.blocks[i].tracks) > 1 and self.blocks[i].has_train():
            # 让车情况下的变灯。
            last_blk_has_train = False
            if not self.blocks[i - 1].has_available_track(): #后一个blk有车
                last_blk_has_train = True

            ava_track = -1
            prev_train_spd = 0

            if last_blk_has_train and self.blocks[i].has_available_track():
                ava_track = self.blocks[i].find_available_track()
                prev_train_spd = self.blocks[i - 1].tracks[0].train.max_speed
            
            # 找到速度最快火车的track
            max_train_track = ava_track
            top_speed = prev_train_spd
            if not self.blocks[i].has_available_track():
                top_speed = -1
            fastest_train_track = 0
            fastest_speed = -1
            for j, track in enumerate(self.blocks[i].tracks):
                if track.train != None and track.train.max_speed > top_speed:
                    max_train_track = j
                    top_speed = track.train.max_speed
                if track.train != None and track.train.max_speed > fastest_speed:
                    fastest_train_track = j
                    fastest_speed = track.train.max_speed
            if max_train_track != fastest_train_track: #说明最快车是后一个block的车。
                fastest_train = self.blocks[i].tracks[fastest_train_track].train
                target_spd = 0
                fastest_train_brk_dis = (fastest_train.curr_speed ** 2 - target_spd ** 2) / fastest_train.acc
                dis_to_blk_end = self.block_intervals[i][1] - fastest_train.curr_pos
                if fastest_train_brk_dis > dis_to_blk_end:  #如果刹车距离大于
                    max_train_track = fastest_train_track

            for j, track in enumerate(self.blocks[i].tracks):
                # if max_train_track >= 0:
                #     print(max_train_track)
                if j != max_train_track:
                    if j == max_train_track:
                        print(j)
                    track.right_signal.update_signal('r')
            
    def update_track_signal_color(self):
        for i in range(len(self.blocks)):
            self.update_blk_right(i)
            
    def refresh(self):
        self.update_track_signal_color()
        headway = self.headway#np.random.normal(exp_buffer, var_buffer)
        # If the time slot between now and the time of last train generation
        # is bigger than headway, it will generate a new train at start point.
        if self.train_num == 0:
            track_idx = self.blocks[0].find_available_track()
            self.generate_train(track_idx)
            
        if self.sys_time - self.last_train_init_time >= headway and self.blocks[0].has_available_track():
            track_idx = self.blocks[0].find_available_track()
            self.generate_train(track_idx)

        for t in self.trains:
            t.update_acc()
        self.trains.sort()
        for i, tr in enumerate(self.trains):
            tr.rank = i
        self.sys_time += self.refresh_time
        
if __name__ =='__main__':
    sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
    sim_term_time = datetime.strptime('2018-01-10 15:30:00', "%Y-%m-%d %H:%M:%S")
    sp_container = [random.uniform(0.01, 0.02) for i in range(20)]
    acc_container = [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
    headway = 200 * random.random() + 400
    sys = System(sim_init_time, sp_container, acc_container,
                 dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],  
                 headway=headway, 
                 tracks=[1,1,1,4,1,1,3,1,1,1], 
                 dos_pos=-1)

    left_light = []
    right_light = []
    for blk in sys.blocks:
        if blk.track_number > 1:
            mul_tk_lgt = []
            for i in range(blk.track_number):
                mul_tk_lgt.append(blk.tracks[i].left_signal.aspect.color)
            left_light.append(mul_tk_lgt)
        else:
            left_light.append(blk.tracks[0].left_signal.aspect.color)

    for blk in sys.blocks:
        if blk.track_number > 1:
            mul_tk_lgt = []
            for i in range(blk.track_number):
                mul_tk_lgt.append(blk.tracks[i].right_signal.aspect.color)
            right_light.append(mul_tk_lgt)
        else:
            right_light.append(blk.tracks[0].right_signal.aspect.color)
    
    # for i in range(len(left_light)):
    #     if len(left_light[i]) == 1:
    #         print("[" + left_light[i] + "," + right_light[i] + "]", end=" ")
    #     else:
    #         print("{", end="")
    #         for j in range(len(left_light[i])):
    #             print("[" + left_light[i][j] + "," + right_light[i][j] + "]", end="")
    #         print("}", end=" ")
    # print("")
    for i in range(len(right_light)):
        if len(right_light[i]) == 1:
            print("[" + right_light[i] + "]", end=" ")
        else:
            print("{", end="")
            for j in range(len(right_light[i])):
                print("[" + right_light[i][j] + "]", end="")
            print("}", end=" ")
    print("")
    
    # print("left light color:  {}".format(left_light))
    # print("right light color: {}".format(right_light))
    