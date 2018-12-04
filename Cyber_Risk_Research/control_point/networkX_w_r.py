import networkx as nx
import matplotlib.pyplot as plt
import collections

def networkX_write():
    '''
    generate a network graph and output it into 'gpickle' file
    '''
    number = 30
    G = nx.Graph()
    nodes = []
    edges = []
    for i in range(number):
        nodes.append(i + 1)
        if i < number - 1:
            edges.append((i+1, i+2))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
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

        plt.pause(0.1)
    #plt.ioff()
    plt.show()
    plt.pause(1)
    plt.close('all')
    return

'''
# code in main class
import networkX_w_r
networkX_w_r.networkX_write()
networkX_w_r.networkX_read()
'''
