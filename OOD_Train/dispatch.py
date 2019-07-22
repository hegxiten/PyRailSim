#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(
    'D:\\Users\\Hegxiten\\workspace\\Rutgers_Railway_security_research\\OOD_Train'
)
import random
import numpy as np
from datetime import datetime, timedelta
from collections.abc import MutableSequence
import networkx as nx
from itertools import combinations, permutations

from infrastructure import Track, BigBlock
from signaling import AutoSignal, HomeSignal, AutoPoint, ControlPoint


class Dispatcher():
    def __init__(self, sys):
        self.system = sys

        setattr(self.system, 'dispatcher', self)

    def get_all_routes(self, source, source_port, target, target_port):
        route_list = []
        cp_path_generator = nx.all_simple_paths(self.system.G_skeleton, 
                source=source, target=target)
        parallel_bblks = []
        #for 
        #for cp_path in cp_path_generator:
        #    _single_route = 

    
    def get_main_route(self, source, source_port, target, target_port):
        main_route = []
        main_cp_path = nx.shortest_path(self.system.G_skeleton, 
                source=source, target=target, weight='edge_key')
        port_by_bblk = lambda bblk, cp: [p for p in cp.ports 
            if cp.bigblock_by_port.get(p) == bblk][0]
        for cp1, cp2 in zip(main_cp_path[0:],main_cp_path[1:]):
            _parallel_bblks = [self.system.G_skeleton[cp1][cp2][k]['instance'] 
                for k in self.system.G_skeleton[cp1][cp2].keys()]
            _main_bblk = min(_parallel_bblks)
            rp_seg = (  (cp1, port_by_bblk(_main_bblk, cp1)), 
                        (cp2, port_by_bblk(_main_bblk, cp2)))
            main_route.append(rp_seg)
        if not source.bigblock_by_port.get(source_port):
            main_route.insert(0, ((None,None),(source, source_port)))
        if source.bigblock_by_port.get(source_port):
            init_bblk = source.bigblock_by_port.get(source_port)
            _p = init_bblk.shooting_point(point=source, port=source_port)
            _port = init_bblk.shooting_port(point=source, port=source_port)
            main_route.insert(0, ((_p,_port),(source, source_port)))
        if not target.bigblock_by_port.get(target_port):
            main_route.append(((target, target_port),(None,None)))
        if target.bigblock_by_port.get(target_port):
            final_bblk = target.bigblock_by_port.get(target_port)
            _p = final_bblk.shooting_point(point=target, port=target_port)
            _port = final_bblk.shooting_port(point=target, port=target_port)
            main_route.append(((target, target_port),(_p,_port)))
        return main_route

    def get_all_routes(self, source, source_port, target, target_port):
        all_parallel_bblks = []
        for ((e1p1,e1p2,k1), (e2p1,e2p2,k2)) in combinations(self.system.G_skeleton.edges, 2):
            if e1p1 == e2p1 and e1p2 == e2p2:
                if self.system.G_skeleton[e1p1][e1p2][k1]['instance'] not in all_parallel_bblks:
                    all_parallel_bblks.append(self.system.G_skeleton[e1p1][e1p2][k1]['instance'])
                if self.system.G_skeleton[e2p1][e2p2][k2]['instance'] not in all_parallel_bblks:
                    all_parallel_bblks.append(self.system.G_skeleton[e2p1][e2p2][k2]['instance'])
        
        port_by_bblk = lambda bblk, cp: [p for p in cp.ports 
                if cp.bigblock_by_port.get(p) == bblk][0]
        route_list = []
        cp_paths = list(nx.all_simple_paths(self.system.G_skeleton, 
                source=source, target=target))
        while cp_paths:
            _single_cp_route = cp_paths[0]
            _single_route = []
            for cp1, cp2 in zip(_single_cp_route[0:],_single_cp_route[1:]):
                _parallel_bblks = [self.system.G_skeleton[cp1][cp2][k]['instance'] 
                    for k in self.system.G_skeleton[cp1][cp2].keys()]
                _tentative_bblk = random.choice(_parallel_bblks)
                rp_seg = (  (cp1, port_by_bblk(_tentative_bblk, cp1)), 
                            (cp2, port_by_bblk(_tentative_bblk, cp2)))
                _single_route.append(rp_seg)
            if not source.bigblock_by_port.get(source_port):
                _single_route.insert(0, ((None,None),(source, source_port)))
            if source.bigblock_by_port.get(source_port):
                init_bblk = source.bigblock_by_port.get(source_port)
                _p = init_bblk.shooting_point(point=source, port=source_port)
                _port = init_bblk.shooting_port(point=source, port=source_port)
                _single_route.insert(0, ((_p,_port),(source, source_port)))
            if not target.bigblock_by_port.get(target_port):
                _single_route.append(((target, target_port),(None,None)))
            if target.bigblock_by_port.get(target_port):
                final_bblk = target.bigblock_by_port.get(target_port)
                _p = final_bblk.shooting_point(point=target, port=target_port)
                _port = final_bblk.shooting_port(point=target, port=target_port)
                _single_route.append(((target, target_port),(_p,_port)))
            
            if _single_route not in route_list:
                cp_paths.pop(0)
                route_list.append(_single_route)
        return route_list
        
    def max_MA_limit(self, route):
        pass

    def conflicts(self):
        pass

    def grant(self, trn):
        pass

    def revoke(self, trn):
        pass