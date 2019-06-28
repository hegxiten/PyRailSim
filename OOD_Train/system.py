#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('D:\\Users\\Hegxiten\\workspace\\Rutgers_Railway_security_research\\OOD_Train')

from datetime import datetime, timedelta
import numpy as np
import random
from train import Train
from infrastructure import Track, BigBlock
from signaling import Aspect, AutoSignal, HomeSignal, AutoPoint, ControlPoint
import networkx as nx

class System():
    """
    Parameters
    ----------
    :headway: (**kw), seconds
        Traffic headway in seconds for unidirectional trains. 500 by default.
    :dos_pos: int (**kw)
        Index of block to be attacked by DoS. -1 by default (no DoS).
    :refresh_time: int (**kw), seconds
        Seconds between two consecutive traverse calculations of the simulation.
    :sp_containter: list (**kw), mph
        A list of randomized speed values for trains to initialize by. Uniform range.
    :acc_container: list (**kw), miles/(sec)^2
        A list of randomized acceleration values for trains to initialize by. Uniform range.
    :dcc_container: list (**kw), miles/(sec)^2
        A list of randomized deceleration values for trains to brake by. Uniform range.
    """
    def __init__(self, init_time, *args, **kwargs):
        super().__init__()

        self.sys_time = init_time.timestamp()   # CPU format time in seconds, transferable between numerical value and M/D/Y-H/M/S string values 
        self.trains = []

        self.G_origin = self.graph_constructor()
        self.G_skeleton = self.graph_extractor(self.G_origin)

        self.signal_points = list(self.G_origin.nodes())
        # list of all SignalPoints, including AutoPoints and ControlPoints
        self.control_points = list(self.G_skeleton.nodes())
        # list of all ControlPoints. Its indices are not the same as self.signal_points.
        self.tracks = [data['instance'] for (u,v,data) in list(self.G_origin.edges(data=True))]
        # list of all Tracks. 
        self.bigblocks = [data['instance'] for (u,v,data) in list(self.G_skeleton.edges(data=True))]
        # list of all BigBlocks.

        self.headway = 500  if not kwargs.get('headway') else kwargs.get('headway')
        self.dos_period = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp() for t in kwargs.get('dos_period') if type(t) == str]
        self.dos_pos = -1   if not kwargs.get('dos_pos') else kwargs.get('dos_pos')
        self.last_train_init_time = self.sys_time
        self.sp_container = args[0]     if args else [random.uniform(0.01, 0.02) for i in range(20)]
        self.acc_container = args[1]    if args else [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
        self.dcc_container = args[2]    if args else [random.uniform(self.min_dcc_rate*1.15, self.min_dcc_rate*1.25) for i in range(20)]
        self.dcc_container = [i if i >= self.min_dcc_rate else self.min_dcc_rate for i in self.dcc_container]
        self.refresh_time = 1           if not kwargs.get('refresh_time') else kwargs.get('refresh_time')    

        #------------deprecated------------#
        # self.register(self.blocks)
        # register method links the observation relationships
        #------------deprecated------------#
    
    @property
    def min_dcc_rate(self):    
        '''Absolute value, minimum brake acceleration of all trains required by the 
        system setup. If a train's maximum braking deceleration is smaller than this 
        value, it may violate some signal/speed limit at extreme scenarios. 
        If violated, the program will throw Assertion Errors at braking distance check.
        '''
        _signal_speeds = sorted([spd for _, spd in Aspect.COLOR_SPD_DICT.items()])
        _speed_diff_pairs = [(_signal_speeds[i],_signal_speeds[i+1]) for i in range(len(_signal_speeds)-1)]
        _max_diff_square_of_spd = max([abs(i[0]**2-i[1]**2) for i in _speed_diff_pairs])
        _min_track_length = min([t.length for t in self.tracks])
        return _max_diff_square_of_spd / (2*_min_track_length)
    
    @property
    def train_num(self):
        return len(self.trains)

    @property
    def curr_routing_paths(self):
        def shrinkable(to_remove,rplist):
            for i in to_remove:
                if i in rplist:
                    rplist.remove(i)
            rplist_copy = rplist
            for rp in rplist_copy:
                for _rp in rplist:
                    if connectable(rp, _rp) or connectable(_rp, rp):
                        return True
            return False
        def connectable(rp1,rp2):
            if rp1 and rp2:
                rp1_head, rp1_tail = rp1[0][0][0], rp1[-1][-1][0]
                rp2_head, rp2_tail = rp2[0][0][0], rp2[-1][-1][0]
                rp1_head_port, rp1_tail_port = rp1[0][0][1], rp1[-1][-1][1]
                rp2_head_port, rp2_tail_port = rp2[0][0][1], rp2[-1][-1][1]
                if rp1_tail == None or rp2_head == None:
                    return False
                elif rp1_tail == rp2_head:
                    assert rp1_tail.current_routes == rp2_head.current_routes
                    if (rp1_tail_port, rp2_head_port) in rp1_tail.current_routes:
                        return True
            return False

        _routing_list = [i for i in [getattr(_bblk,'self_routing_path') for _bblk in self.bigblocks] if i]
        if self.control_points[0].current_routes:
            for r in self.control_points[0].current_routes:
                if self.control_points[0].track_by_port.get(r[0]):
                    _routing_list.append([((self.control_points[0],r[1]),(None,None))])
                if self.control_points[0].track_by_port.get(r[1]):
                    _routing_list.append([((None,None),(self.control_points[0],r[0]))])
        if self.control_points[-1].current_routes:
            for r in self.control_points[-1].current_routes:
                if self.control_points[-1].track_by_port.get(r[0]):
                    _routing_list.append([((self.control_points[-1],r[1]),(None,None))])
                if self.control_points[-1].track_by_port.get(r[1]):
                    _routing_list.append([((None,None),(self.control_points[-1],r[0]))])
        
        _to_remove = []        
        while shrinkable(_to_remove, _routing_list):
            for i in range(len(_routing_list)):
                for j in range(len(_routing_list)):
                    if connectable(_routing_list[i], _routing_list[j]):
                        _routing_list[i].extend(_routing_list[j])
                        _to_remove.append(_routing_list[j])
                    elif connectable(_routing_list[j], _routing_list[i]):
                        _routing_list[j].extend(_routing_list[i])
                        _to_remove.append(_routing_list[i])
        return _routing_list

    def get_track_by_point_port_pairs(self, p1, p1_port, p2, p2_port):
        for t in self.tracks:
            if p1 in (t.L_point, t.R_point) and p2 in (t.L_point, t.R_point):
                if p1_port in (t.L_point_port, t.R_point_port) and p2_port in (t.L_point_port, t.R_point_port):
                    return t
        return None

    def graph_constructor(self, node={}, track={}):      
        '''Initialize the MultiGraph object with railroad components 
        (CP, AT as nodes, Tracks as edges)'''
        # TODO: construct the nbunch and ebunch list for Graph in network_constructor.py
        # TODO: automation of port connecting and index assignment
        # TODO: to be achieved in network_constructor.py
        TEST_NODE = {   0:ControlPoint(self, idx=0, ports=[0,1], MP=0.0), \
                        1:AutoPoint(self, 1, MP=5.0), \
                        2:AutoPoint(self, 2, MP=10.0), \
                        3:ControlPoint(self, idx=3, ports=[0,1,3], ban_ports_by_port={1:[3],3:[1]}, MP=15.0), \
                        4:ControlPoint(self, idx=4, ports=[0,2,1], ban_ports_by_port={0:[2],2:[0]}, MP=20.0), \
                        5:AutoPoint(self, 5, MP=25.0), \
                        6:ControlPoint(self, idx=6, ports=[0,1,3], ban_ports_by_port={1:[3],3:[1]}, MP=30.0), \
                        7:ControlPoint(self, idx=7, ports=[0,2,1], ban_ports_by_port={0:[2],2:[0]}, MP=35.0), \
                        8:AutoPoint(self, 8, MP=40.0), \
                        9:AutoPoint(self, 9, MP=45.0), \
                        10:ControlPoint(self, idx=10, ports=[0,1], MP=50.0)}       

        TEST_TRACK = [  Track(self,TEST_NODE[0], 1, TEST_NODE[1], 0), Track(self,TEST_NODE[1], 1, TEST_NODE[2], 0), Track(self,TEST_NODE[2], 1, TEST_NODE[3], 0),\
                        Track(self,TEST_NODE[3], 1, TEST_NODE[4], 0), Track(self,TEST_NODE[3], 3, TEST_NODE[4], 2, edge_key=1),\
                        Track(self,TEST_NODE[4], 1, TEST_NODE[5], 0), Track(self,TEST_NODE[5], 1, TEST_NODE[6], 0),\
                        Track(self,TEST_NODE[6], 1, TEST_NODE[7], 0), Track(self,TEST_NODE[6], 3, TEST_NODE[7], 2, edge_key=1),\
                        Track(self,TEST_NODE[7], 1, TEST_NODE[8], 0), Track(self,TEST_NODE[8], 1, TEST_NODE[9], 0), Track(self,TEST_NODE[9], 1, TEST_NODE[10], 0)]
        
        _node = TEST_NODE if not node else node
        nbunch = [_node[i] for i in range(len(_node))]
        _track = TEST_TRACK if not track else track
        ebunch = [_track[i] for i in range(len(_track))]

        # _node and _track will be parameters passed from outside in the future development
        G = nx.MultiGraph()
        for n in nbunch:
            G.add_node(n, attr=n.__dict__, instance=n)              
            # __dict__ of instances (CPs, ATs, Tracks) is pointing the same 
            # attribute dictionary as the node in the MultiGraph

        for t in ebunch:
            G.add_edge(t.L_point, t.R_point, key=t.edge_key, attr=t.__dict__, instance=t)          
            # __dict__ of instances (CPs, ATs, Tracks) is pointing the same 
            # attribute dictionary as the edge in the MultiGraph
            # key is the index of parallel edges between two nodes
            t.L_point.track_by_port[t.L_point_port] = t.R_point.track_by_port[t.R_point_port] = t

        for i in G.nodes():     # register the neighbor nodes as observers to each node
            i.neighbor_nodes.extend([n for n in G.neighbors(i)])              
            for n in G.neighbors(i):
                i.add_observer(n)
        return G
    
    def graph_extractor(self, G):         
        '''
        Extract the skeletion MultiGraph with only ControlPoints and Bigblocks
        ----------
        Parameter:
            G: networkx MultiGraph instance of the raw network with only Track as edges.
        ----------
        Return:
            F: networkx MultiGraph instance with only BigBlock as edges.
        '''
        F = G.copy()        
        # F is a shallow copy of G: attrbutes of G/F components 
        # are pointing at the same memory.
        def _get_new_edge(node, length=False):
            at_neighbor = [j for j in F.neighbors(i)]
            assert len(at_neighbor) == len(F.edges(i)) == 2
            edgetrk_L_points = [F[at_neighbor[0]][node][0]['instance'].L_point, F[node][at_neighbor[1]][0]['instance'].L_point]
            edgetrk_R_points = [F[at_neighbor[0]][node][0]['instance'].R_point, F[node][at_neighbor[1]][0]['instance'].R_point]
            edgetrk_L_points.remove(i)
            edgetrk_R_points.remove(i)
            new_edge_length = F[at_neighbor[0]][i][0]['instance'].length + F[i][at_neighbor[1]][0]['instance'].length
            if length:
                return edgetrk_L_points[0], edgetrk_R_points[0], new_edge_length
            else:  
                return edgetrk_L_points[0], edgetrk_R_points[0]

        for i in G.nodes():
            # only use G.nodes() instead of F.nodes() to get original nodes 
            # to avoid dictionary size changing issues. 
            # all the following graph updates are targeted on F
            if i.type == 'at':
                new_L_point, new_R_point = _get_new_edge(i)
                assert len(F[new_L_point][i]) == len(F[i][new_R_point]) == 1
                new_track =  Track( self, new_L_point, F[new_L_point][i][0]['instance'].L_point_port,\
                                    new_R_point, F[i][new_R_point][0]['instance'].R_point_port,\
                                    edge_key=0)

                F.remove_node(i)
                F.add_edge(new_L_point, new_R_point, attr=new_track.__dict__, instance=new_track)     
                # MultiGraph parallel edges are auto-keyed (0, 1, 2...)
                # default 0 as mainline, idx as track number

        for (u, v, k) in F.edges(keys=True):
            blk_path = nx.shortest_path(G, u, v)
            big_block_edges = [(blk_path[i], blk_path[i+1]) for i in range(len(blk_path) - 1)]
            big_block_instance = BigBlock(  self,   u, F[u][v][k]['instance'].L_point_port,\
                                                    v, F[u][v][k]['instance'].R_point_port,\
                                            edge_key=k, \
                                            raw_graph=G, cp_graph=F)
            u.bigblock_by_port[F[u][v][k]['instance'].L_point_port] = v.bigblock_by_port[F[u][v][k]['instance'].R_point_port] = big_block_instance

            for (n, m) in big_block_edges:
                if G[n][m][k]['instance'] not in big_block_instance.tracks:
                    big_block_instance.tracks.append(G[n][m][k]['instance'])
                # get the list of track unit components of a bigblock, and record in the instance
            
            F[u][v][k]['attr'] = big_block_instance.__dict__
            F[u][v][k]['instance'] = big_block_instance
            for t in F[u][v][k]['instance'].tracks:
                t.bigblock = F[u][v][k]['instance']
        return F

    def generate_train(self, init_point, init_port, dest_point, dest_port):
        '''Generate train only. 
        '''
        if self.generable(init_point, dest_point):
            new_train = Train(idx=self.train_num, 
                            rank=self.train_num, 
                            system=self, 
                            init_time=self.sys_time, 
                            init_segment=init_segment, 
                            max_sp=self.sp_container[self.train_num % len(self.sp_container)], 
                            max_acc=self.acc_container[self.train_num % len(self.acc_container)], 
                            max_dcc=self.dcc_container[self.train_num % len(self.dcc_container)])
            self.trains.append(new_train)
            self.train_num += 1
            self.last_train_init_time = self.sys_time
            new_train.curr_track.train.append(new_train)

    def update_routing(self):
        for trn in self.trains:
            if not trn.curr_sig:
                pass
            elif not trn.curr_sig.route:
                if self.generable(trn.curr_sigpoint, trn.curr_sigport, trn.intended_sigpoint, trn.intended_sigport):
                    trn.curr_sigpoint.open_route((curr_sigport,trn.intended_sigport))
    
    def refresh(self):
        self.generate_train()
        self.trains.sort()
        self.update_routing()
        for t in self.trains:
            t.update_acc()
        self.trains.sort()                  # 更新完每列列车后进行排序，为调度逻辑做准备
        for i, tr in enumerate(self.trains):
            tr.rank = i
        self.sys_time += self.refresh_time

    def generable(init_point, init_port, dest_point, dest_port):
        _parallel_tracks = self.num_parallel_tracks(init_point, dest_point)
        _outbound_trains = self.get_trains_between_points(from_point=init_point, to_point=dest_point, directed=True)
        _inbound_trains = self.get_trains_between_points(from_point=dest_point, to_point=init_point, directed=True)
        return True if min(len(_outbound_trains), len(_inbound_trains)) <= len(_parallel_tracks)\
            else False

    def num_parallel_tracks(self, init_point, dest_point):
        _mainline_section = nx.shortest_path(self.G_origin, init_point, dest_point)
        _start_point = _mainline_section.pop(0)
        count = 0
        _traversed = []
        while _mainline_section:
            for t in _traversed:
                if t in _mainline_section:
                    _mainline_section.remove(t)
            for p in _mainline_section:
                if len(list(nx.all_simple_paths(self.G_origin, _start_point, p))) == 1:
                    _traversed.append(p)
                    continue
                else:
                    count += len(list(nx.all_simple_paths(self.G_origin, _start_point, p))) -1
                    _traversed.append(p)
                    _start_point = p
                    break
        return count

    def get_trains_between_points(self, from_point, to_point, directed=False):
        all_paths = list(nx.all_simple_paths(self.G_origin, from_point, to_point))
        _trains = []
        for p in all_paths:
            for i in range(len(p)-1):
                for k in list(self.G_origin[p[i]][p[i+1]]):
                    for t in self.G_origin[p[i]][p[i+1]][k]['instance'].train:
                        if t not in _trains:
                            _trains.append((t, t.curr_routing_path_segment, (p[i], p[i+1], k)))
        if not directed:
            return [i[0] for i in _trains]
        else:
            return [i[0] for i in _trains if (i[1][0][0], i[1][1][0]) == i[2]]

    def clear_train(self, train=None):
        if train:
            self.trains.remove(train)
        else:
            self.trains = []

    def update_blk_right(self, i):
        '''
        logics of overpassing, manipulating controlpoints
        TODO: translate the operations below into ControlPoint manipulations'''
        # 只管变化（若满足条件更新CP 路径，否则无操作）
        # for track in self.blocks[i].tracks:
        #     if self.dos_period[0] <= self.sys_time <= self.dos_period[1] and i == self.dos_pos:
        #         track.right_signal.update_signal('r')
        #     elif i + 1 < len(self.blocks) and not self.blocks[i + 1].is_Occupied():
        #         track.right_signal.update_signal('r')
        #     elif i + 2 < len(self.blocks) and not self.blocks[i + 2].is_Occupied():
        #         track.right_signal.update_signal('yy')
        #     elif i + 3 < len(self.blocks) and not self.blocks[i + 3].is_Occupied():
        #         track.right_signal.update_signal('y')
        #     else:
        #         track.right_signal.update_signal('g')

        # 如果track数量超过1才考虑让车情况。（第一个blk暂不考虑为多track）
        if i > 0 and len(self.blocks[i].tracks) > 1 and self.blocks[i].has_train():
            # 让车情况下的变灯。
            last_blk_has_train = False
            if not self.blocks[i - 1].is_Occupied(): #后一个blk有车
                last_blk_has_train = True

            ava_track = -1
            prev_train_spd = 0

            if last_blk_has_train and self.blocks[i].is_Occupied():
                ava_track = self.blocks[i].find_available_track()
                prev_train_spd = self.blocks[i - 1].tracks[0].train.max_speed
            
            # 找到速度最快火车的track
            max_train_track = ava_track
            top_speed = prev_train_spd
            if not self.blocks[i].is_Occupied():
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
        '''
        TODO: confirm if no longer needed or not
        '''
        for i in range(len(self.blocks)):
            self.update_blk_right(i)        # 每次只更新右侧信号，是因为仅考虑从左到右的车流。
            
    def register(self, blocks):
        '''
        TODO: confirm if no longer needed or not
        '''
        pass
        return
        # 本段代码及以下所有方法应该都用不上了。（除了self.__name__ = '__main__' 的测试代码）
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

if __name__ =='__main__':
    sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
    sim_term_time = datetime.strptime('2018-01-10 15:30:00', "%Y-%m-%d %H:%M:%S")
    sp_container = [random.uniform(0.01, 0.02) for i in range(20)]
    acc_container = [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
    dcc_container = [random.uniform(2.78e-05*0.85, 2.78e-05*1.15) for i in range(20)]
    headway = 200 * random.random() + 400
    sys = System(sim_init_time, sp_container, acc_container, dcc_container,
                 dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],  
                 headway=headway, 
                 dos_pos=-1,
                 refresh_time = 20)
    
