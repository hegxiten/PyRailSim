import networkx as nx
import matplotlib.pyplot as plt
from random import randint

G = nx.Graph()
# for i in range(3):
# G.add_node(i)
G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 7.5), (0, 2, 5.5)])

pos = [(1, 3), (1, 2), (2, 2)]

nx.draw(G, pos, with_labels=True, node_color='g')

# plt.xlim(0, 5)
# plt.ylim(0, 5)
plt.show()
