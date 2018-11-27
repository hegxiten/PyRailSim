import networkx as nx
import matplotlib.pyplot as plt
G = nx.cubical_graph()
plt.subplot(121)
nx.draw(G)
plt.subplot(122)
nx.draw(G,pos=nx.random_layout(G),nodecolor='r',edge_color='b')
plt.show()