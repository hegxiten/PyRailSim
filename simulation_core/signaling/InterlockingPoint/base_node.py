from abc import ABC, abstractmethod
from collections import defaultdict

from simulation_core.observation_model.observe import Observable, Observer


class BaseNode(Observable, Observer, ABC):
    """
        Base Class, a.k.a SignalPoint, consisting of Graph nodes; containing signals
        Child classes include InterlockingPoint, AutoPoint, and ControlPoint, etc.
    """

    def __init__(self, system, idx, MP=None):
        super().__init__()
        self._system = system
        self._MP = MP
        self._idx = idx
        self._ports = []

        self._non_mutex_routes_set_by_route = None
        self._mutex_routes_by_route = None
        self._banned_ports_by_port = defaultdict(set)

        self.neighbor_nodes = []
        self.track_by_port = {}

        self._curr_routes_set = set()
        self._curr_train_with_route = {}

    @property
    @abstractmethod
    def available_ports_by_port(self) -> dict:
        pass

    @property
    @abstractmethod
    def all_valid_routes_set(self):
        pass

    @property
    @abstractmethod
    def curr_routes_set(self):
        pass

    @property
    @abstractmethod
    def non_mutex_routes_set_by_route(self) -> dict:
        pass

    @property
    @abstractmethod
    def banned_ports_by_port(self) -> dict:
        return self._banned_ports_by_port

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
    def non_mutex_routes_set_by_route(self):
        return self._non_mutex_routes_set_by_route

    @property
    def mutex_routes_by_route(self):
        if self._mutex_routes_by_route is None:
            self._mutex_routes_by_route = defaultdict(set)
            for valid_route in self.all_valid_routes_set:
                _all_valid_routes = self.all_valid_routes_set.copy()
                _all_valid_routes.remove(valid_route)
                self._mutex_routes_by_route[valid_route].update(_all_valid_routes)
            for route, non_mutex_route_list in self.non_mutex_routes_set_by_route.items():
                if non_mutex_route_list in self._mutex_routes_by_route[route]:
                    self._mutex_routes_by_route[route].remove(non_mutex_route_list)
        return self._mutex_routes_by_route

    @property
    def curr_route_by_port(self):
        _current_route_by_port = {}
        for r in self.curr_routes_set:
            _current_route_by_port[r[0]] = r
        return _current_route_by_port

    @property
    def curr_train_with_route(self):
        return self._curr_train_with_route

    @property
    def curr_invalid_routes_set(self):
        # General cases. For simplifcation, better be overriden
        _curr_invalid_routes_set = set()
        # collect all banned routes in a permutation list of 2-element tuples
        for p, bports in self.banned_ports_by_port.items():
            for bp in bports:
                _curr_invalid_routes_set.add((p, bp))
                _curr_invalid_routes_set.add((bp, p))
        # collect all mutex routes according to currently openned routes
        for r in self.curr_routes_set:
            for vr in self.all_valid_routes_set:
                if vr not in self.non_mutex_routes_set_by_route[r]:
                    _curr_invalid_routes_set.add(vr)
        # collect all routes currently under trains
        for r in self.locked_routes_due_to_train_set:
            _curr_invalid_routes_set.add(r)
        return _curr_invalid_routes_set

    @property
    def locked_routes_due_to_train_set(self):
        _locked_routes = set()
        for _, r in self.curr_train_with_route.items():
            _locked_routes.add(r)
            _locked_routes.update(self.mutex_routes_by_route.get(r))
        return _locked_routes

    @property
    @abstractmethod
    def banned_paths_set(self):
        raise NotImplementedError("Needed to be implemented in AutoPoint or CtrlPoint")
