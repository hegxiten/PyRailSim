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


class AutoSignal(Signal):
    '''
    Automatic Blocking Signal object, inherited from Signal.
    Serve as the intermediate signals within a BigBlock that governs individual track segments.
    Used for single directional traffic control only.
    Not used for granting movement authorities.
    '''

    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__(port_idx, sigpoint, MP)
        self.type = 'auto'

        self._bblks_to_enter = None
        self._ctrl_pnts_to_reach = None

    def __repr__(self):
        return 'AutoSig port:{} of {}'.format(
            str(self.port_idx).rjust(2, ' '),
            self.sigpoint)

    @property
    def bblks_to_enter(self):
        if self._bblks_to_enter is None:
            self._bblks_to_enter = [self.sigpoint.bigblock]
        return self._bblks_to_enter

    @property
    def ctrl_pnts_to_reach(self):
        if self._ctrl_pnts_to_reach is None:
            if self.downwards:
                self._ctrl_pnts_to_reach = [self.sigpoint.bigblock.R_point]
            elif self.upwards:
                self._ctrl_pnts_to_reach = [self.sigpoint.bigblock.L_point]
            else:
                raise Exception("Cannot specify the signal milepost direction: \n\t{}".format(self.__repr__))
        return self._ctrl_pnts_to_reach