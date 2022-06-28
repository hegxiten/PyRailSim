from abc import ABC, abstractmethod
from collections import defaultdict

from simulation_core.observation_model.observe import Observable, Observer


class InterlockingPoint(Observable, Observer, ABC):
    """
        Base Class, a.k.a SignalPoint/Sigpoint
    """

    def __init__(self, system, idx, MP=None):
        super().__init__()
        self._system = system
        self._MP = MP
        self._idx = idx
        self._ports = []

        self._non_mutex_routes_by_route = None
        self._mutex_routes_by_route = None
        self._banned_ports_by_port = defaultdict(list)

        self.neighbor_nodes = []
        self.track_by_port = {}

        self._current_routes = []
        self._curr_train_with_route = {}

    @property
    @abstractmethod
    def available_ports_by_port(self) -> dict:
        pass

    @property
    @abstractmethod
    def all_valid_routes(self) -> list:
        pass

    @property
    @abstractmethod
    def current_routes(self) -> list:
        pass

    @property
    @abstractmethod
    def non_mutex_routes_by_route(self) -> dict:
        pass

    @property
    def system(self):
        return self._system

    @property
    def ports(self):
        return self._ports

    @property
    def MP(self):
        return self._MP

    @property
    def idx(self):
        return self._idx

    @property
    def non_mutex_routes_by_route(self):
        return self._non_mutex_routes_by_route

    @property
    def mutex_routes_by_route(self):
        return self._mutex_routes_by_route

    @property
    @abstractmethod
    def banned_ports_by_port(self) -> dict:
        return self._banned_ports_by_port

    @property
    def mutex_routes_by_route(self):
        if self._mutex_routes_by_route is None:
            self._mutex_routes_by_route = defaultdict(list)
            for valid_route in self.all_valid_routes:
                _all_valid_routes = self.all_valid_routes.copy()
                _all_valid_routes.remove(valid_route)
                self._mutex_routes_by_route[valid_route].extend(_all_valid_routes)
            for route, non_mutex_route_list in self.non_mutex_routes_by_route.items():
                if non_mutex_route_list in self._mutex_routes_by_route[route]:
                    self._mutex_routes_by_route[route].remove(non_mutex_route_list)
        return self._mutex_routes_by_route

    @property
    def current_route_by_port(self):
        _current_route_by_port = {}
        for r in self.current_routes:
            _current_route_by_port[r[0]] = r
        return _current_route_by_port

    @property
    def curr_train_with_route(self):
        return self._curr_train_with_route

    @property
    def current_invalid_routes(self):
        # General cases. For simplifcation, better be overriden
        _current_invalid_routes = set()
        # collect all banned routes in a permutation list of 2-element tuples
        for p, bplist in self.banned_ports_by_port.items():
            for bp in bplist:
                _current_invalid_routes.add((p, bp))
                _current_invalid_routes.add((bp, p))
        # collect all mutex routes according to currently openned routes
        for r in self.current_routes:
            for vr in self.all_valid_routes:
                if vr not in self.non_mutex_routes_by_route[r]:
                    _current_invalid_routes.add(vr)
        # collect all routes currently under trains
        for r in self.locked_routes_due_to_train:
            _current_invalid_routes.add(r)
        return list(_current_invalid_routes)

    @property
    def locked_routes_due_to_train(self):
        _locked_routes = []
        for _, r in self.curr_train_with_route.items():
            _locked_routes.append(r)
            _locked_routes.extend(self.mutex_routes_by_route.get(r))
        return _locked_routes

    @property
    @abstractmethod
    def banned_paths(self):
        raise NotImplementedError("Needed to be implemented in AutoPoint or CtrlPoint")
