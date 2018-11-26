import networkx as nx
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def drawnet():

    plt.figure(figsize=(8, 6), dpi=80)

    G = nx.Graph()

    tuple = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (4, 8), (5, 8), (3, 7)]
    G.add_edges_from(tuple)
    nx.draw(G, node_size=500)


    plt.ion()

    for index in range(10):
        #plt.cla()

        G[1][3]['color'] = 'blue'


        plt.pause(0.1)

    plt.ioff()

    plt.show()
    return
drawnet()


