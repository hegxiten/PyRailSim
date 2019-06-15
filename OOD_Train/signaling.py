from collections import defaultdict
from itertools import combinations, permutations
from observe import Observable, Observer

class Aspect(object):
    '''
    Aspect代表信号的“含义”,用于比较“大小”
    '''    
    def __init__(self, color, route=None):
        self.color = color
        self.route = ()
    
    def __repr__(self):
        return 'Aspect: {}, route {}'.format(self.color, self.route)

    def __eq__(self,other):
        return self.color == other.color

    def __ne__(self,other):
        return self.color != other.color

    def __lt__(self,other):
        '''r < y < yy < g'''
        if self.color == 'r' and other.color != 'r':
            return True
        elif self.color == 'y' and (other.color == 'yy' or other.color == 'g'):
            return True
        elif self.color == 'yy' and (other.color == 'g'):
            return True
        else:
            return False

    def __gt__(self,other):
        '''g > yy > y > r'''  
        if self.color == 'g' and other.color != 'g':
            return True
        elif self.color == 'yy' and (other.color == 'y' or other.color == 'r'):
            return True
        elif self.color == 'y' and (other.color == 'r'):
            return True
        else:
            return False

    def __le__(self,other):
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

    def __ge__(self,other):
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
        self.sigpoint = sigpoint
        self.port_idx = port_idx
        self._aspect = Aspect('r', route=self.route)

    @property
    def route(self):
        return self.sigpoint.current_route_by_port.get(self.port_idx)
    
    @property
    def aspect(self):
        self._aspect.route = self.route
        if not self.route:
            self._aspect.color = 'r'
            return self._aspect
        elif self.permit_track.is_Occupied:
            self._aspect.color = 'r'
            return self._aspect
        elif self.next_enroute_signal.aspect.color == 'r':
            self._aspect.color = 'y'
            return self._aspect
        elif self.next_enroute_signal.aspect.color == 'y':
            self._aspect.color = 'yy'
            return self._aspect
        elif self.next_enroute_signal.aspect.color == 'yy':
            self._aspect.color = 'g'
            return self._aspect
        else:
            self._aspect.color = 'g'
            return self._aspect

    @property
    def permit_track(self):
        assert self.route
        return self.sigpoint.track_by_port[self.route[1]]

    @property
    def next_enroute_sigpoint(self):    # call a point instance from signal instance
        if self.sigpoint == self.permit_track.L_point:
            return self.permit_track.R_point
        elif self.sigpoint == self.permit_track.R_point:
            return self.permit_track.L_point

    @property
    def next_enroute_signal(self):
        if self.sigpoint == self.permit_track.L_point:
            port_of_next_enroute_signal = self.permit_track.port_by_sigpoint[self.permit_track.R_point]
        elif self.sigpoint == self.permit_track.R_point:
            port_of_next_enroute_signal = self.permit_track.port_by_sigpoint[self.permit_track.L_point]
        return self.next_enroute_sigpoint.signal_by_port[port_of_next_enroute_signal]

    def clear(self, route):
        pass

    def close(self, route):
        pass

    def change_color_to(self, color, isNotified=True):
        new_aspect = Aspect(color)
        print("\t {} signal changed from {} to {}".format(self.port_idx, self.aspect.color, color))
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)

class AutoSignal(Signal):
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__(port_idx, sigpoint, MP)
        self.type = 'abs'
    
    def __repr__(self):
        return 'AutoSignal of {}, port: {}'.format(self.sigpoint, self.port_idx)

    def clear(self, port):
        pass

    def close(self, port):
        pass

    def update(self, observable, update_message):
        assert observable.type in ['abs','home','block','bigblock']
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
            if update_message.color == 'yy':                         # observable:        g -> yy
                self.change_color_to('g', True)                            # observer:            -> g
            elif update_message.color == 'y':                        # observable:     g/yy -> y
                self.change_color_to('yy', True)                           # observer:            -> yy
            elif update_message.color == 'r':                        # observable: g/yy/y/r -> r
                self.change_color_to('y', True)                            # observer:            -> g

