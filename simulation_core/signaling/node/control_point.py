from collections import defaultdict
from itertools import permutations

from simulation_core.network.network_utils import collect_banned_paths
from simulation_core.signaling.node.base_node import BaseNode
from simulation_core.signaling.signal.home_signal import HomeSignal
from simulation_test.simulation_helpers import timestamper


class CtrlPoint(BaseNode):

    def __init__(self,
                 network,
                 uuid,
                 ports,
                 MP=None,
                 banned_ports_by_port=defaultdict(set),
                 non_mutex_routes_set_by_route=defaultdict(set)):
        super().__init__(network, uuid, MP)
        self.type = 'cp'
        self._ports = ports
        self.banned_ports_by_port = banned_ports_by_port
        self._non_mutex_routes_set_by_route = non_mutex_routes_set_by_route
        self._curr_routes_set = set()
        self.group_block_by_port = {}
        self._banned_paths_set = None
        self._available_ports_by_port = None  # available options for routes, dict[port] = list(options)
        # build up signals
        self.signal_by_port = {}
        for i in self.ports:
            self.signal_by_port[i] = HomeSignal(i, self, MP)
        # add the ownership of signals
        for _, sig in self.signal_by_port.items():
            sig.node = self
            sig.network = self.network

    def __repr__(self):
        return 'CtrlPnt{}'.format(str(self.uuid).rjust(2, ' '), )

    @property
    def banned_ports_by_port(self):
        return self._banned_ports_by_port

    @banned_ports_by_port.setter
    def banned_ports_by_port(self, val):
        self._banned_ports_by_port = val

    @property
    def ports(self):
        return self._ports

    @property
    def is_vertex(self) -> bool:
        """
            Property of a Control Point: if it is a vertex (initiating node) of a network
            @return: True/False
        """
        for i in self.ports:
            if not self.track_by_port.get(i):
                return True
        return False

    @property
    def non_mutex_routes_set_by_route(self):
        return self._non_mutex_routes_set_by_route

    @property
    def all_valid_routes_set(self):
        # available options for routes, list of routes
        _all_valid_routes_set = set()
        for port_0, ports in self.available_ports_by_port.items():
            for port_1 in ports:
                _all_valid_routes_set.add((port_0, port_1))
                _all_valid_routes_set.add((port_1, port_0))
        return _all_valid_routes_set

    @property
    def curr_routes_set(self):
        for r1, r2 in permutations(self._curr_routes_set, 2):
            assert r1 not in self.mutex_routes_by_route[r2]
            assert r2 not in self.mutex_routes_by_route[r1]
            assert r1[1] not in self.banned_ports_by_port[r1[0]]
            assert r2[1] not in self.banned_ports_by_port[r2[0]]
        return self._curr_routes_set

    @curr_routes_set.setter
    def curr_routes(self, new_routes_set):
        assert isinstance(new_routes_set, set)
        for i in new_routes_set:
            assert i in self.all_valid_routes_set
        self._curr_routes_set = new_routes_set

    @property
    def banned_paths_set(self):
        """
            The banned paths for each control node in a 3-element tuple
            (init_node, self, ending_node)
            @return:
                tuple
        """
        if self._banned_paths_set is None:
            self._banned_paths_set = set(
                collect_banned_paths(self, skeleton=False) + collect_banned_paths(self, skeleton=True))
        return self._banned_paths_set

    @property
    def available_ports_by_port(self):
        """
            Define legal routes
            @return:
                dictionary of {port: [ports]}
        """
        if self._available_ports_by_port is None:
            self._available_ports_by_port = defaultdict(set)
            for i in self.ports:
                for j in self.ports:
                    if j not in self.banned_ports_by_port.get(i, set()):
                        self._available_ports_by_port[i].add(j)
        return self._available_ports_by_port

    def open_route(self, route):
        # CtrlPoint port traffic routing: route[0] -> route[1]
        # GroupBlock routing:
        #   (somewhere, someport) -> (self, route[0]) and
        #   (self, route[1]) to (somewhere, someport)
        if route in self.curr_routes_set:
            return
        # if not in all_valid routes, the route to open is banned
        if route not in self.all_valid_routes_set:
            raise Exception('illegal route for {}: banned/non-existing routes'.format(self))
        # in all_valid_routes_set: the route to open is not banned;
        # the route-to-open is still possible to conflict with existing routes
        if route in self.curr_invalid_routes_set:
            conflicting_routes = set()
            for curr_rte in self.curr_routes_set:
                if route not in self.non_mutex_routes_set_by_route[curr_rte]:
                    conflicting_routes.add(curr_rte)
            for r in conflicting_routes:
                self.close_route(r)
        self.curr_routes_set.add(route)
        self.set_grpblk_routing_by_ctrlpnt_route(route)
        print('{0} [INFO]: route {1} of {2} is opened'.format(timestamper(self.network.sys_time), route, self))

    def close_route(self, route=None):
        def close_single_route(route):
            assert route in self.curr_routes_set
            entry_port = route[0]
            _impacted_grpblk = self.group_block_by_port.get(entry_port)
            _impacted_trns = []
            if _impacted_grpblk:
                for trn in _impacted_grpblk.trains:
                    if trn not in self.curr_train_with_route:
                        _impacted_trns.append(trn)
            if not _impacted_trns or all([trn.curr_route_cancelable for trn in _impacted_trns]):
                self.curr_routes_set.remove(route)
                if _impacted_grpblk:
                    if not _impacted_grpblk.trains:
                        self.cancel_grpblk_routing_by_port(entry_port)
                print('{0} [INFO]: route {1} of {2} is closed'.format(timestamper(self.network.sys_time), route, self))
            # TODO: groom the logics below. Relating to the problem of closing a route of control node in front of approaching trains.
            # else:
            #     raise Exception('\troute {} of {} protected: failed to close'.format(route, self))

        if route:
            close_single_route(route)
        else:
            for r in self.curr_routes_set:
                close_single_route(r)

    def find_route_for_port(self, port, dest_node_port=None):
        mainline_routing_paths = list(
            self.network.dispatcher.all_routing_paths_generator(self, port, dest_node_port[0], dest_node_port[1],
                                                                mainline=True))
        siding_routing_paths = list(
            self.network.dispatcher.all_routing_paths_generator(self, port, dest_node_port[0], dest_node_port[1],
                                                                mainline=False))

        all_routing_paths = mainline_routing_paths + siding_routing_paths
        _candidate_ports = list(set([rp[1][0][1] for rp in all_routing_paths]))
        _trn_number_in_grpblks = [len(self.group_block_by_port[p].trains) if self.group_block_by_port.get(p) else 0 for
                                  p in _candidate_ports]
        final_selection = [p for p in _candidate_ports]
        for p in _candidate_ports:
            _candidate_grpblk = self.group_block_by_port.get(p)
            _candidate_track = self.track_by_port.get(p)
            if not _candidate_grpblk or not _candidate_track:
                continue
            elif not _candidate_grpblk.routing:
                continue
            if _candidate_grpblk.routing != (
                    (self, p),
                    (_candidate_grpblk.get_shooting_node(node=self), _candidate_grpblk.get_shooting_port(port=p))
            ):
                if _candidate_grpblk.trains:
                    final_selection.remove(p)
                    continue
            else:
                if len(_candidate_grpblk.trains) != min(_trn_number_in_grpblks):
                    final_selection.remove(p)
                    continue
        if not final_selection:
            return None
        for p in final_selection:
            if not self.group_block_by_port.get(p):
                return (port, p)
            if len(self.group_block_by_port[p].trains) == min(_trn_number_in_grpblks):
                return (port, p)
        return (port, final_selection[0])

    def set_grpblk_routing_by_ctrlpnt_route(self, route):
        (x, y) = route
        _in_port, _in_grpblk = x, self.group_block_by_port.get(x)
        _out_port, _out_grpblk = y, self.group_block_by_port.get(y)
        if _in_grpblk and _out_grpblk:
            _in_grpblk.routing = ((_in_grpblk.get_shooting_node(node=self),
                                   _in_grpblk.get_shooting_port(node=self)), (self, x))
            _out_grpblk.routing = ((self, y),
                                   (_out_grpblk.get_shooting_node(node=self),
                                    _out_grpblk.get_shooting_port(node=self)))

        elif (not _in_grpblk) and _out_grpblk:
            _out_grpblk.routing = ((self, y),
                                   (_out_grpblk.get_shooting_node(node=self),
                                    _out_grpblk.get_shooting_port(node=self)))
        elif _in_grpblk and (not _out_grpblk):
            _in_grpblk.routing = ((_in_grpblk.get_shooting_node(node=self),
                                   _in_grpblk.get_shooting_port(node=self)), (self, x))

    def cancel_grpblk_routing_by_port(self, port):
        _grpblk = self.group_block_by_port.get(port)
        if _grpblk:
            _grpblk.routing = None

    def opposite_port(self, port):
        assert port in self.ports
        assert len(self.ports) == 2
        for p in self.ports:
            if p != port:
                return p
