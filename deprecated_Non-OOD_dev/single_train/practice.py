from SimPy.Simulation import *

class Train(Process):
    def __init__(self, t_num,cc):
        Process.__init__(self)  # manually call __init__ of the superclass to initialize process object 
        self.t_num = t_num
        self.cc = cc
        '''
        self.speed = speed
        self.rank = collections.defaultdict(int)
        self.weight = collections.defaultdict(int)
        '''
        
    def go(self):
         print now( ), self.t_num, "Starting"
         yield hold,self,100.0
         print now( ), self.t_num, "Arrived"

initialize( )
t1  = Train("Train1",2000)           # a new train
activate(t1,t1.go( ),at=6.0)    # activate at time 6.0
t2  = Train("Train2",1600)           # another new train
activate(t2,t2.go( ))           # activate at time 0
simulate(until=200)
print 'Current time is ',now( ) # will print 106.0
