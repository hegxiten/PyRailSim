from collections import defaultdict
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
        '''
        r < y < yy < g
        '''
        if self.color == 'r' and other.color != 'r':
            return True
        elif self.color == 'y' and (other.color == 'yy' or other.color == 'g'):
            return True
        elif self.color == 'yy' and (other.color == 'g'):
            return True
        else:
            return False

    def __gt__(self,other):
        '''
        g > yy > y > r
        '''  
        if self.color == 'g' and other.color != 'g':
            return True
        elif self.color == 'yy' and (other.color == 'y' or other.color == 'r'):
            return True
        elif self.color == 'y' and (other.color == 'r'):
            return True
        else:
            return False

    def __le__(self,other):
        '''
        r <= y <= yy <= g
        '''  
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
        self.track_to_enter = None
        self.type = None
    
    def change_color_to(self, color, isNotified=True):
        
        new_aspect = Aspect(color)

        print("\t {} signal changed from {} to {}".format(self.port_idx, self.aspect.color, color))
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)

class AutoSignal(Signal):
    def __init__(self, port_idx, MP=None):
        super().__init__(port_idx, MP)
        self.at = None
        if (port_idx % 2) == 0:
            self.facing_direction = 'L'
        else:
            self.facing_direction = 'R'
        self.aspect = Aspect('g')
        self.type = 'abs'
    
    def __repr__(self):
        return 'AutoSignal of {}, port: {}'.format(self.at, self.port_idx)

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
        self.cp = None
        self.aspect = Aspect('r')
        self.type = 'home'
    
    def __repr__(self):
        return 'HomeSignal of {}, port: {}'.format(self.cp, self.port_idx)

    def clear(self, port, condition='fav'):
        pass

    def close(self):
        pass

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
        self.idx = idx
        self.type = 'at'
        self.MP = MP
        self.ports = [0,1]
        # build up signals
        self.port_entry_signal = {0:AutoSignal(0, MP=self.MP), 1:AutoSignal(1, MP=self.MP)}
        # define legal routes
        self.available_p2p_routes = {0:[1], 1:[0]}
        self.non_mutex_routes = {(0,1):[(1,0)], (1,0):[(0,1)]}
        assert len(self.port_entry_signal) == 2
        self.port_track = defaultdict(int)
        # add the ownership of signals
        for _, v in self.port_entry_signal.items():
            v.at = self
        self.neighbors = []
        self._current_routes = []

    def __repr__(self):
        return 'AutoPoint{}'.format(self.idx)

class ControlPoint(AutoPoint):
    def __init__(self, idx, ports, MP=None, ban_routes=defaultdict(list), non_mutex_routes=defaultdict(list)):
        super().__init__(idx, MP)
        self.type = 'cp'
        self.ports = ports
        self.port_entry_signal = defaultdict(list)
        self.available_p2p_routes = defaultdict(list)   # port to port - p2p
        self.non_mutex_routes = non_mutex_routes
        
        # ban illegal routes
        for i in self.ports:
            for j in self.ports:
                if j not in ban_routes.get(i, []):
                    self.available_p2p_routes[i].append(j)
        
        # build up signals
        for i in self.ports:
            port_entry_signal = HomeSignal(i)
            port_entry_signal.out_ports.extend(self.available_p2p_routes[i])            
            self.port_entry_signal[i] = port_entry_signal
        # add the ownership of signals
        for _, v in self.port_entry_signal.items():
            v.cp = self

        self._current_routes = []

    def __repr__(self):
        return 'ControlPoint{}'.format(self.idx)
    
    @property
    def current_routes(self):
        return self._current_routes
    
    @current_routes.setter
    def current_routes(self, route):
        if route in self._current_routes:
            pass
        else:
            self._current_routes.append(route)
            self.port_entry_signal[route[0]].clear(route)
            for r in self._current_routes:
                if r not in self.non_mutex_routes[route]:
                    self.close_route(r)
            self.listener_updates(obj=('cleared', route))

    def close_route(self, route):
        assert route in self._current_routes
        self.port_entry_signal[route[0]].close()
        self._current_routes.remove(route)
        self.listener_updates(obj=('closed', route))
   
        
    # ------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------- #

    def open_route_old(self, direction, track_idx, color):
        # 打开cp中的某个方向某条通路，打开一侧的某个灯，反向的变红
        if direction == 'R' or direction == 'L':
            if direction == 'R':
                assert track_idx < len(self.L_port_entry_signal)
            if direction == 'L':
                assert track_idx < len(self.R_port_entry_signal)
            #取出通路需要改变的那一侧的信号灯以及另一侧全部需要变红的信号灯
            selected_track_signals = self.L_port_entry_signal if direction == 'R' else self.R_port_entry_signal
            other_track_signals = self.L_port_entry_signal if direction == 'L' else self.R_port_entry_signal
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
            for signal in self.L_port_entry_signal:
                signal.change_color_to('r')
            for signal in self.R_port_entry_signal:
                signal.change_color_to('r')
        # 更新变化之后cp的方向，并且更新观察者的更新。
        self.available_p2p_routes = direction
        self.listener_updates()

if __name__ == '__main__':
    cp = ControlPoint(idx=3, ports=[0,1,3], ban_routes={1:[3],3:[1]})
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
