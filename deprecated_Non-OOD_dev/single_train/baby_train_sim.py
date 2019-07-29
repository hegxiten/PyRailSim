"""
Simulation of a train network
"""
from SimPy.Simulation import *
from math import sqrt
from random import randint
from itertools import cycle
import networkx as nx


'''
将TrackNode与Íblock转化为block delay/hold process联系起来
继承networkx的node, edge与rackNode, Block的关系
'''



def timeTo(acc_const, max_spd, dist):
    """
    Given a trapezoidal velocity envelope defined by
    acc_const      constant acceleration, m/s/s
    max_spd        maximum velocity, m/s
    dist           distance, m
    return time in seconds required to travel
    """
    tA = float(max_spd)/acc_const           # time to accelerate to max_spd
    dA = acc_const*tA*tA                    # distance traveled during acceleration from 0 to max_spd and back to 0
    if (dist < dA):                         # train never reaches full speed?
        return sqrt(4.0*dist/acc_const)     # time needed to accelerate to half-way point then decelerate to destination
    else:
        return 2*tA + (dist-dA)/max_spd     # time to accelerate to max_spd plus travel at max_spd plus decelerate to destination

class Train(Process):
    def __init__(self, name, sim, accel=1.0, max_spd=50.0, passengers=0, maxPassengers=400):
        # Initialize Train instance with inheriting Process
        super(Train, self).__init__(name, sim)  # Train instance inherits Process instance (as superclass) with modification to name and sim parameters
        self.accel = accel
        self.max_spd  = max_spd
        self.p     = passengers
        self.maxP  = maxPassengers

    def acc_dec(self, acc, brake_acc, target_spd):
        pass
    
    def roll(self, route):
        # A Train action traveling along provided route, route as an iterator 
        curr_node = route.next()     
        # starting node, route iterates the instances of TrackNode class
        for dest in route:
            # travel to next node
            print "{:.1f}s: {} leaving {} for {}".format(self.sim.now(), self.name, curr_node, dest)
            yield hold, self, timeTo(self.accel, self.max_spd, curr_node.distanceTo[dest])
            # arrive at next node
            curr_node = dest
            print "{:.1f}s: {} at {}".format(self.sim.now(), self.name, curr_node)
            yield hold, self, curr_node.arrive(self)
    
    def getOff(self, num):
        if self.p >= num:
            print "  {} passengers got off".format(num)
            self.p -= num
        else:
            num = self.p
            print "  train is empty - only {} passengers got off".format(num)
            self.p = 0

    def getOn(self, num):
        if (self.maxP is None) or (self.p + num <= self.maxP):
            print "  {} passengers got on".format(num)
            self.p += num
        else:
            num = self.maxP - self.p
            print "  train is full - only {} passengers got on".format(num)
            self.p = self.maxP

class RailNetwork(nx.Graph):
    def __init__(self, sim_data=None, **attr):  #sim_data is designed as a dictionary containing simulation setting information for the RailNetwork
        super(RailNetwork, self).__init__()
        self.sim_data = sim_data



class TrackNode(object):
    def __init__(self, name, delay=5.0):
        self.name = name
        self.delay = delay
        self.distanceTo = {}
    def arrive(self, train):
        pass
    def __str__(self):
        return self.name

class Siding(TrackNode):
    def main(self, train):
        pass
    def diverge(self, train):
        pass
        
class CtrlPoint(TrackNode):
    def stop(self, train):
        pass
    def approach(self, train):
        pass
    def clear(self, train):
        pass
    
class Switch(CtrlPoint):
    def arrive(self, train):
        print("  switching tracks")
        return self.delay

class Station(TrackNode):
    def arrive(self, train):
        train.getOff(randint(1,15))
        train.getOn(randint(1,15))
        return self.delay
    
        
class SampleRailroad(Simulation):
    def run(self, maxTime=100.0):
        self.initialize()
        # create places
        x = Switch("switch x", 20.0)
        A = Station("Station A", 24.0)
        B = Station("Station B", 27.0)
        C = Station("Station C", 25.0)
        y = Switch("switch y", 18.0)
        # distances between places
        x.distanceTo[A] = 50.0
        A.distanceTo[B] = 5000.0
        B.distanceTo[C] = 2000.0
        C.distanceTo[y] = 80.0
        y.distanceTo[C] = 80.0
        C.distanceTo[B] = 2000.0
        B.distanceTo[A] = 5000.0
        A.distanceTo[x] = 50.0
        # set up first train
        sf = Train("Santa Fe 219", self)
        self.activate(sf, sf.roll(cycle([A,B,C,y,C,B,A,x])), at=0.0)
        # set up second train
        cn = Train("Canadian National 41", self, maxPassengers=200)
        self.activate(cn, cn.roll(cycle([C,B,A,x,A,B,C,y])), at=5.0)
        # start simulating!
        self.simulate(until=maxTime)

def main():
    rr = SampleRailroad()
    rr.run(800000.0)

if __name__=="__main__":
    main()