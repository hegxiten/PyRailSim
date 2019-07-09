#!/usr/bin/python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod, abstractproperty
from observe import Observable, Observer
from itertools import combinations, permutations
from collections import defaultdict


class Aspect():
    """
    Aspect shows the meaning of the signals. 
    Could be compared with other aspects with more/less favorable comparison.
    """
    COLOR_SPD_DICT = {'r': 0.0, 'y': 20 / 3600, 'yy': 40 / 3600, 'g': 72 / 3600}

    def __init__(self, color, route=None):
        self.color = color
        self.route = route

    def __repr__(self):
        return 'Aspect: {}, \t route {}, target speed {} mph'.format(
            self.color, self.route, self.target_speed * 3600)

    @property
    def target_speed(self):
        return self.COLOR_SPD_DICT[self.color] if self.color else 0

    def __eq__(self, other):
        return self.color == other.color

    def __ne__(self, other):
        return self.color != other.color

    def __lt__(self, other):
        '''r < y < yy < g'''
        if self.color == 'r' and other.color != 'r':
            return True
        elif self.color == 'y' and (other.color == 'yy' or other.color == 'g'):
            return True
        elif self.color == 'yy' and (other.color == 'g'):
            return True
        else:
            return False

    def __gt__(self, other):
        '''g > yy > y > r'''
        if self.color == 'g' and other.color != 'g':
            return True
        elif self.color == 'yy' and (other.color == 'y' or other.color == 'r'):
            return True
        elif self.color == 'y' and (other.color == 'r'):
            return True
        else:
            return False

    def __le__(self, other):
        '''r <= y <= yy <= g'''
        if self.color == 'r':
            return True
        elif self.color == 'y' and (other.color != 'r'):
            return True
        elif self.color == 'yy' and (other.color == 'g' or other.color == 'yy'):
            return True
        elif self.color == 'g' and other.color == 'g':
            return True
        else:
            return False

    def __ge__(self, other):
        '''
        g >= yy >= y >= r
        '''
        if self.color == 'g':
            return True
        elif self.color == 'yy' and (other.color != 'g'):
            return True
        elif self.color == 'y' and (other.color == 'r' or other.color == 'y'):
            return True
        elif self.color == 'r' and other.color == 'r':
            return True
        else:
            return False