class HomeSignal(Signal):
    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__(port_idx, sigpoint, MP)
        self.sigpoint = None
        self.type = 'home'
    
    def __repr__(self):
        return 'HomeSignal of {}, port: {}'.format(self.sigpoint, self.port_idx)
    
    def update(self, observable, update_message):
        if observable.type == 'block':
            if update_message:      # block 有车
                self.change_color_to('r', False)
        # 情况4
        elif observable.type == 'home' and self.hs_type == 'A'\
            and observable.port_idx != self.port_idx:
            if update_message.color != 'r':                          # 反向主体信号非红                 
                self.change_color_to('r', True)
        elif observable.type == 'home' and self.hs_type == 'B'\
            and observable.port_idx != self.port_idx:
            if update_message.color != 'r':                          # 反向主体信号非红                 
                self.change_color_to('r', False)
        elif observable.type == 'abs': # and 同时还放车进入下一个abs:
            if update_message.color == 'yy':                         # observable:        g -> yy
                self.change_color_to('g', False)                            # observer:            -> g
            elif update_message.color == 'y':                        # observable:     g/yy -> y
                self.change_color_to('yy', False)                           # observer:            -> yy
            elif update_message.color == 'r':                        # observable: g/yy/y/r -> r
                self.change_color_to('y', False)  

class AutoPoint(Observable, Observer):
    def __init__(self, idx, MP=None):
        super().__init__()
        self.MP = MP
        self.idx = idx
        self.type = 'at'
        self.ports = [0,1]
        self.available_ports_by_port = {0:[1], 1:[0]}          # define legal routes
        self.non_mutex_routes_by_route = {}
        self.ban_ports_by_port = {}
        self.all_valid_routes = [(0,1),(1,0)]

        self._current_routes = []
        self.neighbor_nodes = []
        self.track_by_port = {}
        
        # build up signals
        self.signal_by_port = {0:AutoSignal(0, self, MP=self.MP), 1:AutoSignal(1, self, MP=self.MP)}
        assert len(self.signal_by_port) == 2
        
        # add the ownership of signals
        for _, sig in self.signal_by_port.items():
            sig.sigpoint = self
        
    def __repr__(self):
        return 'AutoPoint{}'.format(self.idx)
    
    @property
    def current_routes(self):
        for r1,r2 in permutations(self._current_routes,2):
            assert r2 not in self.mutex_routes_by_route[r1]
            assert r1[1] not in self.ban_ports_by_port[r1[0]] and r2[1] not in self.ban_ports_by_port[r2[0]]
        return self._current_routes

    @current_routes.setter
    def current_routes(self, new_route_list):
        assert isinstance(new_route_list, list)
        for i in new_route_list:
            assert i in self.all_valid_routes
        self._current_routes = new_route_list

    @property
    def current_route_by_port(self):
        _current_route_by_port = {}
        for r in self.current_routes:
            _current_route_by_port[r[0]] = r
        return _current_route_by_port

    @property
    def mutex_routes_by_route(self):
        _mutex_routes_by_route = defaultdict(list)
        for r, nmrl in self.non_mutex_routes_by_route.items():
            for vr in self.all_valid_routes:
                if vr not in nmrl:
                    _mutex_routes_by_route[r].append(vr)
        return _mutex_routes_by_route
    
    @property
    def current_invalid_routes(self):
        _current_invalid_routes = []
        # collect all banned routes in a permutation list of 2-element tuples
        for p, bplist in self.ban_ports_by_port.items():
            for bp in bplist:
                if (p, bp) not in _current_invalid_routes:
                    _current_invalid_routes.append((p,bp))
                if (bp, p) not in _current_invalid_routes:
                    _current_invalid_routes.append((bp,p))
        # collect all mutex routes according to currently openned routes
        for r in self.current_routes:
            for vr in self.all_valid_routes:
                if vr not in self.non_mutex_routes_by_route[r] and vr not in _current_invalid_routes:
                    _current_invalid_routes.append(vr)
        return _current_invalid_routes

