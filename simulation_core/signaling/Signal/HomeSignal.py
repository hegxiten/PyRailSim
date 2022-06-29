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

from simulation_core.signaling.Signal.Signal import Signal


class HomeSignal(Signal):
    def __init__(self, port_idx, signal_point, MP=None):
        super().__init__(port_idx, signal_point, MP)
        self.sigpoint = None
        self.type = 'home'

        self._bblks_to_enter = None
        self._ctrl_pnts_to_reach = None
        self._governed_bigblock = None

    def __repr__(self):
        return 'HomeSig port:{} of {}, aspect {}'.format(str(self.port_idx).rjust(2, ' '),
                                                         self.signal_point,
                                                         self.aspect)

    @property
    def bblks_to_enter(self):
        if self._bblks_to_enter is None:
            self._bblks_to_enter = [self.sigpoint.bigblock_by_port[p] for p in self.sigpoint.available_ports_by_port[self.port_idx]]
        return self._bblks_to_enter

    @property
    def ctrl_pnts_to_reach(self):
        if self._ctrl_pnts_to_reach is None:
            self._ctrl_pnts_to_reach = []
            for bblk in self.bblks_to_enter:
                for p in [bblk.L_point, bblk.R_point]:
                    if p != self.sigpoint:
                        self._ctrl_pnts_to_reach.append(p)
        return self._ctrl_pnts_to_reach

    @property
    def governed_bigblock(self):
        if self._governed_bigblock is None:
            self._governed_bigblock = self.sigpoint.bigblock_by_port.get(self.port_idx)
        return self._governed_bigblock