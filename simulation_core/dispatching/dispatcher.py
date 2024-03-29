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
from simulation_core.train.train import Train
from simulation_test.simulation_helpers import timestamper


class Dispatcher():
    @staticmethod
    def cp_port_leading_to(autopoint, port):
        assert autopoint.__class__.__name__ == 'AutoPoint'
        if autopoint.signal_by_port[port].upwards:
            return autopoint.group_block.node1, autopoint.group_block.node1_port
        if autopoint.signal_by_port[port].downwards:
            return autopoint.group_block.node2, autopoint.group_block.node2_port

    def __init__(self, network):
        self.network = network
        setattr(self.network, 'dispatcher', self)

    def routing_requestable(self, init_node, dest_node):
        """
            Determines if a train could currently request routing from init_node towards dest_node.
            @return: bool
            TODO: this case now return True for all scenarios because the simulation is uni-directional.
        """
        _parallel_routing_static = len(
            list(all_simple_paths(self.network.G_origin, source=init_node, target=dest_node)))
        _outbound_trains = self.network.get_trains_between_points(from_point=init_node, to_point=dest_node, obv=True)
        _inbound_trains = self.network.get_trains_between_points(from_point=dest_node, to_point=init_node, obv=True)
        _occupied_parallel_tracks = self.network.num_occupied_parallel_tracks(init_node, dest_node)
        if min(len(_outbound_trains), len(_inbound_trains)) <= _parallel_routing_static - _occupied_parallel_tracks:
            return True
        return False

    def generate_train(self, init_node, init_port, dest_node, dest_port, **kwargs):
        """
            Generate train only.
        """
        _new_train = None
        if self.routing_requestable(init_node, dest_node):
            init_segment = ((None, None), (init_node, init_port)) \
                if not init_node.track_by_port.get(init_port) \
                else ((init_node.track_by_port[init_port]
                       .get_shooting_node(node=init_node),
                       init_node.track_by_port[init_port]
                       .get_shooting_port(node=init_node)),
                      (init_node, init_port))
            dest_segment = ((dest_node, dest_port), (None, None)) \
                if not dest_node.track_by_port.get(dest_port) \
                else ((dest_node.track_by_port[dest_port]
                       .get_shooting_node(node=dest_node),
                       dest_node.track_by_port[dest_port]
                       .get_shooting_port(node=dest_node)),
                      (dest_node, dest_port))
            init_track = self.network.get_track_by_node_port_pairs(
                init_segment[0][0], init_segment[0][1],
                init_segment[1][0], init_segment[1][1]
            )
            _new_train = Train(
                network=self.network,
                init_segment=init_segment,
                dest_segment=dest_segment,
                max_spd=kwargs.get('max_spd', random.choice(self.network.spd_container)),
                max_acc=kwargs.get('max_acc', random.choice(self.network.acc_container)),
                max_dcc=kwargs.get('max_dcc', random.choice(self.network.dcc_container)),
                length=kwargs.get('length', 1))
            if not init_track:
                print("{0} [INFO]: new train generated WITHOUT init track.".format(timestamper(self.network.sys_time)))
                return _new_train
            # TODO: The logics below are not in use - trains are currently all generated from network vertices.
            elif init_track.is_occupied:
                print('{0} [WARNING]: cannot generate train: track is occupied. Hold new train for track availability.'.format(timestamper(self.network.sys_time)))
            elif not init_track.routing:
                print('{0} [INFO]: -------------NOT INIT ROUTING-------------'.format(timestamper(self.network.sys_time)))
                return _new_train
            elif Train.directional_sign(init_segment) == init_track.sign_routing(init_track.routing):
                print('{0} [INFO]: -------------INIT SEGMENT SIGN CONFORMS-------------'.format(timestamper(self.network.sys_time)))
                return _new_train
        return _new_train

    def request_routing(self, train):
        """
            Method of the train to call the closest CtrlPoint to clear a route.
            Serve the myopic dispatch logic where trains only calls the cloest CPs.
            @return: None
        """
        if train.is_waiting_route_at_curr_cp and self.determine_paths_enterable_ahead_train(train):
            _pending_route_to_open = train.curr_ctrl_point.find_route_for_port(port=train.curr_ctrl_point_port, dest_node_port=train.dest_node_port)
            if _pending_route_to_open is None:
                return None
            if _pending_route_to_open not in train.curr_ctrl_point.curr_invalid_routes_set:
                if not train.curr_track or not train.curr_track.yard:
                    print('{0} [INFO]: {1}, \n\trequested {2} at {3}'
                          .format(timestamper(self.network.sys_time), train, _pending_route_to_open,
                                  train.curr_ctrl_point.MP))
                    train.curr_ctrl_point.open_route(_pending_route_to_open)
                    return _pending_route_to_open
                elif train.curr_track.yard:
                    if not self.determine_if_hold_to_be_passed(train, max_passes=1):
                        print('{0} [INFO]: {1}, \n\trequested {2} at {3}'
                              .format(timestamper(self.network.sys_time), train, _pending_route_to_open,
                                      train.curr_ctrl_point.MP))
                        train.curr_ctrl_point.open_route(_pending_route_to_open)
                        return _pending_route_to_open
                    else:
                        for cp in self.network.ctrl_points:
                            for (entry_port, exit_port) in cp.curr_routes_set:
                                if cp.group_block_by_port.get(exit_port):
                                    if train in cp.group_block_by_port[exit_port].trains:
                                        _route_to_change = cp.find_route_for_port(port=entry_port, dest_node_port=train.dest_node_port)
                                        cp.open_route(_route_to_change)
                                        return _pending_route_to_open
        return None

    def determine_paths_enterable_ahead_train(self, train):
        for p in train.all_paths_ahead:
            if all([True if self.routing_requestable(train.curr_ctrl_point, n) else False for n in p]):
                return True
        return False

    def determine_if_hold_to_be_passed(self, train, max_passes=1):
        '''
            determine if the train is slower than the one behind and needs to be
            put on the siding to let the follower pass it.
            Rank minus initial index is the number of trains have passed it.
            @return: True or False
            TODO: implement better judgment to consider more conditions, such as
                priority, proximity (to the follower), etc.
        '''
        # the last train is not passable by any train
        if train.rank == len(train.same_way_trains) - 1:
            return False
        # for any train that is not the last one:
        if not train.curr_track or not train.rear_curr_track:
            return False  # not passable when not fully entered yet
        if not (train.max_spd < train.trn_follow_behind.max_spd):
            return False  # not passable if not slower than the one behind
        if train.rank - train.train_idx >= max_passes:  # TODO: This logic is naive
            return False  # not passable if has already been passed by once
        if train.curr_track.yard:
            _all_trains = train.curr_track.yard.all_trains
            _rest_trains = [t for t in _all_trains if t != train]
            if train.stopped and any([not t.stopped for t in _rest_trains]):
                return True  # during the pass, hold the stopped train from move
            if all([trk.trains for trk in train.curr_track.yard.tracks]):
                if abs(train.max_spd) == min([abs(trn.max_spd) for trn in train.curr_track.yard.all_trains]):
                    return True
            if train.curr_track.yard.available_tracks >= 1 and train.dist_to_trn_behind <= 10:  # TODO: explain this??????
                return True
        return False

    def get_routing_path(self, src=None, srcport=None, tgt=None, tgtport=None, path=None, mainline=True):
        if src == tgt == path == None:
            raise Exception("Need to specify either a path or pair of points!")
        if src.__class__.__name__ == 'AutoPoint':
            src, srcport = self.cp_port_leading_to(src, srcport)
        if tgt.__class__.__name__ == 'AutoPoint':
            tgt, tgtport = self.cp_port_leading_to(tgt, tgtport)
        routing_path = []
        cp_path = path
        lambda_get_port_by_grpblk_and_cp = lambda grpblk, cp: [p for p in cp.ports if cp.group_block_by_port.get(p) == grpblk][0]
        for cp1, cp2 in zip(cp_path[0:], cp_path[1:]):
            _parallel_grpblks = [self.network.G_skeleton[cp1][cp2][k]['instance'] for k in self.network.G_skeleton[cp1][cp2].keys()]
            selected_grpblk = min(_parallel_grpblks) if mainline else max(_parallel_grpblks)
            rp_seg = ((cp1, lambda_get_port_by_grpblk_and_cp(selected_grpblk, cp1)),
                      (cp2, lambda_get_port_by_grpblk_and_cp(selected_grpblk, cp2)))
            routing_path.append(rp_seg)
        if not src.group_block_by_port.get(srcport):
            routing_path.insert(0, ((None, None), (src, srcport)))
        if src.group_block_by_port.get(srcport):
            init_grpblk = src.group_block_by_port.get(srcport)
            _p = init_grpblk.get_shooting_node(node=src, port=srcport)
            _port = init_grpblk.get_shooting_port(node=src, port=srcport)
            routing_path.insert(0, ((_p, _port), (src, srcport)))
        if not tgt.group_block_by_port.get(tgtport):
            routing_path.append(((tgt, tgtport), (None, None)))
        if tgt.group_block_by_port.get(tgtport):
            final_grpblk = tgt.group_block_by_port.get(tgtport)
            _p = final_grpblk.get_shooting_node(node=tgt, port=tgtport)
            _port = final_grpblk.get_shooting_port(node=tgt, port=tgtport)
            routing_path.append(((tgt, tgtport), (_p, _port)))
        return routing_path

    def all_routing_paths_generator(self, src, srcport, tgt, tgtport, mainline):
        src, srcport, tgt, tgtport = src, srcport, tgt, tgtport
        if src.__class__.__name__ == 'AutoPoint':
            src, srcport = self.cp_port_leading_to(src, srcport)
        if tgt.__class__.__name__ == 'AutoPoint':
            tgt, tgtport = self.cp_port_leading_to(tgt, tgtport)
        cp_paths = list(all_simple_paths(self.network.G_skeleton, source=src, target=tgt))
        _routing_path_list = []
        while cp_paths:
            _single_cp_route = cp_paths[0]
            _single_routing_path = self.get_routing_path(src, srcport, tgt, tgtport, path=_single_cp_route, mainline=mainline)
            cp_paths.pop(0)
            _routing_path_list.append(_single_routing_path)
            yield _single_routing_path

    def get_all_routes(self, src, srcport, tgt, tgtport):
        return list(self.all_routing_paths_generator(src, srcport, tgt, tgtport))

    """
        Deprecated or placeholder below
    """

    def update_routing(self):
        """
            TODO: Combine dispatcher actions
        """
        for trn in self.network.train_list.all_trains:
            if not trn.curr_sig:
                pass
            elif not trn.curr_sig.route:
                if self.routing_requestable(trn.curr_node, trn.intended_sigpoint):
                    trn.curr_node.open_route((trn.curr_port, trn.intended_sigport))

    def cp_segment_to_node(self, cp_seg):
        cp1, prt1, cp2, prt2 = cp_seg[0][0], cp_seg[0][1], cp_seg[1][0], cp_seg[1][1]
        assert cp1.__class__.__name__ == cp2.__class__.__name__ == 'CtrlPoint'

    def get_path(self, route, raw=True):
        assert len(route) >= 2
        cp_path = [rp_seg[0][0] for rp_seg in route[1:]]
        if raw is False:
            return cp_path
        if raw is True:
            pass

    def max_MA_limit(self, route):
        pass

    def conflicts(self):
        pass

    def grant(self, trn):
        pass

    def revoke(self, trn):
        pass