class ControlPoint(AutoPoint):
    def __init__(self, idx, ports, MP=None, ban_ports_by_port=defaultdict(list), non_mutex_routes_by_route=defaultdict(list)):
        super().__init__(idx, MP)
        self.type = 'cp'
        self.ports = ports
        self.ban_ports_by_port = ban_ports_by_port
        self.non_mutex_routes_by_route = non_mutex_routes_by_route
        self.bigblock_by_port = {}
        self.available_ports_by_port = defaultdict(list)   # available options for routes, dict[port] = list(options)
        for i in self.ports:
            for j in self.ports:
                if j not in self.ban_ports_by_port.get(i, []) and j != i:
                    self.available_ports_by_port[i].append(j)
        
        self.signal_by_port = {}      # build up signals
        for i in self.ports:
            self.signal_by_port[i] = HomeSignal(i, self, MP)

        self.all_valid_routes = []                      # available options for routes, list of routes
        for p, plist in self.available_ports_by_port.items():
            for rp in plist:
                if (p, rp) not in self.all_valid_routes:
                    self.all_valid_routes.append((p,rp))
                if (rp, p) not in self.all_valid_routes:
                    self.all_valid_routes.append((rp,p))

        for _, sig in self.signal_by_port.items():     # add the ownership of signals
            sig.sigpoint = self
    
    def __repr__(self):
        return 'ControlPoint{}'.format(self.idx)


    def open_route(self, route):
        assert len(route) == 2
        assert isinstance(route, tuple)
        if route in self.current_routes:       # do nothing when trying to open an existing route
            raise ValueError('route for {} already opened'.format(self))
        if route not in self.current_routes:   
            if route not in self.all_valid_routes:
                raise ValueError('illegal route for {}: banned or non-existing routes'.format(self))
            if route in self.all_valid_routes:
                if route in self.current_invalid_routes:
                    conflict_routes = []
                    for cr in self.current_routes:
                        if route not in self.non_mutex_routes_by_route[cr]:
                            conflict_routes.append(cr)
                    raise ValueError('illegal route for {}: conflicting with routes: {}'.format(self, conflict_routes))
                if route not in self.current_invalid_routes:
                    for cr in self.current_routes:
                        if cr not in self.non_mutex_routes_by_route:
                            self.close_route(cr)
                            print('conflicting route {} closed because {} is to open'.format(cr,route))
                    print('route {} is opened'.format(route))
                    self.current_routes.append(route)
                    # ControlPoint port traffic direction: route[0] -> route[1]
                    # BigBlock traffic direction: flip(route[0]) and flip(route[1])
                    # x, y are ports of the sigpoints that connecting to the bigblock
                    (x, y) = route
                    if (x % 2) == 0:
                        self.bigblock_by_port[x].traffic_direction = (1, 0)
                    else:
                        self.bigblock_by_port[x].traffic_direction = (0, 1)
                    if (y % 2) == 0:
                        self.bigblock_by_port[y].traffic_direction = (0, 1)
                    else:
                        self.bigblock_by_port[y].traffic_direction = (1, 0)
                    self.broadcast_route_to_autopoints(route)
                    self.listener_updates(obj=('cleared', route))

    def close_route(self, route=None):
        if route:
            assert route in self._current_routes
            self.signal_by_port[route[0]].close(route)
            self.current_routes.remove(route)
            self.listener_updates(obj=('closed', route))
        else:
            self._current_routes = []

    def broadcast_route_to_autopoints(self, route_to_broadcast):
        (x, y) = route_to_broadcast
        for t in self.bigblock_by_port[x].tracks:
            t.update_route_of_connected_autopoints()
        for t in self.bigblock_by_port[y].tracks:
            t.update_route_of_connected_autopoints()

    def update_signal(self, all_routes):
        '''update the signals in a ControlPoint according to current routes'''
        for (p1, p2) in self.all_valid_routes:
            self.signal_by_port[p1].close()
            self.signal_by_port[p2].close()
        for (p1, p2) in self.current_routes:
            self.signal_by_port[p2].close()
            self.signal_by_port[p1].clear()
            
            
        
    # ------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------- #
    
    def open_route_old(self, direction, track_idx, color):
        # 打开cp中的某个方向某条通路，打开一侧的某个灯，反向的变红
        if direction == 'R' or direction == 'L':
            if direction == 'R':
                assert track_idx < len(self.L_signal_by_port)
            if direction == 'L':
                assert track_idx < len(self.R_signal_by_port)
            #取出通路需要改变的那一侧的信号灯以及另一侧全部需要变红的信号灯
            selected_track_signals = self.L_signal_by_port if direction == 'R' else self.R_signal_by_port
            other_track_signals = self.L_signal_by_port if direction == 'L' else self.R_signal_by_port
            # 将cp两侧灯，除了通路面对灯那盏灯变为固定的非红颜色，其余变红。
            for i in range(len(selected_track_signals)):
                if i == track_idx:
                    selected_track_signals[i].change_color_to(color)
                else:
                    selected_track_signals[i].change_color_to('r')
            for i in range(len(other_track_signals)):
                other_track_signals[i].change_color_to('r')
        elif direction == 'neutral':
            # 如果没有方向，那么cp的两侧的所有灯全部变红
            for signal in self.L_signal_by_port:
                signal.change_color_to('r')
            for signal in self.R_signal_by_port:
                signal.change_color_to('r')
        # 更新变化之后cp的方向，并且更新观察者的更新。
        self.available_ports_by_port = direction
        self.listener_updates()

