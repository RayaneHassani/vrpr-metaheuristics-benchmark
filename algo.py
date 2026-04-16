import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def random_graph(vertice_count = None, edge_chance = 0.3):
    if vertice_count is None:
        vertice_count = 100
    vertice_count = random.randint(10, vertice_count)
    '''
    edges = []
    for i in range(vertice_count):
        for y in range(vertice_count):
            if i != y and random.random() <= edge_chance:
                edges.append((i, y))
    '''
    edges = [[0 for _ in range(vertice_count)] for _ in range(vertice_count)]
    for i in range(vertice_count):
        for y in range(vertice_count):
            if i != y and random.random() <= edge_chance:
                edges[i][y] = 1
    # Tentative de bloquer les sommets avec une seule arète
    # for i in range(vertice_count):
        # if type(edges[i]) is int:
            # continue;
        # if sum([y for y in edges[i]]) == 0:
            # edges[random.randrange(0, vertice_count - 1)] = 1
    return nx.from_numpy_array(np.matrix(edges))

G = random_graph(25, edge_chance=0.05)

nx.draw(G, with_labels=True)
plt.show()

'''
class Graph:
    def __init__(self, vertices, edges):
        self.V = tuple(vertices)
        self.C = list(vertices)
        self.C.pop(self.C.index(0))
        self.C = tuple(self.C)
        self.E = tuple(edges)
    
    def __len__(self):
        return len(self.V)

def random_graph(vertice_count = None, edge_chance = 0.3):
    if vertice_count is None:
        vertice_count = 100
    vertice_count = random.randint(10, vertice_count)
    edges = [[0 for _ in range(vertice_count)] for _ in range(vertice_count)]
    for i in range(vertice_count):
        for y in range(vertice_count):
            if random.random() <= edge_chance:
                edges[i][y] = 1
    return Graph(([i for i in range(vertice_count + 1)]), edges)

def block_random_edges(G, min = 1, max = None):
    if max is None:
        max = (len(G.V) / 2) - 1
    count = random.randint(min, max)
    blocked = set()
    for i in range(count):
        rand = random.choice(G.E)
    return blocked


G = random_graph()
# le nombre total de villes à visiter, sans compter le dépôt
n = len(G.C)
# le nombre de véhicules disponibles
m = 5

F = block_random_edges(G, 1, 3)

subax1 = plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
subax2 = plt.subplot(122)
nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')

nx.draw(G)
plt.show()

#- $C_{ij}$ ∈ $\mathbb{R}^+$, $\forall$(i,j) ∈ E \ F est le coût de parcours entre la ville i et la ville j. Ce coût peut représenter un temps, une distance, un coût en carburant... en fonction du contexte : une route présentant un surcoût est modélisée par un $C_{ij}$ plus élevé que les autres routes.
'''