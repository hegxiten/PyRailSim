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

    def change_color_to(self, color, isNotified=True):
        
        new_aspect = Aspect(color)

        print("\t {} signal {} changed from {} to {}".format(self.facing_direction, str(self.pos), self.aspect.color, color))
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)

class AutoSignal(Signal):
    def __init__(self, pos, facing_direction):
        super().__init__(pos, facing_direction)
        self.aspect = Aspect('g')
        self.type = 'abs'
        self.lock = False
    
    def update(self, observable, update_message):
        assert observable.type in ['abs','home','block']
        # print("{} signal {} is observing {} signal {}".format(self.facing_direction, self.pos, observable.facing_direction, observable.pos))
        # print("Because {} signal {} changed from {} to {}:".format(observable.facing_direction, str(observable.pos), update_message['old'].color, update_message['new'].color))
        
        if observable.type == 'block':
            if update_message:
                self.lock = True
                self.change_color_to('r')
        elif observable.type == 'home' and observable.facing_direction != self.facing_direction:
            if update_message.color != 'r':
                self.change_color_to('r', False)
        else:
            if update_message.color == 'yy':                         # observable:        g -> yy
                self.change_color_to('g')                                   # observer:            -> g
            elif update_message.color == 'y':                        # observable:     g/yy -> y
                self.change_color_to('yy')                                  # observer:            -> yy
            elif update_message.color == 'r':                        # observable: g/yy/y/r -> r
                self.change_color_to('y')                                   # observer:            -> g

class HomeSignal(Signal):
    def __init__(self, pos, facing_direction):
        super().__init__(pos, facing_direction)
        self.aspect = Aspect('g')
        self.type = 'home'

    def update(self, observable, update_message):
        if observable.type == 'block':
            if update_message:      # block 有车
                self.change_color_to('r')
        elif observable.type == 'home':
            if update_message.color != 'r':                          # 反向主体信号非红                 
                self.change_color_to('r', False)

        elif observable.type == 'abs' and 同时还放车进入下一个abs:
            if update_message.color == 'yy':                         # observable:        g -> yy
                self.change_color_to('g')                                   # observer:            -> g
            elif update_message.color == 'y':                        # observable:     g/yy -> y
                self.change_color_to('yy')                                  # observer:            -> yy
            elif update_message.color == 'r':                        # observable: g/yy/y/r -> r
                self.change_color_to('y')  
        elif observable.type == 'home' and observable.facing_direction != self.facing_direction:
            if update_message.color != 'r':                          # 反向主体信号非红                 
                self.change_color_to('r')

class BlockTrack(Observable):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.__occupiers = []
        self.type = 'block'

    @property
    def occupiers(self):
        return self.__occupiers

    def has_occupier(self):
        return False if not self.__occupiers else True

    def monitor_block(self, add_occupier=None, remove_occupier=None):
        if add_occupier:
            self.__occupiers.append(add_occupier)
        elif remove_occupier:
            self.__occupiers.remove(remove_occupier)
        self.listener_updates(obj=self.__occupiers)

if __name__ == '__main__':
    left_signals= [HomeSignal(0, 'left', 'trailingmain')] + [AutoSignal(i, 'left') for i in range(1,9)] + [HomeSignal(9, 'left', 'main')]
    right_signals = [HomeSignal(0, 'right', 'main')] + [AutoSignal(i, 'right') for i in range(1,9)] + [HomeSignal(9, 'right', 'trailingmain')]
    blocks = [BlockTrack(i) for i in range(9)]
    def registersignal():
        for i in range(1,10):
            left_signals[i].add_observer(left_signals[i-1])
        for i in range(0,9):
            right_signals[i].add_observer(right_signals[i+1])
        
        for i in right_signals:
            if i.type == 'abs':
                left_signals[0].add_observer(i)
        for i in left_signals:
            if i.type == 'abs':
                right_signals[9].add_observer(i)
        
    def initialize():
        for i in left_signals + right_signals:
            if i.type == 'home':
                i.change_color_to('r')

    def registerblock():
        for i in range(9):
            blocks[i].add_observer(left_signals[i])
            blocks[i].add_observer(right_signals[i+1])

    registersignal()
    #registerblock()
    initialize()

    '''
    Print observers
    '''
    # for i in left_signals + right_signals:
    #     print((i.__class__.__name__, i.pos, i.type, i.facing_direction),'  \t\tobservers:', [(j.__class__.__name__, j.pos, j.facing_direction) for j in i._Observable__observers])

    # for i in blocks:
    #     print((i.__class__.__name__, i.pos, i.type),'  \t\t\tobservers:', [(j.__class__.__name__, j.pos, j.facing_direction) for j in i._Observable__observers])

    print('left :',[s.aspect.color for s in left_signals])
    print('right:',[s.aspect.color for s in right_signals])
    print('pos   ',[str(i) for i in range(10)])

    # left_signals[0].change_color_to('g')
    right_signals[9].change_color_to('g')
    
    print('\n')
    print('left :',[s.aspect.color for s in left_signals])
    print('right:',[s.aspect.color for s in right_signals])
    print('pos   ',[str(i) for i in range(10)])
