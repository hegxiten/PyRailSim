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

from functools import wraps
import networkx as nx


def no_banned_rail_paths_on_cp(func):

    if func.__name__ == 'all_simple_paths':
        '''
        Parameters
        ----------
        G : NetworkX graph

        source : node
            Starting node for path

        target : node
            Ending node for path

        cutoff : integer, optional
            Depth to stop the search. Only paths of length <= cutoff are returned.

        Returns
        -------
        path_generator: generator
            A generator that produces lists of simple paths.  If there are no paths
            between the source and target within the given cutoff the generator
            produces no output.
        '''

        @wraps(func)
        def filter_out_banned_paths(G, source, target, cutoff=None):
            '''
                Filter out the simple paths that contain banned paths inside control points (CPs)
            '''
            if source == target:
                yield [source]
            raw_simple_path_gen = func(G, source, target, cutoff=None) # Calling the wrapped function
            for path in raw_simple_path_gen:
                if len(path) <= 2:
                    yield path
                elif all([
                        True if (p0, p1, p2) not in p1.banned_paths \
                            else False \
                            for p0, p1, p2 in zip(path[0:], path[1:], path[2:])
                        ]):
                    yield path
        return filter_out_banned_paths

    if func.__name__ == 'shortest_path':
        '''
        Compute shortest paths in the graph.

        Parameters
        ----------
        G : NetworkX graph

        source : node, optional
            Starting node for path. If not specified, compute shortest
            paths for each possible starting node.

        target : node, optional
            Ending node for path. If not specified, compute shortest
            paths to all possible nodes.

        weight : None, string or function, optional (default = None)
            If None, every edge has weight/distance/cost 1.
            If a string, use this edge attribute as the edge weight.
            Any edge attribute not present defaults to 1.
            If this is a function, the weight of an edge is the value
            returned by the function. The function must accept exactly
            three positional arguments: the two endpoints of an edge and
            the dictionary of edge attributes for that edge.
            The function must return a number.

        method : string, optional (default = 'dijkstra')
            The algorithm to use to compute the path.
            Supported options: 'dijkstra', 'bellman-ford'.
            Other inputs produce a ValueError.
            If `weight` is None, unweighted graph methods are used, and this
            suggestion is ignored.

        Returns
        ------
        path: list or dictionary
            All returned paths include both the source and target in the path.

            If the source and target are both specified, return a single list
            of nodes in a shortest path from the source to the target.

            If only the source is specified, return a dictionary keyed by
            targets with a list of nodes in a shortest path from the source
            to one of the targets.

            If only the target is specified, return a dictionary keyed by
            sources with a list of nodes in a shortest path from one of the
            sources to the target.

            If neither the source nor target are specified return a dictionary
            of dictionaries with path[source][target]=[list of nodes in path].
        '''

        @wraps(func)
        def filter_banned_cp_path_shortest(G, source, target, weight=None):
            '''
                Find the shortest path that also allowed by individual control points (CPs)
                (Not in the banned list of any CPs)
            '''
            raw_shortest = func(G, source, target, weight=weight) # Calling the wrapped function
            if len(list(all_simple_paths(G, source, target, cutoff=None))) == 1:
                return raw_shortest
            elif len(raw_shortest) <= 2:
                return raw_shortest
            elif all([
                    True if (p0, p1, p2) not in p1.banned_paths else False 
                    for p0, p1, p2 in zip(raw_shortest[0:], raw_shortest[1:],
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
    return nx.all_simple_paths(G, source, target, cutoff=cutoff)

@no_banned_rail_paths_on_cp
def shortest_path(G, source, target, weight=None):
    return nx.shortest_path(G, source, target, weight=weight)
