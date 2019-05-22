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
        if observer not in self.__observers:
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
    def __init__(self, pos, facing_direction):
        super().__init__()
        self.pos = pos
        self.facing_direction = facing_direction
        self.aspect = Aspect(None)
        self.type = None

    def change_color_to(self, color):
        new_aspect = Aspect(color)
        old_aspect = self.aspect
        print("\t {} signal {} changed from {} to {}".format(self.facing_direction, str(self.pos), self.aspect.color, color))
        self.aspect = new_aspect
        aspect_update = {'old': old_aspect, 'new': new_aspect}
        self.listener_updates(obj=aspect_update)
    
    def update(self, observable, update_message):
        # print("{} signal {} is observing {} signal {}".format(self.facing_direction, self.pos, observable.facing_direction, observable.pos))
        # print("Because {} signal {} changed from {} to {}:".format(observable.facing_direction, str(observable.pos), update_message['old'].color, update_message['new'].color))
        if observable.facing_direction == self.facing_direction:
            if update_message['new'] < update_message['old']:                  # observable drops down
                if update_message['new'].color == 'yy':                         # observable:        g -> yy
                    self.change_color_to('g')                                   # observer:            -> g
                elif update_message['new'].color == 'y':                        # observable:     g/yy -> y
                    self.change_color_to('yy')                                  # observer:            -> yy
                elif update_message['new'].color == 'r':                        # observable: g/yy/y/r -> r
                    self.change_color_to('y')                                   # observer:            -> y
            if update_message['new'] > update_message['old']:                  # observable clears up
                if update_message['new'].color == 'y':                          # observable:        r -> y
                    self.change_color_to('yy')                                  # observer:            -> yy
                elif update_message['new'].color == 'yy':                       # observable:      r/y -> yy
                    self.change_color_to('g')                                   # observer:            -> g
                elif update_message['new'].color == 'g':                        # observable: r/y/yy/g -> g
                    self.change_color_to('g')                                   # observer:            -> g
        if observable.facing_direction != self.facing_direction:
            if observable.type == 'abs':
                if update_message['new'].color != 'r':                          # 任意反向信号非红                 
                    self.change_color_to('r')

class AutomaticBlockSignal(Signal):
    def __init__(self, pos, facing_direction):
        super().__init__(pos, facing_direction)
        self.aspect = Aspect('g')
        self.type = 'abs'

class HomeSignal(Signal):
    def __init__(self, pos, facing_direction, route):
        super().__init__(pos, facing_direction)
        self.aspect = Aspect('r')
        self.type = 'home'



if __name__ == '__main__':
    '''
    测试代码
    '''
    left_signals= [HomeSignal(0, 'left', 'trailingmain')] + [AutomaticBlockSignal(i, 'left') for i in range(1,9)] + [HomeSignal(9, 'left', 'main')]
    right_signals = [HomeSignal(0, 'right', 'main')] + [AutomaticBlockSignal(i, 'right') for i in range(1,9)] + [HomeSignal(9, 'right', 'trailingmain')]
    def register():
        for i in range(1,10):
            left_signals[i].add_observer(left_signals[i-1])
        for i in range(0,9):
            right_signals[i].add_observer(right_signals[i+1])
        for i in range(0,10):
            left_signals[i].add_observer(right_signals[i])
            right_signals[i].add_observer(left_signals[i])
    
    register()
    for i in left_signals:
        print((i.pos, i.type, i.facing_direction),'  \tobservers:', [(j.pos, j.type, j.facing_direction) for j in i._Observable__observers])

    print('left :',[s.aspect.color for s in left_signals])
    print('right:',[s.aspect.color for s in right_signals])

    left_signals[9].change_color_to('y')

    print('left :',[s.aspect.color for s in left_signals])
    print('right:',[s.aspect.color for s in right_signals])
