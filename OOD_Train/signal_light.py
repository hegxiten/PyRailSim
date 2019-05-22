from aspect import Aspect

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
        new_aspect = Aspect(color)
        self.aspect.color = color
        if color == 'g':
            self.tgt_sp = self.allow_sp
        elif color == 'yy':
            self.tgt_sp = self.allow_sp * 3 / 4
        elif color == 'y':
            self.tgt_sp = self.allow_sp / 2
        else:
            self.tgt_sp = 0
        self.listener_updates(obj=new_aspect)

    def update(self, observable, new_aspect):
        if observable.facing_direction == self.facing_direction:
            if new_aspect < self.aspect:                    # observable drops down
                if new_aspect.color == 'yy':                # observable:      g -> yy
                    self.change_color_to('g')               # observer:          -> g
                elif new_aspect.color == 'y':               # observable:   g/yy -> y
                    self.change_color_to('yy')              # observer:          -> yy
                elif new_aspect.color == 'r':               # observable: g/yy/y -> r
                    self.change_color_to('y')               # observer:          -> y
            if new_aspect > self.aspect:                    # observable clears up
                if new_aspect.color == 'y':                 # observable:      r -> y
                    self.change_color_to('yy')              # observer:          -> yy
                elif new_aspect.color == 'yy':              # observable:    r/y -> yy
                    self.change_color_to('g')               # observer:          -> g
                elif new_aspect.color == 'g':               # observable: r/y/yy -> g
                    self.change_color_to('g')               # observer:          -> g
        if observable.facing_direction != self.facing_direction:
            if new_aspect.color != 'r':                     # 任意反向信号非红                 
                self.change_color_to('r')

if __name__ == '__main__':
    '''
    测试代码
    '''
    left_signal = [Signal(i, 'abs', 'left', 70) for i in range(8)]
    right_signal = [Signal(i, 'abs', 'right', 70) for i in range(8)]

    for i in range(7):
        left_signal[i].add_observer(left_signal[i+1])
    for i in range(1,8):
        right_signal[i].add_observer(right_signal[i-1])
    # add the signal ahead as observer (self being observed by the signal facing ahead)

    for i in range(8):
        for j in range(8):
            left_signal[i].add_observer(right_signal[j])
            right_signal[i].add_observer(left_signal[j])


    print('left :',[s.aspect.color for s in left_signal])
    print('right:',[s.aspect.color for s in right_signal])

    left_signal[3].change_color_to('y')     # 测试信号变化

    print('left :',[s.aspect.color for s in left_signal])
    print('right:',[s.aspect.color for s in right_signal])
