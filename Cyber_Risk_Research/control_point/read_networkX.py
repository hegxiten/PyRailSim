import networkx as nx
import matplotlib.pyplot as plt


def drawnet():
    '''
    read "gpickle" file
    dynamic display the node: change the color of a node from red to green every second.
    '''

    G = nx.read_gpickle("a.gpickle")
    pos = nx.get_node_attributes(G, 'pos')

    labels = {}
    labels[1] = r'$1$'
    labels[2] = r'$2$'
    labels[3] = r'$3$'
    labels[4] = r'$4$'
    labels[5] = r'$5$'
    labels[6] = r'$6$'

    ncolor = ['r', 'r', 'r', 'r', 'r', 'r']

    plt.ion()
    for index in range(6):
        plt.cla()

        ncolor[index] = 'g'
        if index > 0:
            ncolor[index-1] = 'r'
        nx.draw_networkx_nodes(G, pos, node_color = ncolor)
        nx.draw_networkx_labels(G, pos, labels, font_size=16)
        nx.draw_networkx_edges(G, pos)

        plt.pause(1)
    plt.ioff()

    plt.show()
    return

drawnet()