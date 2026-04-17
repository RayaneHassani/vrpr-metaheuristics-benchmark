import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def random_graph(vertice_count=None, edge_chance=0.3):
    if vertice_count is None:
        vertice_count = 100
    vertice_count = random.randint(10, vertice_count)

    edges = [[0 for _ in range(vertice_count)] for _ in range(vertice_count)]
    for x in range(vertice_count):
        for y in range(x+1, vertice_count):
            if random.random() <= edge_chance:
                edges[x][y] = 1
                edges[y][x] = 1

    for i in range(vertice_count):
        degree = sum(edges[i])

        while degree < 2:
            target = random.randrange(vertice_count)
            if target != i and edges[i][target] == 0:
                edges[i][target] = 1
                edges[target][i] = 1
                degree += 1
    return nx.from_numpy_array(np.array(edges))


G = random_graph(25, edge_chance=0.05)

nx.draw(G, with_labels=True, node_color='white', node_size=200)
plt.show()



