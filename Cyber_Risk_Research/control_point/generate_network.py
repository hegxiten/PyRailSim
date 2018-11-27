import networkx as nx


def drawnet():
    '''
    generate a network graph and output it into 'gpickle' file
    '''

    G = nx.Graph()
    nodes = [1, 2, 3, 4, 5, 6]
    G.add_nodes_from(nodes)
    edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    nx.set_node_attributes(G, pos, 'pos')
    nx.write_gpickle(G, "a.gpickle")