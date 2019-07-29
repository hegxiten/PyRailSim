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
import os
import random
import sys

sys.path.append(
    'D:\\Users\\Hegxiten\\workspace\\Rutgers_Railway_security_research\\OOD_Train'
)

from functools import wraps

import networkx as nx


def no_banned_rail_paths_on_cp(func):

    if func.__name__ == 'all_simple_paths':

        @wraps(func)
        def filter_banned_paths_all(G, source, target, cutoff=None):
            if source == target:
                yield [source]
            raw_simple_path_gen = func(G, source, target, cutoff=None)
            for path in raw_simple_path_gen:
                if len(path) <= 2:
                    yield path
                elif all([
                        True if (p1, p2, p3) not in p2.banned_paths else False
                        for p1, p2, p3 in zip(path[0:], path[1:], path[2:])
                ]):
                    yield path

        return filter_banned_paths_all

    if func.__name__ == 'shortest_path':

        @wraps(func)
        def filter_banned_cp_path_shortest(G, source, target, weight=None):
            raw_shortest = func(G, source, target, weight=weight)
            while True:
                if len(list(all_simple_paths(G, source, target))) == 1:
                    return raw_shortest
                elif len(raw_shortest) <= 2:
                    return raw_shortest
                elif all([
                        True if (p1, p2, p3) not in p2.banned_paths else False 
                        for p1, p2, p3 in zip(raw_shortest[0:], raw_shortest[1:],
                                    raw_shortest[2:])
                        ]):
                    return raw_shortest
                else:
                    if raw_shortest != func(G, source, target):
                        raw_shortest = func(G, source, target)
                    else:
                        raise Exception("Cannot Find a shortest Path Between \
                                        {} and {}!".format(source, target))
            
        return filter_banned_cp_path_shortest


@no_banned_rail_paths_on_cp
def all_simple_paths(G, source, target, cutoff=None):
    return nx.all_simple_paths(G, source, target, cutoff=None)

@no_banned_rail_paths_on_cp
def shortest_path(G, source, target, weight=None):
    return nx.shortest_path(G, source, target, weight=weight)
