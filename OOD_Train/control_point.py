import networkx as nx
from signal_light import HomeSignal, Observable, Observer

class AutoPoint(Observable, Observer):
    def __init__(self):
        super().__init__()
        self.type = 'at'

class ControlPoint(AutoPoint):
    def __init__(self, left_number, right_number):
        super().__init__()
        # 初始化cp，参数为左边轨道数和右侧轨道数
        self.type = 'cp'                #用来给观察者识别信号变化来源
        self.L_entry_signals = []
        self.R_entry_signals = []
        for i in range(left_number):
            left_sgnl = HomeSignal('left')
            self.L_entry_signals.append(left_sgnl)
        for i in range(right_number):
            right_sgnl = HomeSignal('right')
            self.R_entry_signals.append(right_sgnl)
        self.open_direction = 'neutral'
        
    def open_route(self, direction, track_idx, color):
        # 打开cp中的某个方向某条通路，打开一侧的某个灯，反向的变红
        if direction == 'right' or direction == 'left':
            if direction == 'right':
                assert track_idx < len(self.L_entry_signals)
            if direction == 'left':
                assert track_idx < len(self.R_entry_signals)
            #取出通路需要改变的那一侧的信号灯以及另一侧全部需要变红的信号灯
            selected_track_signals = self.L_entry_signals if direction == 'right' else self.R_entry_signals
            other_track_signals = self.L_entry_signals if direction == 'left' else self.R_entry_signals
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
