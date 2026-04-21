import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from functools import reduce

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

G = random_graph(25, k_voisins=4, taux_fermeture=0.1, taux_surcout=0.08, complet=True)
couleurs = ['red'] + ['white' for _ in range(len(G) - 1)]
aretes_normales = [(i, j) for (i, j) in G.edges() if not G[i][j]['close'] and not G[i][j]['surcout']]
aretes_fermees = [(i, j) for (i, j) in G.edges() if G[i][j]['close']]
aretes_surcout = [(i, j) for (i, j) in G.edges() if G[i][j]['surcout']]

vehicle_count = 3

def genetic_algorithm_vrp_advanced(G, num_vehicles, pop_size=50, generations=100):
    # --- 1. Vérification de la faisabilité ---
    # Chaque véhicule doit pouvoir sortir et revenir au dépôt (nœud 0)
    # Note : G.degree(0) compte le nombre d'arêtes connectées au dépôt.
    if G.degree(0) < num_vehicles * 2:
        raise ValueError(f"Problème insoluble : Le dépôt a un degré de {G.degree(0)}, "
                         f"mais il faut au moins {num_vehicles * 2} arêtes pour {num_vehicles} véhicules.")
    
    nodes = [n for n in G.nodes if n != 0]
    
    # --- 2. Fonctions de Coût ---
    def get_edge_cost(u, v):
        if not G.has_edge(u, v) or G[u][v].get('close', False):
            return float('inf')
        
        return G[u][v].get('cout', 1)
    
    def fitness(individual):
        total_cost = 0
        for route in individual:
            if not route: continue
            
            # Trajet : Dépôt -> Clients -> Dépôt
            full_path = [0] + route + [0]
            route_cost = 0
            for i in range(len(full_path) - 1):
                cost = get_edge_cost(full_path[i], full_path[i+1])
                if cost == float('inf'): return float('inf')
                route_cost += cost
            total_cost += route_cost
        return total_cost
    
    def chromosome_pratiquable(individual):
        for route in individual:
            if not route:
                continue
            
            # Trajet : Dépôt -> Clients -> Dépôt
            full_path = [0] + route + [0]
            for i in range(len(full_path) - 1):
                u = full_path[i]
                v = full_path[i+1]
                if not G.has_edge(u, v) or G[u][v].get('close', False):
                    return False
        return True
    
    # --- 3. Initialisation de la Population ---
    # Chaque individu est une liste de m sous-listes
    def create_individual():
        shuffled = random.sample(nodes, len(nodes))
        # Découpe aléatoire en m segments pour varier les tailles de tournées
        splits = sorted(random.sample(range(1, len(nodes)), num_vehicles))
        return [list(x) for x in np.split(shuffled, splits)]
    
    population = [create_individual() for _ in range(pop_size)]
    
    # --- 4. Boucle Génétique ---
    for gen in range(generations):
        # Tri par fitness
        population = sorted(population, key=lambda x: fitness(x))
        
        # Garder le meilleur (Élitisme)
        new_gen = population[:2]
        
        while len(new_gen) < pop_size:
            # Sélection par tournoi
            parent1, parent2 = random.sample(population[:pop_size//2], 2)
            
            # Crossover simplifié (Échange de routes entières entre véhicules)
            # Pour respecter "chaque sommet une seule fois", on ré-aplatit et on croise
            flat_p1 = [item for sublist in parent1 for item in sublist]
            flat_p2 = [item for sublist in parent2 for item in sublist]
            
            # Ordered Crossover (OX) sur la version plate
            start, end = sorted(random.sample(range(len(nodes)), 2))
            child_flat = [None] * len(nodes)
            child_flat[start:end] = flat_p1[start:end]
            
            rem = [n for n in flat_p2 if n not in child_flat]
            cursor = 0
            for i in range(len(child_flat)):
                if child_flat[i] is None:
                    child_flat[i] = rem[cursor]
                    cursor += 1
            
            # Re-découpage en sous-chromosomes
            # On conserve les longueurs des routes du parent 1
            child = []
            curr = 0
            for route in parent1:
                child.append(child_flat[curr:curr+len(route)])
                curr += len(route)
            
            # Mutation : Échange de deux villes entre deux véhicules
            if random.random() < 0.2:
                v1, v2 = random.sample(range(num_vehicles), 2)
                if child[v1] and child[v2]:
                    idx1 = random.randrange(len(child[v1]))
                    idx2 = random.randrange(len(child[v2]))
                    child[v1][idx1], child[v2][idx2] = child[v2][idx2], child[v1][idx1]
            
            new_gen.append(child)
        
        population = new_gen
    
    best = min(population, key=lambda x: fitness(x))
    return best, fitness(best)

try:
    while True:
        best_routes, total_cost = genetic_algorithm_vrp_advanced(G, num_vehicles=2, pop_size=200)
        if len(G) == sum(list(map(len, best_routes))) + 1:
            break
    print(f"Nombre de sommets client : {len(G) - 1}")
    print("Solution trouvée :")
    for i, r in enumerate(best_routes):
        print(f" Véhicule {i+1} : 0 -> {' -> '.join(map(str, r))} -> 0")
    print(f"Coût total : {total_cost}")
    
    show()
except ValueError as e:
    print(e)
