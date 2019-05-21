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

    def update(self, observing, new_aspect):
        # print('^^^')
        # print(self.__dict__['index'], self.__dict__['facing_direction'], self.__dict__['aspect'].color)
        # print(observing_old.__dict__['index'], observing_old.__dict__['facing_direction'], observing_old.__dict__['aspect'].color)
        # print(observing_new.__dict__['index'], observing_new.__dict__['facing_direction'], observing_new.__dict__['aspect'].color)
        if observing.facing_direction == self.facing_direction:
            if observing.aspect < observing_old.aspect:         # observable drops down
                print('####')
                if observing_new.aspect.color == 'yy':              # observable:      g -> yy
                    self.change_color_to('g')                       # observer:          -> g
                elif observing_new.aspect.color == 'y':             # observable:   g/yy -> y
                    self.change_color_to('yy')                      # observer:          -> yy
                elif observing_new.aspect.color == 'r':             # observable: g/yy/y -> r
                    self.change_color_to('y')                       # observer:          -> y
            if observing_new.aspect > observing_old.aspect:         # observable clears up
                if observing_new.aspect.color == 'y':               # observable:      r -> y
                    self.change_color_to('yy')                      # observer:          -> yy
                elif observing_new.aspect.color == 'yy':            # observable:    r/y -> yy
                    self.change_color_to('g')                       # observer:          -> g
                elif observing_new.aspect.color == 'g':             # observable:  r/y/yy -> g
                    self.change_color_to('g')                       # observer:          -> g
        if observing_new.facing_direction != observing_old.facing_direction:
            if observing_new.aspect.color != 'r':                   # 任意反向信号非红                 
                self.change_color_to('r')

if __name__ == '__main__':
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

    left_signal[3].change_color_to('y')

    print('left :',[s.aspect.color for s in left_signal])
    print('right:',[s.aspect.color for s in right_signal])
