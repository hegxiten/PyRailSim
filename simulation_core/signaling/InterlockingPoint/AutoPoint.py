from simulation_core.signaling.InterlockingPoint.InterlockingPoint import InterlockingPoint
from simulation_core.signaling.Signal.AutoSignal import AutoSignal


class AutoPoint(InterlockingPoint):
    """
        Implementation of automatic signal point
        Signaling method: automatic block.
    """
    def __init__(self, system, idx, MP=None):
        super().__init__(system, idx, MP)
        self.type = 'at'
        self._ports = [0, 1]

        self._non_mutex_routes_by_route = {}
        self._banned_ports_by_port = {0: set([0]), 1: set([1])}
        # build up signals
        self.signal_by_port = {0: AutoSignal(0, self, MP=self.MP),
                               1: AutoSignal(1, self, MP=self.MP)}
        # register the AutoPoint's ownership over the signals
        for _, sig in self.signal_by_port.items():
            sig.signal_point = self
            sig.system = self.system

    def __repr__(self):
        return 'AutoPnt{}'.format(str(self.idx).rjust(2, ' '), )

    @property
    def banned_ports_by_port(self) -> dict:
        return self._banned_ports_by_port

    @property
    def bigblock(self):
        """
            For auto signal points, the bigblock for the two tracks on both ports are unique.
            @return: BigBlock of self.
        """
        return [t.bigblock for _, t in self.track_by_port.items()][0]

    @property
    def all_valid_routes_set(self):
        return set([(0, 1), (1, 0)])

    @property
    def non_mutex_routes_set_by_route(self):
        return self._non_mutex_routes_by_route

    @property
    def available_ports_by_port(self):
        """
            Define legal routes by different ports of the auto signal point.
            @return: Dictionary of {port: [ports]}
        """
        return {0: set([1]), 1: set([0])}

    @property
    def curr_routes_set(self):
        """
            Infer the current route from the track routing.
            @return: List of 2-element tuples, specifying the current routes of self.
        """
        for p, t in self.track_by_port.items():
            # only AutoPoints can assign current routes like this because
            # AutoPoints have only 0, 1 as their ports
            if t.routing:
                if p == 0 and p == t.routing[1][1]:
                    self._curr_routes_set = set([(0, 1)])
                elif p == 0 and p == t.routing[0][1]:
                    self._curr_routes_set = set([(1, 0)])
        return self._curr_routes_set

    @property
    def curr_invalid_routes_set(self):
        """
            Current invalid routes providing a valid current route. Overriding the general cases for simplification.
            @return: List of 2-element tuples, specifying the current routes of self.
        """
        _curr_routes_set = self.curr_routes_set
        if not _curr_routes_set:
            return set([])
        elif _curr_routes_set == [(0, 1)]:
            return set([(1, 0)])
        elif _curr_routes_set == [(1, 0)]:
            return set([(0, 1)])
        else:
            raise Exception('illegal route for AutoPoint {}: invalid route calculation error.'.format(self))

    @property
    def banned_paths_set(self):
        """
            There is no banned paths for auto signal points.
            @return: Empty list.
        """
        return set()

    def opposite_port(self, port):
        """
            Return the signal port on the other side of the given port of an AutoSignal.
            Method restricted to AutoSignal instances
            @return: int, port index
        """
        for p in self.ports:
            if p != port:
                return p