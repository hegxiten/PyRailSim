#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
            if len(raw_shortest) <= 2:
                return raw_shortest
            elif all([
                    True if (p1, p2, p3) not in p2.banned_paths else False 
                    for p1, p2, p3 in zip(raw_shortest[0:], raw_shortest[1:],
                                  raw_shortest[2:])
            ]):
                return raw_shortest

        return filter_banned_cp_path_shortest


@no_banned_rail_paths_on_cp
def all_simple_paths(G, source, target, cutoff=None):
    return nx.all_simple_paths(G, source, target, cutoff=None)


@no_banned_rail_paths_on_cp
def shortest_path(G, source, target, weight=None):
    return nx.shortest_path(G, source, target, weight=weight)
