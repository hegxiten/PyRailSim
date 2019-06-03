import networkx as nx
from signal_light import Observable, Observer, AutoSignal, HomeSignal

class AutoPoint(Observable, Observer):
    def __init__(self):
        super().__init__()
        self.type = 'at'
        self.in_ports = [0,1]
        self.out_ports = [0,1]
        self.entry_signals = {0:AutoSignal(0), 1:AutoSignal(1)}
        assert len(self.entry_signals) == 2
        self.open_direction = {0:1, 1:0}
        self.mutex_routes = {(0,1):[(1,0)], (1,0):[(0,1)]}
        self.current_route = []

class ControlPoint(AutoPoint):
    def __init__(self, num_ports, ban_routes, mutex_routes):
        super().__init__()
        self.type = 'cp'
        self.entry_signals = []
        for i in range(num_ports):
            self.entry_signals.append(HomeSignal('null', i))
        self.in_ports = [i for i in range(num_ports)]
        self.out_ports = [i for i in range(num_ports)]
        self.open_direction = {}
        for i in self.in_ports:
            for j in self.out_ports:
                if ban_routes[i] != j:
                    self.open_direction[i] = j
        assert {None} == set([self.open_direction.get(k) for k in ban_routes.keys()])
        self.current_route = []

    def open_route(self, route, condition='fav'):
        assert route not in self.current_route
        self.current_route.append(route)
        self.entry_signals[route[0]].clear(condition=condition)
        for r in self.mutex_routes[route]:
            if r in self.current_route:
                self.close_route(r)
        self.listener_updates(obj=('cleared', route))

    def close_route(self, route):
        assert route in self.current_route
        self.current_route.remove(route)
        self.entry_signals[route[0]].close()
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
        self.open_direction = direction
        self.listener_updates()
