class Observable(object):
    '''
    被观察的对象，实现类需要具体增加被监听的资源
    '''
    def __init__(self):
        self._observers = []

    @property
    def observers(self):
        return self._observers
        
    def has_observer(self):
        return False if not self._observers else True

    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
        
    def remove_observer(self, observer):
        self._observers.remove(observer)

    def listener_updates(self, obj=None):
        for observer in self._observers:
            observer.update(self, obj)

class Observer(object):
    '''
    观察者，当观察的对象发生变化时，依据变化情况增加处理逻辑
    '''
    def update(self, observable, obj):
        pass