#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import random
import sys

sys.path.append(
    'D:\\Users\\Hegxiten\\workspace\\Rutgers_Railway_security_research\\OOD_Train'
)

from collections.abc import MutableSequence
from datetime import datetime, timedelta
from itertools import combinations, permutations

import networkx as nx
import numpy as np

from rail_networkx import all_simple_paths, shortest_path


class Dispatcher():
    def __init__(self, sys):
        self.system = sys
        setattr(self.system, 'dispatcher', self)

    def get_route(self, src, srcport, tgt, tgtport, path=None, mainline=True):
        route = []
        cp_path = path
        if cp_path is None:
            cp_path = shortest_path(self.system.G_skeleton, 
                            source=src, target=tgt, weight='weight_mainline') \
                    if mainline==True else \
                    next(all_simple_paths(self.system.G_skeleton, 
                                            source=src, target=tgt))
        port_by_bblk = lambda bblk, cp: [p for p in cp.ports 
            if cp.bigblock_by_port.get(p) == bblk][0]
        for cp1, cp2 in zip(cp_path[0:],cp_path[1:]):
            _parallel_bblks = [self.system.G_skeleton[cp1][cp2][k]['instance'] 
                for k in self.system.G_skeleton[cp1][cp2].keys()]
            selected_bblk = min(_parallel_bblks) \
                if mainline else random.choice(_parallel_bblks)
            rp_seg = (  (cp1, port_by_bblk(selected_bblk, cp1)), 
                        (cp2, port_by_bblk(selected_bblk, cp2)))
            route.append(rp_seg)
        if not src.bigblock_by_port.get(srcport):
            route.insert(0, ((None,None),(src, srcport)))
        if src.bigblock_by_port.get(srcport):
            init_bblk = src.bigblock_by_port.get(srcport)
            _p = init_bblk.shooting_point(point=src, port=srcport)
            _port = init_bblk.shooting_port(point=src, port=srcport)
            route.insert(0, ((_p,_port),(src, srcport)))
        if not tgt.bigblock_by_port.get(tgtport):
            route.append(((tgt, tgtport),(None,None)))
        if tgt.bigblock_by_port.get(tgtport):
            final_bblk = tgt.bigblock_by_port.get(tgtport)
            _p = final_bblk.shooting_point(point=tgt, port=tgtport)
            _port = final_bblk.shooting_port(point=tgt, port=tgtport)
            route.append(((tgt, tgtport),(_p,_port)))
        return route

    def get_all_routes(self, src, srcport, tgt, tgtport):
        route_list = []
        cp_paths = list(all_simple_paths(self.system.G_skeleton, 
                                            source=src, target=tgt))
        while cp_paths:
            _single_cp_route = cp_paths[0]
            _single_route = self.get_route(src, srcport, tgt, tgtport, 
                                        path=_single_cp_route, mainline=False)
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
