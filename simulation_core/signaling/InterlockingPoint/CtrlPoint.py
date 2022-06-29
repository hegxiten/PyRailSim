from collections import defaultdict
from itertools import permutations

from simulation_core.network.network_utils import collect_banned_paths
from simulation_core.signaling.InterlockingPoint.InterlockingPoint import InterlockingPoint
from simulation_core.signaling.Signal.HomeSignal import HomeSignal


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
        if route not in self.current_routes:
            # if not in all_valid routes, the route to open is banned
            if route not in self.all_valid_routes:
                raise Exception(
                    'illegal route for {}: banned/non-existing routes'
                    .format(self))
            elif route in self.all_valid_routes:
                # in all_valid_routes: the route to open is not banned;
                # the route-to-open is still possible to conflict with
                # existing routes
                if route not in self.current_invalid_routes:
                    self.current_routes.append(route)
                    self.set_bigblock_routing_by_CtrlPoint_route(route)
                    print('\troute {} of {} is opened'.format(route, self))
                else:
                    # try to close conflicting routes if possible
                    conflict_routes_of_route_to_open = []
                    for cr in self.current_routes:
                        if route not in self.non_mutex_routes_by_route[cr]:
                            conflict_routes_of_route_to_open.append(cr)
                    try:
                        for cr in conflict_routes_of_route_to_open:
                            self.close_route(cr)
                        self.current_routes.append(route)
                        self.set_bigblock_routing_by_CtrlPoint_route(route)
                        print('\troute {} of {} is opened'.format(route, self))
                    except:
                        print('\troute {} of {} failed to open because \
                                conflicting routes are protected')
                    finally:
                        pass
                # CtrlPoint port traffic routing: route[0] -> route[1]
                # BigBlock routing:
                #   (somewhere, someport) -> (self, route[0]) and
                #   (self, route[1]) to (somewhere, someport)

    def close_route(self, route=None):
        def close_single_route(route):
            assert route in self.current_routes
            _impacted_bblk = self.bigblock_by_port.get(route[0])
            _impacted_trns = [] if not _impacted_bblk \
                else [t for t in _impacted_bblk.trains
                      if t not in self.curr_train_with_route]
            if not _impacted_trns or \
                    all([t.curr_route_cancelable for t in _impacted_trns]):
                self.current_routes.remove(route)
                if self.bigblock_by_port.get(route[0]):
                    if not self.bigblock_by_port.get(route[0]).trains:
                        self.cancel_bigblock_routing_by_port(route[0])
                print('\troute {} of {} is closed'.format(route, self))
            else:
                raise Exception('\troute {} of {} protected: failed to close'.
                                format(route, self))

        if route:
            close_single_route(route)
        else:
            for r in self.current_routes:
                close_single_route(r)

    def find_route_for_port(self, port, dest_pointport=None):
        def candidate_ports(port, dest_pointport=None):
            if not dest_pointport:
                return [i for i in self.available_ports_by_port[port]]
            if dest_pointport:
                all_routes = self.system.dispatcher.all_routes_generator(self,
                                                                         port, dest_pointport[0], dest_pointport[1])
                _candi = []
                for r in all_routes:
                    if set(_candi) == set(self.available_ports_by_port[port]):
                        return _candi
                    if r[1][0][1] not in _candi:
                        _candi.append(r[1][0][1])
                return _candi

        _candidate_ports = candidate_ports(port, dest_pointport)
        trns = [len(self.bigblock_by_port[p].trains)
                if self.bigblock_by_port.get(p) else 0
                for p in _candidate_ports]
        final_selection = [p for p in _candidate_ports]
        for p in _candidate_ports:
            _candi_bblk = self.bigblock_by_port.get(p)
            _candi_track = self.track_by_port.get(p)
            if not _candi_bblk or not _candi_track:
                continue
            elif not _candi_bblk.routing:
                continue
            elif _candi_bblk.routing != ((self, p), (_candi_bblk.get_shooting_point(
                    point=self), _candi_bblk.get_shooting_port(port=p))):
                if _candi_bblk.trains:
                    final_selection.remove(p)
                    continue
            elif _candi_bblk.routing == ((self, p), (_candi_bblk.get_shooting_point(
                    point=self), _candi_bblk.get_shooting_port(port=p))):
                if len(_candi_bblk.trains) != min(trns):
                    final_selection.remove(p)
                    continue

        if not final_selection:
            return None
        else:
            for p in final_selection:
                if not self.bigblock_by_port.get(p): return (port, p)
                if len(self.bigblock_by_port[p].trains) == min(trns):
                    return (port, p)
            return (port, final_selection[0])

    def set_bigblock_routing_by_CtrlPoint_route(self, route):
        assert route
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
        assert port in self.ports
        _port, _bblk = port, self.bigblock_by_port.get(port)
        if _bblk:
            _bblk.routing = None

    def opposite_port(self, port):
        assert port in self.ports
        assert len(self.ports) == 2
        for p in self.ports:
            if p != port:
                return p