if __name__ == '__main__':
    cp = ControlPoint(idx=3, ports=[0,1,3], ban_ports_by_port={1:[3],3:[1]})
    print(cp)

if __name__ == '__main__':
    L_signals = [HomeSignal('L')] + [AutoSignal('L') for i in range(1,9)] + [HomeSignal('L')]
    R_signals = [HomeSignal('R')] + [AutoSignal('R') for i in range(1,9)] + [HomeSignal('R')]
    blocks = [BlockTrack() for i in range(9)]
    def registersignal():
        for i in range(1,10):
            L_signals[i].add_observer(L_signals[i-1])
        for i in range(0,9):
            R_signals[i].add_observer(R_signals[i+1])
        
        for i in R_signals:
            if i.type == 'abs':
                L_signals[0].add_observer(i)
        for i in L_signals:
            if i.type == 'abs':
                R_signals[9].add_observer(i)
        
    def initialize():
        for i in L_signals + R_signals:
            if i.type == 'home':
                i.change_color_to('r')

    def registerblock():
        for i in range(9):
            blocks[i].add_observer(L_signals[i])
            blocks[i].add_observer(R_signals[i+1])

    registersignal()
    #registerblock()
    initialize()

    '''
    Print observers
    '''
    # for i in L_signals + R_signals:
    #     print((i.__class__.__name__, i.pos, i.type, i.port_idx),'  \t\tobservers:', [(j.__class__.__name__, j.pos, j.port_idx) for j in i._Observable__observers])

    # for i in blocks:
    #     print((i.__class__.__name__, i.pos, i.type),'  \t\t\tobservers:', [(j.__class__.__name__, j.pos, j.port_idx) for j in i._Observable__observers])

    print('left :',[s.aspect.color for s in L_signals])
    print('right:',[s.aspect.color for s in R_signals])

    # L_signals[0].change_color_to('g')
    R_signals[9].change_color_to('g')
    
    print('\n')
    print('left :',[s.aspect.color for s in L_signals])
    print('right:',[s.aspect.color for s in R_signals])
