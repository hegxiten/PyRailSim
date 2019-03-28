from SimPy.Simulation import *
from math import sqrt
from random import randint
from itertools import cycle
import matplotlib.pyplot as plt
import networkx as nx

class RailNetwork(nx.Graph):
    def __init__(self, sim_data=None, **attr):  #sim_data is designed as a dictionary containing simulation setting information for the RailNetwork
        super(RailNetwork, self).__init__()
        self.sim_data = sim_data



if __name__ == '__main__':
    n = RailNetwork()
    n.add_nodes_from([2,3])
    print(n.nodes)
    nx.draw(n)
    plt.show()