class Observable(object):
    '''
    被观察的对象，实现类需要具体增加被监听的资源
    '''
    def __init__(self):
        self.__observers = []

    @property
    def observers(self):
        return self.__observers

    def has_observer(self):
        return False if not self.__observers else True

    def add_observer(self, observer):
        self.__observers.append(observer)

    def remove_observer(self, observer):
        self.__observers.remove(observer)

    def listener_updates(self, obj=None):
        for observer in self.__observers:
            observer.update(self, obj)
            
from aspect import Aspect

class Observer(object):
    '''
    观察者，当观察的对象发生变化时，依据变化情况增加处理逻辑
    '''
    def update(self, observable, obj):
        pass

class Signal(Observable, Observer):
    def __init__(self, index, type, facing_direction, allow_sp):
        super().__init__()
        self.index = index
        self.aspect = Aspect('g')
        self.allow_sp = allow_sp
        self.tgt_sp = 0
        self.type = type
        self.facing_direction = facing_direction
    def change_color_to(self, color):
        self.aspect.color = color
        if color == 'g':
            self.color = 'g'
            self.tgt_sp = self.allow_sp
        elif color == 'yy':
            self.color = 'yy'
            self.tgt_sp = self.allow_sp * 3 / 4
        elif color == 'y':
            self.color = 'y'
            self.tgt_sp = self.allow_sp / 2
        else:
            self.color = 'r'
            self.tgt_sp = 0
        new = self
        self.listener_updates(obj=new)
    def update(self, observing_old, observing_new):
        if observing_new.aspect < observing_old.aspect:        # 同向下一个信号降灯
            if observing_new.aspect.color == 'yy':             # g -> yy
                self.aspect.color = 'g'
                self.tgt_sp = self.allow_sp 
            elif observing_new.aspect.color == 'y':            # yy -> y
                self.aspect.color = 'yy'
                self.tgt_sp = self.allow_sp * 3 / 4
            elif observing_new.aspect.color == 'r':            # y -> r
                self.aspect.color = 'y'
                self.tgt_sp = self.allow_sp / 2
        if observing_new > observing_old.aspect:        # 同向下一个信号升灯
            if observing_new.aspect.color == 'y':       # r -> y
                self.aspect.color = 'yy'
                self.tgt_sp = self.allow_sp * 3 / 4
            elif observing_new.aspect.color == 'yy':    # y -> yy
                self.aspect.color = 'g'
                self.tgt_sp = self.allow_sp
        if observing_new.aspect.color != 'r':           # 反向同位置信号非红
            self.aspect.color = 'r'
            self.tgt_sp = 0

if __name__ == '__main__':
    left_signal = [Signal(i, 'abs', 'left', 70) for i in range(8)]
    right_signal = [Signal(i, 'abs', 'right', 70) for i in range(8)]
    for i in range(8):
        left_signal[i].add_observer(right_signal[i])
        right_signal[i].add_observer(left_signal[i])
    
    for i in range(1,8):
        left_signal[i].add_observer(left_signal[i-1])
        right_signal[i].add_observer(right_signal[i-1])

    print('left :',[s.aspect.color for s in left_signal])
    print('right:',[s.aspect.color for s in right_signal])

    left_signal[3].change_color_to('yy')

    print('left :',[s.aspect.color for s in left_signal])
    print('right:',[s.aspect.color for s in right_signal])