import random
from collections import deque

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def random_graph(vertice_count=None, k_voisins=4, taux_fermeture=0.1, taux_surcout=0.08, facteur_surcout=2.0, complet=False):
    if vertice_count is None:
        vertice_count = 100
    vertice_count = random.randint(10, vertice_count)

    # Positions aléatoires avec distance minimale entre sommets
    distance_min = 12
    positions = {}
    for i in range(vertice_count):
        for _ in range(200):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            if all(np.sqrt((x - xp) ** 2 + (y - yp) ** 2) >= distance_min for (xp, yp) in positions.values()):
                positions[i] = (x, y)
                break
        else:
            positions[i] = (x, y)

    # Connecter chaque sommet à ses k plus proches voisins
    edges = [[0 for _ in range(vertice_count)] for _ in range(vertice_count)]

    if complet:
        # Graphe complet : toutes les arêtes existent
        for i in range(vertice_count):
            for j in range(vertice_count):
                if i != j:
                    edges[i][j] = 1
    else:
        # Graphe des k plus proches voisins
        for i in range(vertice_count):
            distances = []
            for j in range(vertice_count):
                if i != j:
                    xi, yi = positions[i]
                    xj, yj = positions[j]
                    d = np.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                    distances.append((d, j))
            distances.sort()
            for _, j in distances[:k_voisins]:
                edges[i][j] = 1
                edges[j][i] = 1

    G = nx.from_numpy_array(np.array(edges))
    nx.set_node_attributes(G, positions, 'pos')

    # Coût de chaque arête
    for (i, j) in G.edges():
        xi, yi = positions[i]
        xj, yj = positions[j]
        G[i][j]['cout'] = np.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
        G[i][j]['close'] = False
        G[i][j]['surcout'] = False

    # --- Fermeture d'arêtes (sauf celles du dépôt) ---
    aretes_clients = [(i, j) for (i, j) in G.edges() if i != 0 and j != 0]
    nb_close = int(len(aretes_clients) * taux_fermeture)

    if nb_close > 0:
        aretes_a_fermer = random.sample(aretes_clients, nb_close)
        for (i, j) in aretes_a_fermer:
            G[i][j]['close'] = True

    # Arêtes avec surcoût
    aretes_ouvertes_clients = [(i, j) for (i, j) in G.edges()
                               if not G[i][j]['close'] and i != 0 and j != 0]
    nb_surcout = int(len(aretes_ouvertes_clients) * taux_surcout)

    if nb_surcout > 0:
        aretes_surcout_list = random.sample(aretes_ouvertes_clients, nb_surcout)
        for (i, j) in aretes_surcout_list:
            G[i][j]['cout'] *= facteur_surcout
            G[i][j]['surcout'] = True

    return G


# Affichage

G = random_graph(25, k_voisins=3, taux_fermeture=0.1, taux_surcout=0.08, complet=False)

couleurs = []
for node in G.nodes():
    if node == 0:
        couleurs.append('red')
    else:
        couleurs.append('white')

aretes_normales = [(i, j) for (i, j) in G.edges() if not G[i][j]['close'] and not G[i][j]['surcout']]
aretes_fermees = [(i, j) for (i, j) in G.edges() if G[i][j]['close']]
aretes_surcout = [(i, j) for (i, j) in G.edges() if G[i][j]['surcout']]


plt.figure(figsize=(12, 8))
pos = nx.get_node_attributes(G, 'pos')

nx.draw_networkx_edges(G, pos, edgelist=aretes_normales, edge_color='black', width=1)

nx.draw_networkx_edges(G, pos, edgelist=aretes_fermees, edge_color='red', width=1.5, style='dashed')

nx.draw_networkx_edges(G, pos, edgelist=aretes_surcout, edge_color='orange', width=2)

nx.draw_networkx_nodes(G, pos, node_color=couleurs, node_size=300, edgecolors='black')

nx.draw_networkx_labels(G, pos, font_size=9)

labels_cout = {(i, j): f"{G[i][j]['cout']:.0f}" for (i, j) in G.edges() if not G[i][j]['close']}
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels_cout, font_size=7)

plt.show()


def recherche_tabou(solution_initiale, taille_tabou, iter_max):
    nb_iter = 0
    liste_tabou = deque(maxlen=taille_tabou)

    solution_courante = solution_initiale
    meilleure_globale = solution_initiale
    valeur_meilleure_globale = cout_solution(G, solution_initiale)

    historique = [valeur_meilleure_globale]

    while nb_iter < iter_max:
        valeur_meilleure = float('inf')
        meilleure = None

        for voisin in voisinage(solution_courante):
            voisin_hashable = tuple(tuple(t) for t in voisin)

            if voisin_hashable not in liste_tabou:
                val_voisin = cout_solution(G, voisin)

                if val_voisin < valeur_meilleure:
                    valeur_meilleure = val_voisin
                    meilleure = voisin

        # Si aucun voisin valide trouvé, on arrête
        if meilleure is None:
            break

        if valeur_meilleure < valeur_meilleure_globale:
            meilleure_globale = meilleure
            valeur_meilleure_globale = valeur_meilleure
            nb_iter = 0
        else:
            nb_iter += 1

        solution_courante = meilleure

        solution_hashable = tuple(tuple(t) for t in solution_courante)
        liste_tabou.append(solution_hashable)

        historique.append(valeur_meilleure_globale)

    return meilleure_globale, historique



def voisinage(solution):
    """Génère les solutions voisines par swap intra et relocate."""
    voisins = []

    for k in range(len(solution)):
        tournee = solution[k]
        for i in range(1, len(tournee) - 1):
            for j in range(i + 1, len(tournee) - 1):
                nouvelle = [list(t) for t in solution]
                nouvelle[k][i], nouvelle[k][j] = nouvelle[k][j], nouvelle[k][i]
                voisins.append(nouvelle)

    for k1 in range(len(solution)):
        for k2 in range(len(solution)):
            if k1 == k2:
                continue
            for i in range(1, len(solution[k1]) - 1):
                for j in range(1, len(solution[k2])):
                    nouvelle = [list(t) for t in solution]
                    ville = nouvelle[k1].pop(i)
                    nouvelle[k2].insert(j, ville)
                    if len(nouvelle[k1]) >= 3:
                        voisins.append(nouvelle)

    return voisins


def cout_solution(G, solution):
    """Calcule le coût total d'une solution."""
    total = 0
    for tournee in solution:
        for idx in range(len(tournee) - 1):
            i, j = tournee[idx], tournee[idx + 1]
            if not G.has_edge(i, j) or G[i][j]['close']:
                return float('inf')
            total += G[i][j]['cout']
    return total







