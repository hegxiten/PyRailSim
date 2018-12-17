import networkx as nx
import matplotlib.pyplot as plt
import collections

def networkX_write():
    '''
    generate a network graph and output it into 'gpickle' file
    '''
    number = 30
    G = nx.Graph()

    # define the position of all nodes, it should be a dictionary
    pos = {}

    for i in range(1, number+1):
        col = ((i-1) % 10) + 1 if ((i-1) // 10) % 2 == 0 else 10 - (i-1) % 10
        row = i // 10 if i % 10 != 0 else i // 10 - 1
        pos[i] = [col, row]

    nodes = []
    edges = []
    for i in range(1, number+1):
        nodes.append(i)
        if i < number:
            edges.append((i, i+1))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_node_attributes(G, pos, 'pos')
    nx.write_gpickle(G, "a.gpickle")

def networkX_read():
    '''
    read "gpickle" file
    dynamic display the node: change the color of a node from red to green every second.
    '''

    G = nx.read_gpickle("a.gpickle")
    pos = nx.get_node_attributes(G, 'pos')

    ncolor = []
    for i in range(len(pos)):
        ncolor.append('r')

    #plt.ion()
    for index in range(len(ncolor)):
        plt.cla()
        ncolor[index] = 'g'
        if index > 0:
            ncolor[index-1] = 'r'
        nx.draw_networkx_nodes(G, pos, node_color = ncolor)
        nx.draw_networkx_labels(G, pos, font_size=16)
        nx.draw_networkx_edges(G, pos)

        plt.pause(0.05)
    #plt.ioff()
    plt.show()
    #plt.pause(0.2)
    plt.cla()
    plt.close('all')
    return

'''
# code in main class
import networkX_w_r
networkX_w_r.networkX_write()
networkX_w_r.networkX_read()
'''
