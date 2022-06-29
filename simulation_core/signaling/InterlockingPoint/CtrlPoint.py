from collections import defaultdict
from itertools import permutations

from simulation_core.network.network_utils import collect_banned_paths
from simulation_core.signaling.InterlockingPoint.InterlockingPoint import InterlockingPoint
from simulation_core.signaling.Signal.HomeSignal import HomeSignal
from simulation_test.sim import timestamper


class CtrlPoint(InterlockingPoint):

    def __init__(self,
                 system,
                 idx,
                 ports,
                 MP=None,
                 banned_ports_by_port=defaultdict(list),
                 non_mutex_routes_by_route=defaultdict(list)):
        super().__init__(system, idx, MP)
        self.type = 'cp'
        self._ports = ports
        self.banned_ports_by_port = banned_ports_by_port
        self._non_mutex_routes_by_route = non_mutex_routes_by_route
        self._current_routes = []
        self.bigblock_by_port = {}
        self._banned_paths = None
        self._available_ports_by_port = None  # available options for routes, dict[port] = list(options)
        # build up signals
        self.signal_by_port = {}
        for i in self.ports:
            self.signal_by_port[i] = HomeSignal(i, self, MP)
        # add the ownership of signals
        for _, sig in self.signal_by_port.items():
            sig.sigpoint = self
            sig.system = self.system

    def __repr__(self):
        return 'CtrlPnt{}'.format(
            str(self.idx).rjust(2, ' '), )

    @property
    def banned_ports_by_port(self) -> dict:
        return self._banned_ports_by_port

    @banned_ports_by_port.setter
    def banned_ports_by_port(self, val) -> dict:
        self._banned_ports_by_port = val

    @property
    def ports(self):
        return self._ports

    @property
    def is_vertex(self) -> bool:
        """
            Property of a Control Point: if it is a vertex (initiating point) of a network
            @return: True/False
        """
        for i in self.ports:
            if not self.track_by_port.get(i):
                return True
        return False

    @property
    def non_mutex_routes_by_route(self):
        return self._non_mutex_routes_by_route

    @property
    def all_valid_routes(self):
        # available options for routes, list of routes
        _all_valid_routes = set()
        for p, plist in self.available_ports_by_port.items():
            for rp in plist:
                _all_valid_routes.add((p, rp))
                _all_valid_routes.add((rp, p))
        return list(_all_valid_routes)

    @property
    def current_routes(self):
        for r1, r2 in permutations(self._current_routes, 2):
            assert r1 not in self.mutex_routes_by_route[r2]
            assert r2 not in self.mutex_routes_by_route[r1]
            assert r1[1] not in self.banned_ports_by_port[r1[0]]
            assert r2[1] not in self.banned_ports_by_port[r2[0]]
        return self._current_routes

    @current_routes.setter
    def current_routes(self, new_route_list):
        assert isinstance(new_route_list, list)
        for i in new_route_list:
            assert i in self.all_valid_routes
        self._current_routes = new_route_list

    @property
    def banned_paths(self):
        """
            The banned paths for each control point in a 3-element tuple
            (init_point, self, ending_point)
            @return:
                tuple
        """
        if self._banned_paths is None:
            self._banned_paths = list(set(collect_banned_paths(self, skeleton=False) + collect_banned_paths(self, skeleton=True)))
        return self._banned_paths

    @property
    def available_ports_by_port(self):
        """
            Define legal routes
            @return:
                dictionary of {port: [ports]}
        """
        if self._available_ports_by_port is None:
            self._available_ports_by_port = defaultdict(list)
            for i in self.ports:
                for j in self.ports:
                    if j not in self.banned_ports_by_port.get(i, []):
                        self._available_ports_by_port[i].append(j)
        return self._available_ports_by_port

    def open_route(self, route):
        # CtrlPoint port traffic routing: route[0] -> route[1]
        # BigBlock routing:
        #   (somewhere, someport) -> (self, route[0]) and
        #   (self, route[1]) to (somewhere, someport)
        if route in self.current_routes:
            return
        # if not in all_valid routes, the route to open is banned
        if route not in self.all_valid_routes:
            raise Exception('illegal route for {}: banned/non-existing routes'.format(self))
        # in all_valid_routes: the route to open is not banned;
        # the route-to-open is still possible to conflict with existing routes
        if route in self.current_invalid_routes:
            conflicting_routes = []
            for curr_rte in self.current_routes:
                if route not in self.non_mutex_routes_by_route[curr_rte]:
                    conflicting_routes.append(curr_rte)
            for r in conflicting_routes:
                self.close_route(r)
        self.current_routes.append(route)
        self.set_bigblock_routing_by_CtrlPoint_route(route)
        print('{0} [INFO]: route {1} of {2} is opened'.format(timestamper(self.system.sys_time), route, self))

    def close_route(self, route=None):
        def close_single_route(route):
            assert route in self.current_routes
            entry_port = route[0]
            _impacted_bblk = self.bigblock_by_port.get(entry_port)
            _impacted_trns = []
            if _impacted_bblk:
                for trn in _impacted_bblk.trains:
                    if trn not in self.curr_train_with_route:
                        _impacted_trns.append(trn)
            if not _impacted_trns or all([trn.curr_route_cancelable for trn in _impacted_trns]):
                self.current_routes.remove(route)
                if _impacted_bblk:
                    if not _impacted_bblk.trains:
                        self.cancel_bigblock_routing_by_port(entry_port)
                print('{0} [INFO]: route {1} of {2} is closed'.format(timestamper(self.system.sys_time), route, self))
            else:
                raise Exception('\troute {} of {} protected: failed to close'.
                                format(route, self))
        if route:
            close_single_route(route)
        else:
            for r in self.current_routes:
                close_single_route(r)

    def find_route_for_port(self, port, dest_pointport=None):
        mainline_routing_paths = list(self.system.dispatcher.all_routing_paths_generator(self, port, dest_pointport[0], dest_pointport[1], mainline=True))
        siding_routing_paths = list(self.system.dispatcher.all_routing_paths_generator(self, port, dest_pointport[0], dest_pointport[1], mainline=False))

        all_routing_paths = mainline_routing_paths + siding_routing_paths
        _candidate_ports = list(set([rp[1][0][1] for rp in all_routing_paths]))
        _trn_number_in_bblks = [len(self.bigblock_by_port[p].trains) if self.bigblock_by_port.get(p) else 0 for p in _candidate_ports]
        final_selection = [p for p in _candidate_ports]
        for p in _candidate_ports:
            _candi_bblk = self.bigblock_by_port.get(p)
            _candi_track = self.track_by_port.get(p)
            if not _candi_bblk or not _candi_track:
                continue
            elif not _candi_bblk.routing:
                continue
            if _candi_bblk.routing != ((self, p), (_candi_bblk.get_shooting_point(point=self), _candi_bblk.get_shooting_port(port=p))):
                if _candi_bblk.trains:
                    final_selection.remove(p)
                    continue
            else:
                if len(_candi_bblk.trains) != min(_trn_number_in_bblks):
                    final_selection.remove(p)
                    continue
        if not final_selection:
            return None
        for p in final_selection:
            if not self.bigblock_by_port.get(p):
                return (port, p)
            if len(self.bigblock_by_port[p].trains) == min(_trn_number_in_bblks):
                return (port, p)
        return (port, final_selection[0])

    def set_bigblock_routing_by_CtrlPoint_route(self, route):
        (x, y) = route
        _in_port, _in_bblk = x, self.bigblock_by_port.get(x)
        _out_port, _out_bblk = y, self.bigblock_by_port.get(y)
        if _in_bblk and _out_bblk:
            _in_bblk.routing = ((_in_bblk.get_shooting_point(point=self),
                                 _in_bblk.get_shooting_port(point=self)), (self, x))
            _out_bblk.routing = ((self, y),
                                 (_out_bblk.get_shooting_point(point=self),
                                  _out_bblk.get_shooting_port(point=self)))

        elif (not _in_bblk) and _out_bblk:
            _out_bblk.routing = ((self, y),
                                 (_out_bblk.get_shooting_point(point=self),
                                  _out_bblk.get_shooting_port(point=self)))
        elif _in_bblk and (not _out_bblk):
            _in_bblk.routing = ((_in_bblk.get_shooting_point(point=self),
                                 _in_bblk.get_shooting_port(point=self)), (self, x))

    def cancel_bigblock_routing_by_port(self, port):
        _bblk = self.bigblock_by_port.get(port)
        if _bblk:
            _bblk.routing = None

    def opposite_port(self, port):
        assert port in self.ports
        assert len(self.ports) == 2
        for p in self.ports:
            if p != port:
                return p