class Signal(Observable, Observer):
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__()
        self.system = None
        self.sigpoint = sigpoint
        self._MP = MP
        self.port_idx = port_idx
        self._aspect = Aspect('r', route=self.route)

    @property
    def facing_direction_sign(self):
        if self.governed_track:
            if max(self.governed_track.MP) == self.MP:
                return 1
            elif min(self.governed_track.MP) == self.MP:
                return -1
            else:
                raise ValueError('Undefined MP direction')
        else:
            return -self.sigpoint.signal_by_port[self.sigpoint.opposite_port(
                self.port_idx)].facing_direction_sign

    @property
    def route(self):
        return self.sigpoint.current_route_by_port.get(self.port_idx)

    @property
    def MP(self):
        if not self._MP:
            self._MP = self.sigpoint.MP
        return self._MP

    @MP.setter
    def MP(self, new_MP):
        print(
            'Warning:\n\tSetting MilePost manually for {}!\n\tChanging from old MP {} to new MP {}'
            .format(self, self._MP, new_MP))
        self._MP = new_MP

    @property
    def aspect(self):
        # print('call aspect of {} route {}'.format(self.sigpoint,self.route))
        self._aspect.route = self.route
        if not self.route:
            self._aspect.color = 'r'
        elif self.cleared_signal_to_exit_system:  # exiting the system
            self._aspect.color = 'g'
        elif self.number_of_blocks_cleared_ahead == 0:
            self._aspect.color = 'r'
        elif self.number_of_blocks_cleared_ahead == 1:
            if self.next_enroute_signal.cleared_signal_to_exit_system:
                self._aspect.color = 'g'
            else:
                self._aspect.color = 'y'
        elif self.number_of_blocks_cleared_ahead == 2:
            if self.next_enroute_signal.next_enroute_signal.cleared_signal_to_exit_system:
                self._aspect.color = 'g'
            else:
                self._aspect.color = 'yy'
        elif self.number_of_blocks_cleared_ahead >= 3:
            self._aspect.color = 'g'
        else:
            raise ValueError(
                'signal aspect of {}, port: {} not defined ready'.format(
                    self.sigpoint, self.port_idx))
        return self._aspect

    @property
    def permit_track(self):
        if self.route:
            return self.sigpoint.track_by_port.get(self.route[1])
        else:
            return None

    @property
    def governed_track(self):
        return self.sigpoint.track_by_port.get(self.port_idx)

    @property
    # call a point instance from signal instance
    def next_enroute_sigpoint(self):
        return self.permit_track.shooting_point(self.sigpoint) if self.permit_track\
            else None

    @property
    def next_enroute_signal(self):
        return self.next_enroute_sigpoint.signal_by_port[self.next_enroute_sigpoint_port] \
            if self.permit_track else None

    @property
    def next_enroute_sigpoint_port(self):
        return self.permit_track.shooting_port(point=self.sigpoint) if self.permit_track\
            else None

    @property
    def cleared_signal_to_exit_system(self):
        return True if self.route and not self.permit_track else False

    @property
    def curr_routing_path(self):
        if self.governed_track:
            _track_rp = self.governed_track.curr_routing_path
            if not _track_rp:
                return None
            elif self.governed_track.routing[1][0] == self.sigpoint:
                return _track_rp
            else:
                return None
        elif self.permit_track:
            assert self.permit_track.routing[0][0] == self.sigpoint
            return self.permit_track.curr_routing_path
        else:
            return None

    @property
    def curr_enroute_tracks(self):
        if self.curr_routing_path:
            _curr_enroute_tracks = []
            for ((p1, p1port), (p2, p2port)) in self.curr_routing_path:
                _curr_enroute_tracks.append(
                    self.system.get_track_by_point_port_pairs(
                        p1, p1port, p2, p2port))
            return _curr_enroute_tracks
        else:
            return None

    @property
    def number_of_blocks_cleared_ahead(self):
        _number = 0
        if self.curr_enroute_tracks:
            if self.governed_track:
                _trk_idx = self.curr_routing_path.index(
                    self.governed_track.routing)
            else:
                _trk_idx = 0
            _tracks_ahead = self.curr_enroute_tracks[_trk_idx + 1:]
            for i in range(len(_tracks_ahead)):
                if _tracks_ahead[i]:
                    if _tracks_ahead[i].is_Occupied:
                        return _number
                    elif not _tracks_ahead[i].is_Occupied:
                        _number += 1
                        continue
        return _number

    #-------------------------#
    def clear(self, port):
        pass

    def close(self, port):
        pass

    def update(self, observable, update_message):
        pass
        return
        assert observable.type in ['abs', 'home', 'block', 'bigblock']
        # print("{} signal {} is observing {} signal {}".format(self.port_idx, self.pos, observable.port_idx, observable.pos))
        # print("Because {} signal {} changed from {} to {}:".format(observable.port_idx, str(observable.pos), update_message['old'].color, update_message['new'].color))
        if observable.type == 'bigblock' and observable.direction != self.port_idx:
            self.change_color_to('r', False)
        elif observable.type == 'track':
            self.change_color_to('r', False)
        elif observable.type == 'home' and observable.port_idx != self.port_idx:
            if update_message.color != 'r':
                self.change_color_to('r', False)
        else:
            if update_message.color == 'yy':  # observable:        g -> yy
                # observer:            -> g
                self.change_color_to('g', True)
            elif update_message.color == 'y':  # observable:     g/yy -> y
                # observer:            -> yy
                self.change_color_to('yy', True)
            elif update_message.color == 'r':  # observable: g/yy/y/r -> r
                # observer:            -> g
                self.change_color_to('y', True)

    def change_color_to(self, color, isNotified=True):
        pass
        return
        new_aspect = Aspect(color)
        print("\t {} signal changed from {} to {}".format(
            self.port_idx, self.aspect.color, color))
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)


