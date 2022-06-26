#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    PyRailSim
    Copyright (C) 2019  Zezhou Wang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import random

from simulation_core.network.network_utils import all_simple_paths, shortest_path

class Dispatcher():
    @staticmethod
    def cp_port_leading_to(autopoint, port):
        assert autopoint.__class__.__name__ == 'AutoPoint'
        if autopoint.signal_by_port[port].upwards:
            return autopoint.bigblock.L_point, autopoint.bigblock.L_point_port
        if autopoint.signal_by_port[port].downwards:
            return autopoint.bigblock.R_point, autopoint.bigblock.R_point_port
    
    def __init__(self, sys):
        self.system = sys
        setattr(self.system, 'dispatcher', self)
    
    def cp_segment_to_node(self, cp_seg):
        cp1,prt1,cp2,prt2 = cp_seg[0][0],cp_seg[0][1],cp_seg[1][0],cp_seg[1][1]
        assert cp1.__class__.__name__ == cp2.__class__.__name__ == 'CtrlPoint'


    def get_path(self, route, raw=True):
        assert len(route) >=2
        cp_path = [rp_seg[0][0] for rp_seg in route[1:]]
        if raw is False:
            return cp_path
        if raw is True:
            pass


    def get_route(self, src=None, srcport=None, tgt=None, tgtport=None, 
                        path=None, mainline=True):
        if src == tgt == path == None:
            raise Exception("Need to specify either a path or pair of points!")
        if src.__class__.__name__ == 'AutoPoint':
            src, srcport = self.cp_port_leading_to(src, srcport)
        if tgt.__class__.__name__ == 'AutoPoint':
            tgt, tgtport = self.cp_port_leading_to(tgt, tgtport)
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
            _p = init_bblk.get_shooting_point(point=src, port=srcport)
            _port = init_bblk.get_shooting_port(point=src, port=srcport)
            route.insert(0, ((_p,_port),(src, srcport)))
        if not tgt.bigblock_by_port.get(tgtport):
            route.append(((tgt, tgtport),(None,None)))
        if tgt.bigblock_by_port.get(tgtport):
            final_bblk = tgt.bigblock_by_port.get(tgtport)
            _p = final_bblk.get_shooting_point(point=tgt, port=tgtport)
            _port = final_bblk.get_shooting_port(point=tgt, port=tgtport)
            route.append(((tgt, tgtport),(_p,_port)))
        return route

    def all_routes_generator(self, src, srcport, tgt, tgtport):
        src, srcport, tgt, tgtport = src, srcport, tgt, tgtport 
        if src.__class__.__name__ == 'AutoPoint':
            src, srcport = self.cp_port_leading_to(src, srcport)
        if tgt.__class__.__name__ == 'AutoPoint':
            tgt, tgtport = self.cp_port_leading_to(tgt, tgtport)
        cp_paths = list(all_simple_paths(self.system.G_skeleton, 
                                            source=src, target=tgt))
        _route_list = []
        while cp_paths:
            _single_cp_route = cp_paths[0]
            _single_route = self.get_route(src, srcport, tgt, tgtport, 
                                        path=_single_cp_route, mainline=False)
            if _single_route not in _route_list:
                cp_paths.pop(0)
                _route_list.append(_single_route)
                yield _single_route

    def get_all_routes(self, src, srcport, tgt, tgtport):
        return list(self.all_routes_generator(src, srcport, tgt, tgtport))


    def max_MA_limit(self, route):
        pass

    def conflicts(self):
        pass

    def grant(self, trn):
        pass

    def revoke(self, trn):
        pass
