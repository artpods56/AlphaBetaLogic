import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

# def find_leaf_nodes(graph, start_node):
#     leaf_nodes = []
#     successors = [x[1] for x in graph if x[0] == start_node]
#     print(successors)
#     if len(successors) == 0:
#         leaf_nodes.append(start_node)
#     else:
#         for successor in successors:
#             #print(successor)
#             leaf_nodes.extend(find_leaf_nodes(graph, successor))
#     return leaf_nodes
#
# # Przykładowy graf drzewa
# G = nx.DiGraph()
# G.add_edges_from([(1, 2),(1,2 ) , (1, 3), (2, 4), (2, 5), (3, 6), (4, 7), (4, 8)])
# connections = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (4, 7), (4, 8)]
# node_labels = {node: node for node in G.nodes}
#
# # Rysowanie grafu z etykietami
#
# # Początkowy węzeł
# start_node = 1
#
# # Znajdowanie końców każdego rozgałęzienia
# leaf_nodes = find_leaf_nodes(connections, 1)
# pos = nx.spring_layout(G)  # Ustalamy układ węzłów
# nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=500, node_color='lightblue', font_size=12, font_weight='bold')
# nx.draw_networkx_nodes(G, pos, nodelist=leaf_nodes, node_color='salmon')  # Oznaczamy końce rozgałęzień innym kolorem
# plt.show()
# print("Końce rozgałęzień:")
# for node in leaf_nodes:
#     print(node)

import networkx as nx
import matplotlib.pyplot as plt

connections = [(1, 2), (1, 2, 2), (2, 4), (2, 5)]

# Create a directed graph
G = nx.DiGraph()

# Add connections as edges
for connection in connections:
    G.add_edge([connection[0], connection[1]])

# Create labels with unique identifiers
node_labels = {node: f"{node[0]}-{node[1]}" if len(node) > 2 else f"{node[0]}" for node in connections}

# Draw the graph with labels
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, labels=node_labels, node_color='lightblue', node_size=500, font_size=12, font_weight='bold')
plt.show()