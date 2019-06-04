import networkx as nx
from signal_light import Observable, Observer, AutoSignal, HomeSignal

class AutoPoint(Observable, Observer):
    def __init__(self, idx):
        super().__init__()
        self.type = 'at'
        self.ports = [0,1]
        self.entry_signals = {0:AutoSignal(0), 1:AutoSignal(1)}
        assert len(self.entry_signals) == 2
        self.port_routes = {0:[1], 1:[0]}
        self.port_tracks = {}
        self.current_routes = []

class ControlPoint(AutoPoint):
    def __init__(self, idx, ports, ban_routes={}, non_mutex_routes={}):
        super().__init__(idx)
        self.type = 'cp'
        self.entry_signals = []
        self.ports = ports
        self.port_routes = {}
        self.non_mutex_routes = non_mutex_routes
        for i in self.ports:
            for j in self.ports:
                if j not in ban_routes[i]:
                    self.port_routes[i].append(j)
        assert {None} == set([self.port_routes.get(k) for k in ban_routes.keys()])
        self.port_tracks = {}
        self.current_routes = []

        for i in self.ports:
            port_entry_signal = HomeSignal(i)
            port_entry_signal.out_ports.extend(self.port_routes[i])            
            self.entry_signals.append(port_entry_signal)

    def open_route(self, route, condition='fav'):
        assert route not in self.current_routes
        self.current_routes.append(route)
        self.entry_signals[route[0]].clear(route, condition=condition)
        for r in self.current_routes:
            if r not in self.non_mutex_routes[route]:
                self.close_route(r)
        self.listener_updates(obj=('cleared', route))

    def close_route(self, route):
        assert route in self.current_routes
        self.entry_signals[route[0]].close()
        self.current_routes.remove(route)
        self.listener_updates(obj=('closed', route))
        
    # ------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------- #

    def open_route_old(self, direction, track_idx, color):
        # 打开cp中的某个方向某条通路，打开一侧的某个灯，反向的变红
        if direction == 'R' or direction == 'L':
            if direction == 'R':
                assert track_idx < len(self.L_entry_signals)
            if direction == 'L':
                assert track_idx < len(self.R_entry_signals)
            #取出通路需要改变的那一侧的信号灯以及另一侧全部需要变红的信号灯
            selected_track_signals = self.L_entry_signals if direction == 'R' else self.R_entry_signals
            other_track_signals = self.L_entry_signals if direction == 'L' else self.R_entry_signals
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
            for signal in self.L_entry_signals:
                signal.change_color_to('r')
            for signal in self.R_entry_signals:
                signal.change_color_to('r')
        # 更新变化之后cp的方向，并且更新观察者的更新。
        self.port_routes = direction
        self.listener_updates()