class AutoSignal(Signal):
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__(port_idx, sigpoint, MP)
        self.type = 'abs'

    def __repr__(self):
        return 'AutoSignal of {}, port: {}'.format(self.sigpoint, self.port_idx)


class HomeSignal(Signal):
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__(port_idx, sigpoint, MP)
        self.sigpoint = None
        self.type = 'home'

    def __repr__(self):
        return 'HomeSignal of {}, port: {}'.format(self.sigpoint, self.port_idx)

    # #--------------------------------#
    # def update(self, observable, update_message):
    #     pass
    #     return
    #     if observable.type == 'block':
    #         if update_message:      # block 有车
    #             self.change_color_to('r', False)
    #     # 情况4
    #     elif observable.type == 'home' and self.hs_type == 'A'\
    #         and observable.port_idx != self.port_idx:
    #         if update_message.color != 'r':                          # 反向主体信号非红
    #             self.change_color_to('r', True)
    #     elif observable.type == 'home' and self.hs_type == 'B'\
    #         and observable.port_idx != self.port_idx:
    #         if update_message.color != 'r':                          # 反向主体信号非红
    #             self.change_color_to('r', False)
    #     elif observable.type == 'abs': # and 同时还放车进入下一个abs:
    #         if update_message.color == 'yy':                         # observable:        g -> yy
    #             self.change_color_to('g', False)                            # observer:            -> g
    #         elif update_message.color == 'y':                        # observable:     g/yy -> y
    #             self.change_color_to('yy', False)                           # observer:            -> yy
    #         elif update_message.color == 'r':                        # observable: g/yy/y/r -> r
    #             self.change_color_to('y', False)


class InterlockingPoint(Observable, Observer):
    """
    Abstract Class, a.k.a SignalPoint/Sigpoint
    """

    def __init__(self, system, idx, MP=None):
        super().__init__()
        self.system = system
        self.MP = MP
        self.idx = idx
        self.ports = []
        self.available_ports_by_port = defaultdict(list)
        self.all_valid_routes = []
        self.non_mutex_routes_by_route = defaultdict(list)
        self.ban_ports_by_port = defaultdict(list)

        self._current_routes = []
        self.neighbor_nodes = []
        self.track_by_port = {}
        self._curr_train_with_route = {}

    @abstractproperty
    def current_routes(self):
        pass

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
    def mutex_routes_by_route(self):
        _mutex_routes_by_route = defaultdict(list)
        for vr in self.all_valid_routes:
            _all_valid_routes = [r for r in self.all_valid_routes]
            _all_valid_routes.remove(vr)
            _mutex_routes_by_route[vr].extend(_all_valid_routes)
        for r, nmrl in self.non_mutex_routes_by_route.items():
            if nmrl in _mutex_routes_by_route[r]:
                _mutex_routes_by_route[r].remove(nmrl)
        return _mutex_routes_by_route

    @property
    def current_invalid_routes(self):
        _current_invalid_routes = []
        # collect all banned routes in a permutation list of 2-element tuples
        for p, bplist in self.ban_ports_by_port.items():
            for bp in bplist:
                if (p, bp) not in _current_invalid_routes:
                    _current_invalid_routes.append((p, bp))
                if (bp, p) not in _current_invalid_routes:
                    _current_invalid_routes.append((bp, p))
        # collect all mutex routes according to currently openned routes
        for r in self.current_routes:
            for vr in self.all_valid_routes:
                if vr not in self.non_mutex_routes_by_route[
                        r] and vr not in _current_invalid_routes:
                    _current_invalid_routes.append(vr)
        for _, r in self.curr_train_with_route.items():
            if r not in _current_invalid_routes:
                _current_invalid_routes.append(r)
            for mr in self.mutex_routes_by_route[r]:
                if mr not in _current_invalid_routes:
                    _current_invalid_routes.append(mr)
        return _current_invalid_routes


