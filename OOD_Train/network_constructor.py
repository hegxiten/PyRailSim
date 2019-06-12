from datetime import datetime, timedelta
import numpy as np
import random
from train import Train
from infrastructure import Track, Block, BigBlock
from signaling import AutoSignal, HomeSignal, AutoPoint, ControlPoint

import networkx as nx

class RailNetwork():
    """
    Need to return ready-for-use pbunch, tbunch and _nodes for graph_constructor
    """
    def __init__(self, init_time, *args, **kwargs):
        super().__init__()
        _blk_length_list = [5] * 10     if not kwargs.get('blk_length_list') else kwargs.get('blk_length_list')
        _blk_number = len(_blk_length_list)

        self.sys_time = init_time.timestamp()   # CPU format time in seconds, transferable between numerical value and M/D/Y-H/M/S string values 
        self.trains, self.train_num = [], 0
        self.tracks = kwargs.get('tracks')      # self.track list determines the current topology
        # list of big blocks
       
        self.big_block_list = []
        # list of control points
        self.cp_list = []
        self.G = self.network_constructor()
        self.F = self.network_extractor(self.G)
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
        
        #------------deprecated------------#
        #self.block_intervals = []
        ## interval is the two-element array containing mile posts of boundaries, generated below in the loops
        #for i in range(_blk_number):
        #    if i == 0:
        #        self.block_intervals.append([0, _blk_length_list[0]])
        #    else:
        #        left = self.block_intervals[i - 1][1]
        #        right = left + _blk_length_list[i]
        #        self.block_intervals.append([left, right]) 
        #------------deprecated------------#

        for i in range(len(self.tracks) + 1):
            if i == 0:
                pbunch.append(ControlPoint(1,self.tracks[i+1]))
            elif 0 < i < len(self.tracks):
                if self.tracks[i-1] == self.tracks[i] == 0:
                    pbunch.append()
                else:
                    pbunch.append(ControlPoint(self.tracks[i-1],self.tracks[i]))
            elif i == len(self.tracks):
                pbunch.append(ControlPoint(self.tracks[i-1],1))

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