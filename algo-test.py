import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from functools import reduce

def random_graph(vertice_count=None, k_voisins=3, taux_fermeture=0.1, taux_surcout=0.08, facteur_surcout=2.0):
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
            if all(np.sqrt((x - xp) ** 2 + (y - yp) ** 2) >= distance_min
                   for (xp, yp) in positions.values()):
                positions[i] = (x, y)
                break
        else:
            positions[i] = (x, y)

    # Connecter chaque sommet à ses k plus proches voisins
    edges = [[0 for _ in range(vertice_count)] for _ in range(vertice_count)]
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

def show():
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

G = random_graph(25, k_voisins=3, taux_fermeture=0.1, taux_surcout=0.08)
couleurs = ['red'] + ['white' for _ in range(len(G) - 1)]
aretes_normales = [(i, j) for (i, j) in G.edges() if not G[i][j]['close'] and not G[i][j]['surcout']]
aretes_fermees = [(i, j) for (i, j) in G.edges() if G[i][j]['close']]
aretes_surcout = [(i, j) for (i, j) in G.edges() if G[i][j]['surcout']]

vehicle_count = 3

def genetic_algorithm_vrp_nx(G, num_vehicles, pop_size=100, generations=200):
    """
    G: Graphe NetworkX (chaque arête peut avoir 'cout', 'surcout', 'close')
    num_vehicles: Nombre de véhicules (m)
    """
    # Liste des clients (tous les nœuds sauf le dépôt '0')
    nodes = [n for n in G.nodes if n != 0]
    n_total = len(nodes)
    
    def calculate_route_cost(route):
        if not route: return 0
        total = 0
        # On part du dépôt, on fait la tournée, on revient au dépôt
        full_path = [0] + route + [0]
        
        for i in range(len(full_path) - 1):
            u, v = full_path[i], full_path[i+1]
            
            if not G.has_edge(u, v):
                total += 1e9 # Pas de chemin direct
                continue
                
            edge_data = G[u][v]
            
            # Contrainte : Arête bloquée
            if edge_data.get('close', False):
                total += 1e9
            else:
                # Distance + Surcoût
                total += edge_data.get('cout', 1)
        return total
    
    def fitness(chromosome):
        # Séparation en m véhicules
        routes = np.array_split(chromosome, num_vehicles)
        return sum(calculate_route_cost(list(r)) for r in routes)
    
    # --- Initialisation de la population ---
    population = [random.sample(nodes, n_total) for _ in range(pop_size)]
    print(population)
    
    for gen in range(generations):
        # Tri par performance (coût croissant)
        population = sorted(population, key=lambda x: fitness(x))
        
        # Elitisme : on garde le top 10%
        new_gen = population[:int(pop_size * 0.1)]
        
        while len(new_gen) < pop_size:
            # Sélection par tournoi
            p1, p2 = random.sample(population[:50], 2)
            
            # Crossover (Ordered Crossover OX1)
            start, end = sorted(random.sample(range(n_total), 2))
            child = [None] * n_total
            child[start:end] = p1[start:end]
            
            remaining = [item for item in p2 if item not in child]
            idx = 0
            for i in range(n_total):
                if child[i] is None:
                    child[i] = remaining[idx]
                    idx += 1
            
            # Mutation (Swap)
            if random.random() < 0.15:
                a, b = random.sample(range(n_total), 2)
                child[a], child[b] = child[b], child[a]
                
            new_gen.append(child)
        
        population = new_gen
    
    # Extraction du meilleur résultat
    best_chrom = min(population, key=lambda x: fitness(x))
    best_routes = [list(r) for r in np.array_split(best_chrom, num_vehicles)]
    
    return best_routes, fitness(best_chrom)

# Exécution
routes, total_cost = genetic_algorithm_vrp_nx(G, num_vehicles=vehicle_count)

print(f"Tournées par véhicule : {routes}")
print(f"Coût total calculé : {total_cost}")
