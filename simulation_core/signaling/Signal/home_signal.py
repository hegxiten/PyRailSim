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

from simulation_core.signaling.Signal.base_signal import Signal


class HomeSignal(Signal):
    def __init__(self, port_idx, node, MP=None):
        super().__init__(port_idx, node, MP)
        self.node = None
        self.type = 'home'

        self._group_blocks_to_enter = None
        self._ctrl_points_to_reach = None
        self._governed_group_block = None

    def __repr__(self):
        return 'HomeSig port:{} of {}, aspect {}'.format(str(self.port_idx).rjust(2, ' '),
                                                         self.node,
                                                         self.aspect)

    @property
    def group_blocks_to_enter(self):
        if self._group_blocks_to_enter is None:
            self._group_blocks_to_enter = [self.node.group_block_by_port[p] for p in self.node.available_ports_by_port[self.port_idx]]
        return self._group_blocks_to_enter

    @property
    def ctrl_points_to_reach(self):
        if self._ctrl_points_to_reach is None:
            self._ctrl_points_to_reach = []
            for grp_blk in self.group_blocks_to_enter:
                for p in [grp_blk.node1, grp_blk.node2]:
                    if p != self.node:
                        self._ctrl_points_to_reach.append(p)
        return self._ctrl_points_to_reach

    @property
    def governed_group_block(self):
        if self._governed_group_block is None:
            self._governed_group_block = self.node.group_block_by_port.get(self.port_idx)
        return self._governed_group_block
