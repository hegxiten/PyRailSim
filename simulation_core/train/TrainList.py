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

from collections.abc import MutableSequence

class TrainList(MutableSequence):
    """
        A list-like container for train instances within a simulation system.
        TODO: implement customized attributes of TrainList: 
            append, insert, __getitem__, __setitem__, __delitem__, etc.
    """

    def __init__(self):
        self._uptrains = []
        self._downtrains = []

    @property
    def uptrains(self):
        self._uptrains.sort()
        return self._uptrains

    @property
    def downtrains(self):
        self._downtrains.sort()
        return self._downtrains

    @property
    def all_trains(self):
        _all_trains = self.uptrains + self.downtrains
        _all_idx = [t.train_idx for t in _all_trains]
        return [t for _, t in sorted(zip(_all_idx, _all_trains))]

    @property
    def all_trains_by_MP(self):
        _all_MP = [t.curr_MP for t in self.all_trains]
        return [t for _, t in sorted(zip(_all_MP, self.all_trains))]

    def __str__(self):
        return str(self.all_trains)

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.all_trains)

    def __len__(self):
        """List length"""
        return len(self.all_trains)

    def __getitem__(self, ii):
        return self.all_trains[ii]

    def __delitem__(self, ii):
        _to_del = self.all_trains[ii]
        if _to_del in self._uptrains:
            _idx = self._uptrains.index(_to_del)
            del self._uptrains[_idx]
        if _to_del in self._downtrains:
            _idx = self._downtrains.index(_to_del)
            del self._downtrains[_idx]

    def __setitem__(self, ii, trn):
        raise Exception("Cannot Set Directly in ")

    def insert(self, trn):
        if trn.is_uptrain:
            self._uptrains.append(trn)
        if trn.is_downtrain:
            self._downtrains.append(trn)

    append = insert