class AutoPoint(InterlockingPoint):
    def __init__(self, system, idx, MP=None):
        super().__init__(system, idx, MP)
        self.type = 'at'
        self.ports = [0, 1]
        self.available_ports_by_port = {0: [1], 1: [0]}  # define legal routes
        self.non_mutex_routes_by_route = {}
        self.ban_ports_by_port = {}
        self.all_valid_routes = [(0, 1), (1, 0)]

        # build up signals
        self.signal_by_port = {
            0: AutoSignal(0, self, MP=self.MP),
            1: AutoSignal(1, self, MP=self.MP)
        }
        # register the AutoPoint's ownership over the signals
        for _, sig in self.signal_by_port.items():
            sig.sigpoint = self
            sig.system = self.system

    def __repr__(self):
        return 'AutoPoint{}'.format(self.idx)

    @property
    def current_routes(self):
        self._current_routes = []
        for p, t in self.track_by_port.items():
            # only AutoPoints can assign current routes like this because
            # AutoPoints have only 0,1 as their ports
            if t.routing:
                if p == 0 and p == t.routing[1][1]:
                    self._current_routes = [(0, 1)]
                elif p == 0 and p == t.routing[0][1]:
                    self._current_routes = [(1, 0)]
        return self._current_routes

    def opposite_port(self, port):
        '''Return the signal port on the other side of the given port of an AutoSignal.
        Method restricted to AutoSignal instances. 
        '''
        assert port in self.ports
        assert len(self.ports) == 2
        for p in self.ports:
            if p != port:
                return p


