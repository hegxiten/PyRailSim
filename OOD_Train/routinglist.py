class RoutingNode(object):
    def __init__(self):
        self.next = None
        self.prev = None
        self.curr_routinglist = None

class RoutingList(object):
    def __init__(self, head=None):
        self.head = head
        
    @property
    def tail(self):
        return self.index(self.length - 1)
    
    def add(self,value):
        p = self.head
        new = value
        while p.next:
            p = p.next      
        p.next = new
        new.prev = p

    def remove(self,value):
        p = self.head
        while p.next:
            if p.value == value:
                temp = p.prev
                xyz = p.next
                temp.next = xyz
                xyz.prev = temp
                break
            else:
                p = p.next

    def find(self,value):
        """return the index of a specific node"""
        p = self.head
        i = 0
        while p.next:
            if p.value == value:
                return i
            else:
                p = p.next
                i += 1

        raise AttributeError(u"can\'t find this element")

    def index(self, index):
        """return the specific node by index"""
        i = 0
        p = self.head
        while p.next:
            if i == index:
                return p.value
            else:
                i += 1
                p = p.next
        raise IndexError(u'index out of range')

    def findprev(self, value):
        """return the previous node of a specific node"""
        p = self.head       
        while 1:
            if p.value == value:
                return p.prev.value
            else:
                p = p.next
                if not p.next:
                    return p.prev.value

        raise AttributeError(u"can\'t find this element")

    def findnext(self, value):
        """return the next node of a specific node"""
        p = self.head       
        while 1:
            if p.value == value:
                return p.next.value
            else:
                p = p.next
                if not p.next:
                    return None
        raise AttributeError(u"can\'t find this element")

    def insert(self, index, value):
        """Index has to be greater or equal to 1
        """
        i = 0
        p = self.head
        new = value
        while p.next:
            if i == index:              
                temp = p.prev
                temp.next = new
                new.prev = temp
                new.next = p
                p.prev = new                                
                break
            else:
                p = p.next
                i += 1
        # if reaches here, insert into the tail of the routing list
        else:
            p.next = new
            new.prev = p

    def length(self):
        p = self.head
        i = 0
        while p.next:       
            p = p.next
            i += 1
        return i

    def output(self):
        p = self.head
        while 1:
            print(p.value)
            p = p.next
            if not p.next:
                print(p.value)
                break

    def reverse(self):
        """Reverse the linked Routing List"""
        length = self.length()
        i = 0
        p = self.head.next
        while p.next:
            p = p.next
        else:
            last = p
        first = self.head.next
        while i < length:
            first.value, last.value = last.value, first.value
            first = first.next
            last = last.prev
            i += 1
            length -= 1
    
if __name__ == '__main__':
    l=RoutingList()
    n0 = RoutingNode()
    l.head = n0
    n1=RoutingNode()
    l.add(n1)
    print(n0.next)