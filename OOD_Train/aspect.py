class Aspect(object):
    '''
    Aspect代表信号的“含义”,用于比较“大小”
    '''    
    def __init__(self, color):
        self.color = color
    
    def __eq__(self,other):
        return self.color == other.color

    def __ne__(self,other):
        return self.color != other.color

    def __lt__(self,other):
        '''
        r < y < yy < g
        '''  
        if self.color == 'r' and other.color != 'r':
            return True
        elif self.color == 'y' and (other.color == 'yy' or other.color == 'g'):
            return True
        elif self.color == 'yy' and (other.color == 'g'):
            return True
        else:
            return False

    def __gt__(self,other):
        '''
        g > yy > y > r
        '''  
        if self.color == 'g' and other.color != 'g':
            return True
        elif self.color == 'yy' and (other.color == 'y' or other.color == 'r'):
            return True
        elif self.color == 'y' and (other.color == 'r'):
            return True
        else:
            return False

    def __le__(self,other):
        '''
        r <= y <= yy <= g
        '''  
        if self.color == 'r':
            return True
        elif self.color == 'y' and (other.color != 'r'):
            return True
        elif self.color == 'yy' and (other.color == 'g' or other.color == 'yy'):
            return True
        elif self.color == 'g' and other.color == 'g':
            return True
        else:
            return False

    def __ge__(self,other):
        '''
        g >= yy >= y >= r
        '''  
        if self.color == 'g':
            return True
        elif self.color == 'yy' and (other.color != 'g'):
            return True
        elif self.color == 'y' and (other.color == 'r' or other.color == 'y'):
            return True
        elif self.color == 'r' and other.color == 'r':
            return True
        else:
            return False

if __name__ == '__main__':
    r1 = Aspect('r')
    r2 = Aspect('r')
    y1 = Aspect('y')
    y2 = Aspect('y')
    yy1 = Aspect('yy')
    g1 = Aspect('g')
    g2 = Aspect('g')

    print(y2 < yy1)