class ControlPoint(InterlockingPoint):
    def __init__(self,
                 system,
                 idx,
                 ports,
                 MP=None,
                 ban_ports_by_port=defaultdict(list),
                 non_mutex_routes_by_route=defaultdict(list)):
        super().__init__(system, idx, MP)
        self.type = 'cp'
        self.ports = ports
        self.ban_ports_by_port = ban_ports_by_port
        self.non_mutex_routes_by_route = non_mutex_routes_by_route
        self._current_routes = []
        self.bigblock_by_port = {}
        # available options for routes, dict[port] = list(options)
        self.available_ports_by_port = defaultdict(list)
        for i in self.ports:
            for j in self.ports:
                if j not in self.ban_ports_by_port.get(i, []) and j != i:
                    self.available_ports_by_port[i].append(j)

        self.signal_by_port = {}  # build up signals
        for i in self.ports:
            self.signal_by_port[i] = HomeSignal(i, self, MP)

        # available options for routes, list of routes
        self.all_valid_routes = []
        for p, plist in self.available_ports_by_port.items():
            for rp in plist:
                if (p, rp) not in self.all_valid_routes:
                    self.all_valid_routes.append((p, rp))
                if (rp, p) not in self.all_valid_routes:
                    self.all_valid_routes.append((rp, p))

        for _, sig in self.signal_by_port.items(
        ):  # add the ownership of signals
            sig.sigpoint = self
            sig.system = self.system

    def __repr__(self):
        return 'ControlPoint{}'.format(self.idx)

    @property
    def vertex(self):
        for i in self.ports:
            if not self.track_by_port.get(i):
                return True
        return False

    @property
    def current_routes(self):
        for r1, r2 in permutations(self._current_routes, 2):
            assert r2 not in self.mutex_routes_by_route[r1]
            assert r1[1] not in self.ban_ports_by_port[
                r1[0]] and r2[1] not in self.ban_ports_by_port[r2[0]]
        return self._current_routes

    @current_routes.setter
    def current_routes(self, new_route_list):
        assert isinstance(new_route_list, list)
        for i in new_route_list:
            assert i in self.all_valid_routes
        self._current_routes = new_route_list

    def open_route(self, route):
        assert len(route) == 2
        assert isinstance(route, tuple)
        if route in self.current_routes:  # do nothing when trying to open an existing route
            print('route {} for {} already opened'.format(route, self))
        elif route not in self.current_routes:
            # if not in all_valid routes, the route to open is banned
            if route not in self.all_valid_routes:
                raise ValueError(
                    'illegal route for {}: banned/non-existing routes'.format(
                        self))
            elif route in self.all_valid_routes:
                # being in all_valid_routes means the route to open is not banned
                # it is only possible to be conflicting with somrane existing routes
                conflict_routes = []
                if route in self.current_invalid_routes:
                    for cr in self.current_routes:
                        if route not in self.non_mutex_routes_by_route[cr]:
                            conflict_routes.append(cr)
                    for cr in conflict_routes:
                        self.close_route(cr)
                    print('conflicting routes {} are closed for {} to open'.
                          format(conflict_routes, route))
                # if conflicting with bigblock routing, don't open route
                self.current_routes.append(route)
                self.set_bigblock_routing_by_controlpoint_route(route)
                print('route {} of {} is opened'.format(route, self))
                # ControlPoint port traffic routing: route[0] -> route[1]
                # BigBlock routing:
                #   (somewhere, someport) -> (self, route[0]) and
                #   (self, route[1]) to (somewhere, someport)

    def close_route(self, route=None):
        if route:
            assert route in self._current_routes
            print('route {} of {} is closed'.format(route, self))
            self.current_routes.remove(route)
        else:
            print('all routes fof {} are closed'.format(self))
            self.current_routes = []
            for p in self.ports:
                self.cancel_bigblock_routing_by_port(p)

    def find_route_for_port(self, port):
        _candidate_ports = [i for i in self.available_ports_by_port[port]]
        for p in self.available_ports_by_port[port]:
            _candi_bblk = self.bigblock_by_port.get(p)
            _candi_track = self.track_by_port.get(p)
            if not _candi_bblk or not _candi_track:
                continue
            elif _candi_track.is_Occupied:
                _candidate_ports.remove(p)
                continue
            elif not _candi_bblk.routing:
                continue
            elif _candi_bblk.routing != ((self, p), (_candi_bblk.shooting_point(
                    point=self), _candi_bblk.shooting_port(port=p))):
                if _candi_bblk.train:
                    _candidate_ports.remove(p)
                    continue
        if not _candidate_ports:
            return None
        else:
            return (port, _candidate_ports[0])

    def set_bigblock_routing_by_controlpoint_route(self, route):
        assert route
        (x, y) = route
        _in_port, _in_bblk = x, self.bigblock_by_port.get(x)
        _out_port, _out_bblk = y, self.bigblock_by_port.get(y)
        if _in_bblk and _out_bblk:
            _in_bblk.routing = ((_in_bblk.shooting_point(point=self),
                                 _in_bblk.shooting_port(point=self)), (self, x))
            _out_bblk.routing = ((self, y),
                                 (_out_bblk.shooting_point(point=self),
                                  _out_bblk.shooting_port(point=self)))

        elif (not _in_bblk) and _out_bblk:
            _out_bblk.routing = ((self, y),
                                 (_out_bblk.shooting_point(point=self),
                                  _out_bblk.shooting_port(point=self)))
        elif _in_bblk and (not _out_bblk):
            _in_bblk.routing = ((_in_bblk.shooting_point(point=self),
                                 _in_bblk.shooting_port(point=self)), (self, x))

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

    def update_signal(self, all_routes):
        pass
        return
        '''update the signals in a ControlPoint according to current routes'''
        for (p1, p2) in self.all_valid_routes:
            self.signal_by_port[p1].close()
            self.signal_by_port[p2].close()
        for (p1, p2) in self.current_routes:
            self.signal_by_port[p2].close()
            self.signal_by_port[p1].clear()


if __name__ == '__main__':
    a = Aspect('r')
    print(Aspect.COLOR_SPD_DICT)
