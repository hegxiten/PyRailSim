from collections import defaultdict

import networkx as nx
from signal_light import Observable, Observer, AutoSignal, HomeSignal

class AutoPoint(Observable, Observer):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        self.type = 'at'
        self.ports = [0,1]
        self.port_entry_signal = {0:AutoSignal(0), 1:AutoSignal(1)}
        self.p2p_port_routes = {0:[1], 1:[0]}
        self.non_mutex_routes = {(0,1):[(1,0)], (1,0):[(0,1)]}
        assert len(self.port_entry_signal) == 2
        self.port_track = defaultdict(int)
        self.neighbors = []
        self.current_routes = []

class ControlPoint(AutoPoint):
    def __init__(self, idx, ports, ban_routes=defaultdict(list), non_mutex_routes=defaultdict(list)):
        super().__init__(idx)
        self.type = 'cp'
        self.ports = ports
        self.port_entry_signal = defaultdict(list)
        self.p2p_port_routes = defaultdict(list)
        self.non_mutex_routes = non_mutex_routes
        self.cp_neighbors = []
        for i in self.ports:
            for j in self.ports:
                if j not in ban_routes.get(i, []):
                    self.p2p_port_routes[i].append(j)

        for i in self.ports:
            port_entry_signal = HomeSignal(i)
            port_entry_signal.out_ports.extend(self.p2p_port_routes[i])            
            self.port_entry_signal[i] = port_entry_signal
    
    @property
    def current_routes(self):
        return self.current_routes
    
    @current_routes.setter
    def current_routes(self, route):
        if route in self.current_routes:
            pass
        else:
            self.current_routes.append(route)
            self.port_entry_signal[route[0]].clear(route)
            for r in self.current_routes:
                if r not in self.non_mutex_routes[route]:
                    self.close_route(r)
            self.listener_updates(obj=('cleared', route))

    def close_route(self, route):
        assert route in self.current_routes
        self.port_entry_signal[route[0]].close()
        self.current_routes.remove(route)
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
        self.p2p_port_routes = direction
        self.listener_updates()
