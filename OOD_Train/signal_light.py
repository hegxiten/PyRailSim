from aspect import Aspect

class Observable(object):
    '''
    被观察的对象，实现类需要具体增加被监听的资源
    '''
    def __init__(self):
        self.observers = []

    @property
    def observers(self):
        return self.observers

    def has_observer(self):
        return False if not self.observers else True

    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)
        
    def remove_observer(self, observer):
        self.observers.remove(observer)

    def listener_updates(self, obj=None):
        for observer in self.observers:
            observer.update(self, obj)

class Observer(object):
    '''
    观察者，当观察的对象发生变化时，依据变化情况增加处理逻辑
    '''
    def update(self, observable, obj):
        pass

class Signal(Observable, Observer):
    def __init__(self, port_idx):
        super().__init__()
        self.port_idx = port_idx
        self.aspect = Aspect(None)
        self.type = None

    def change_color_to(self, color, isNotified=True):
        
        new_aspect = Aspect(color)

        print("\t {} signal changed from {} to {}".format(self.port_idx, self.aspect.color, color))
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)

class AutoSignal(Signal):
    def __init__(self, port_idx):
        super().__init__(port_idx)
        if (port_idx % 2) == 0:
            self.facing_direction = 'L'
        else:
            self.facing_direction = 'R'
        self.aspect = Aspect('g')
        self.type = 'abs'
    
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
    def __init__(self, port_idx, track_number):
        super().__init__(port_idx)
        self.aspect = Aspect('r')
        self.type = 'home'
        self.hs_type = 'A'

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

class BlockTrack(Observable):
    def __init__(self):
        super().__init__()
        self.occupiers = []
        self.type = 'block'

    @property
    def occupiers(self):
        return self.occupiers

    def has_occupier(self):
        return False if not self.occupiers else True

    def monitor_block(self, add_occupier=None, remove_occupier=None):
        if add_occupier:
            self.occupiers.append(add_occupier)
        elif remove_occupier:
            self.occupiers.remove(remove_occupier)
        self.listener_updates(obj=self.occupiers)

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
