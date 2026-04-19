import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def random_graph(vertice_count=None, edge_chance=0.3, taux_fermeture=0.1):
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
    G = nx.from_numpy_array(np.array(edges))

    for (i,j) in G.edges():
        G[i][j][('close')] = False

    aretes_clients = [(i,j) for (i,j) in G.edges() if i != 0 and j != 0]
    nb_close = int(len(aretes_clients) * taux_fermeture)

    if nb_close > 0:
        aretes_a_fermer = random.sample(aretes_clients, nb_close)
        for (i, j) in aretes_a_fermer:
            G[i][j]['close'] = True
    return G



### Affichage

G = random_graph(25, edge_chance=0.05, taux_fermeture=0.1)

couleurs = []
for node in G.nodes():
    if node == 0:
        couleurs.append('red')
    else:
        couleurs.append('white')

aretes_ouvertes = [(i, j) for (i, j) in G.edges() if not G[i][j]['close']]
aretes_fermees = [(i, j) for (i, j) in G.edges() if G[i][j]['close']]


plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=2, iterations=100)

nx.draw_networkx_edges(G, pos, edgelist=aretes_ouvertes,
                       edge_color='black', width=1)

nx.draw_networkx_edges(G, pos, edgelist=aretes_fermees,
                       edge_color='red', width=1.5, style='dashed')

nx.draw_networkx_nodes(G, pos, node_color=couleurs,
                       node_size=300, edgecolors='black')

nx.draw_networkx_labels(G, pos, font_size=9)



plt.show()



