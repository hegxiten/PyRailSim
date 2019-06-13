from collections import defaultdict
from itertools import combinations, permutations
from observe import Observable, Observer

class Aspect(object):
    '''
    Aspect代表信号的“含义”,用于比较“大小”
    '''    
    def __init__(self, color, route=None):
        self.color = color
        self.route = None
    
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
    def __init__(self, port_idx, MP=None):
        super().__init__()
        self.port_idx = port_idx
        self.aspect = Aspect(None)
        self.signalpoint = None
        self.type = None
    
    def change_color_to(self, color, isNotified=True):
        new_aspect = Aspect(color)
        print("\t {} signal changed from {} to {}".format(self.port_idx, self.aspect.color, color))
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)

    def clear(self, route):
        pass

    def close(self, route):
        pass

class AutoSignal(Signal):
    def __init__(self, port_idx, MP=None):
        super().__init__(port_idx, MP)
        if (port_idx % 2) == 0:
            self.facing_direction = 'L'
        else:
            self.facing_direction = 'R'
        self.aspect = Aspect('g')
        self.type = 'abs'
    
    def __repr__(self):
        return 'AutoSignal of {}, port: {}'.format(self.signalpoint, self.port_idx)

    @property
    def tracks_to_enter(self):
        _tracks_to_enter = []
        for enter_r in self.signalpoint._current_routes:
            _tracks_to_enter.append(self.signalpoint.port_track[r[1]])

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
    def __init__(self, port_idx, MP=None):
        super().__init__(port_idx)
        self.out_ports = []
        self.signalpoint = None
        self.aspect = Aspect('r')
        self.type = 'home'
    
    def __repr__(self):
        return 'HomeSignal of {}, port: {}'.format(self.signalpoint, self.port_idx)
    
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
        # build up signals
        self.entry_signal_port = {0:AutoSignal(0, MP=self.MP), 1:AutoSignal(1, MP=self.MP)}
        # define legal routes
        self.available_routes_p2p = {0:[1], 1:[0]}
        self.non_mutex_routes = {(0,1):[(1,0)], (1,0):[(0,1)]}
        assert len(self.entry_signal_port) == 2
        self.port_track = defaultdict(int)
        # add the ownership of signals
        for _, v in self.entry_signal_port.items():
            v.signalpoint = self
        self.neighbors = []
        self._current_routes = []

    def __repr__(self):
        return 'AutoPoint{}'.format(self.idx)

class ControlPoint(AutoPoint):
    def __init__(self, idx, ports, MP=None, ban_routes_port=defaultdict(list), non_mutex_routes=defaultdict(list)):
        super().__init__(idx, MP)
        self.type = 'cp'
        self.ports = ports
        self.non_mutex_routes = non_mutex_routes
        self.ban_routes_port = ban_routes_port

        self.available_routes_p2p = defaultdict(list)   # available options for routes, dict[port] = list(options)
        for i in self.ports:
            for j in self.ports:
                if j not in self.ban_routes_port.get(i, []) and j != i:
                    self.available_routes_p2p[i].append(j)
        
        self.entry_signal_port = defaultdict(list)      # build up signals
        for i in self.ports:
            entry_signal_port = HomeSignal(i)
            entry_signal_port.out_ports.extend(self.available_routes_p2p[i])            
            self.entry_signal_port[i] = entry_signal_port

        self.all_valid_routes = []                      # available options for routes, list of routes
        for p, plist in self.available_routes_p2p.items():
            for rp in plist:
                if (p, rp) not in self.all_valid_routes:
                    self.all_valid_routes.append((p,rp))
                if (rp, p) not in self.all_valid_routes:
                    self.all_valid_routes.append((rp,p))

        for _, v in self.entry_signal_port.items():     # add the ownership of signals
            v.signalpoint = self
    
        self._current_routes = []

    def __repr__(self):
        return 'ControlPoint{}'.format(self.idx)

    @property
    def current_invalid_routes(self):
        _current_invalid_routes = []
        # collect all banned routes in a permutation list of 2-element tuples
        for p, bplist in self.ban_routes_port.items():
            for bp in bplist:
                if (p, bp) not in _current_invalid_routes:
                    _current_invalid_routes.append((p,bp))
                if (bp, p) not in _current_invalid_routes:
                    _current_invalid_routes.append((bp,p))
        # collect all mutex routes according to currently openned routes
        for r in self.current_routes:
            for vr in self.all_valid_routes:
                if vr not in self.non_mutex_routes[r] and vr not in _current_invalid_routes:
                    _current_invalid_routes.append(vr)
        return _current_invalid_routes

    @property
    def current_routes(self):
        return self._current_routes

    def open_route(self, route):
        assert len(route) == 2
        assert isinstance(route, tuple)
        if route in self._current_routes:       # do nothing when trying to open an existing route
            raise ValueError('route for {} already opened'.format(self))
        if route not in self._current_routes:   
            if route not in self.all_valid_routes:
                raise ValueError('illegal route for {}: banned or non-existing routes'.format(self))
            if route in self.all_valid_routes:
                if route in self.current_invalid_routes:
                    conflict_routes = []
                    for cr in self._current_routes:
                        if route not in self.non_mutex_routes[cr]:
                            conflict_routes.append(cr)
                    raise ValueError('illegal route for {}: conflicting with routes: {}'.format(self, conflict_routes))
                if route not in self.current_invalid_routes:
                    for cr in self._current_routes:
                        if cr not in self.non_mutex_routes:
                            self.close_route(cr)
                            print('conflicting route {} closed because {} is to open'.format(cr,route))
                    print('route {} is opened'.format(route))
                    self._current_routes.append(route)
                    self.listener_updates(obj=('cleared', route))
                    self.update_signal(self._current_routes)

    def close_route(self, route):
        assert route in self._current_routes
        self.entry_signal_port[route[0]].close(route)
        self._current_routes.remove(route)
        self.listener_updates(obj=('closed', route))
        self.update_signal(self._current_routes)

    def update_signal(self, all_routes):
        pass
    # ------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------- #

    def open_route_old(self, direction, track_idx, color):
        # 打开cp中的某个方向某条通路，打开一侧的某个灯，反向的变红
        if direction == 'R' or direction == 'L':
            if direction == 'R':
                assert track_idx < len(self.L_entry_signal_port)
            if direction == 'L':
                assert track_idx < len(self.R_entry_signal_port)
            #取出通路需要改变的那一侧的信号灯以及另一侧全部需要变红的信号灯
            selected_track_signals = self.L_entry_signal_port if direction == 'R' else self.R_entry_signal_port
            other_track_signals = self.L_entry_signal_port if direction == 'L' else self.R_entry_signal_port
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
            for signal in self.L_entry_signal_port:
                signal.change_color_to('r')
            for signal in self.R_entry_signal_port:
                signal.change_color_to('r')
        # 更新变化之后cp的方向，并且更新观察者的更新。
        self.available_routes_p2p = direction
        self.listener_updates()

if __name__ == '__main__':
    cp = ControlPoint(idx=3, ports=[0,1,3], ban_routes_port={1:[3],3:[1]})
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
