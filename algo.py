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


def glouton(G, nb_vehicules, k_rcl=3):
    clients_restants = set(G.nodes()) - {0}
    tournees = [[0, 0] for _ in range(nb_vehicules)]

    k = 0
    while clients_restants:
        tournee = tournees[k]
        ville_courante = tournee[-2]

        candidats = []
        for candidat in clients_restants:
            if G.has_edge(ville_courante, candidat) and not G[ville_courante][candidat]['close']:
                candidats.append((G[ville_courante][candidat]['cout'], candidat))

        if not candidats:
            for candidat in clients_restants:
                if G.has_edge(0, candidat) and not G[0][candidat]['close']:
                    candidats.append((G[0][candidat]['cout'], candidat))

            if candidats:
                candidats.sort()
                rcl = candidats[:min(k_rcl, len(candidats))]
                _, choisi = random.choice(rcl)
                tournee.insert(1, choisi)
                clients_restants.remove(choisi)
                k = (k + 1) % nb_vehicules
                continue

        if not candidats:
            k = (k + 1) % nb_vehicules
            continue

        candidats.sort()
        rcl = candidats[:min(k_rcl, len(candidats))]
        _, choisi = random.choice(rcl)
        tournee.insert(-1, choisi)
        clients_restants.remove(choisi)
        k = (k + 1) % nb_vehicules

    return tournees


def recherche_tabou(G, solution_initiale, taille_tabou, iter_sans_amelioration_max):
    nb_iter = 0
    liste_tabou = deque(maxlen=taille_tabou)

    solution_courante = solution_initiale
    meilleure_globale = solution_initiale
    valeur_meilleure_globale = cout_solution(G, solution_initiale)

    historique = [valeur_meilleure_globale]

    while nb_iter < iter_sans_amelioration_max:
        valeur_meilleure = float('inf')
        meilleure = None

        for voisin in voisinage(solution_courante):
            voisin_hashable = tuple(tuple(t) for t in voisin)
            val_voisin = cout_solution(G, voisin)

            est_tabou = voisin_hashable in liste_tabou
            aspiration = val_voisin < valeur_meilleure_globale

            if not est_tabou or aspiration:
                if val_voisin < valeur_meilleure:
                    valeur_meilleure = val_voisin
                    meilleure = voisin

        if meilleure is None:
            break

        if valeur_meilleure < valeur_meilleure_globale:
            meilleure_globale = meilleure
            valeur_meilleure_globale = valeur_meilleure
            nb_iter = 0
        else:
            nb_iter += 1

        solution_courante = meilleure
        liste_tabou.append(tuple(tuple(t) for t in solution_courante))
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


def multi_start_sac_a_dos(G, nb_restarts, m=3, k_rcl=3):
    meilleure_globale = None
    cout_meilleure_globale = float('inf')
    couts_finaux = []

    for restart in range(nb_restarts):
        solution = glouton(G, m, k_rcl=k_rcl)
        cout = cout_solution(G, solution)
        couts_finaux.append(cout)

        print(f"Restart {restart + 1}/{nb_restarts} : coût initial = {cout:.2f}")

        if cout < cout_meilleure_globale:
            meilleure_globale = solution
            cout_meilleure_globale = cout

    return meilleure_globale, couts_finaux


def multi_start_tabou(G, nb_restarts, taille_tabou, iter_max, m=3, k_rcl=3):
    meilleure_globale = None
    cout_meilleure_globale = float('inf')
    historiques = []
    couts_finaux = []

    for restart in range(nb_restarts):
        solution_initiale = glouton(G, m, k_rcl=k_rcl)
        cout_initial = cout_solution(G, solution_initiale)

        meilleure, historique = recherche_tabou(G, solution_initiale, taille_tabou, iter_max)
        cout_finale = cout_solution(G, meilleure)

        historiques.append(historique)
        couts_finaux.append(cout_finale)

        print(f"Restart {restart + 1}/{nb_restarts} : coût initial = {cout_initial:.2f} → coût final = {cout_finale:.2f}")

        if cout_finale < cout_meilleure_globale:
            meilleure_globale = meilleure
            cout_meilleure_globale = cout_finale

    return meilleure_globale, historiques, couts_finaux


# Affichage

G = random_graph(40, k_voisins=3, taux_fermeture=0.1, taux_surcout=0.08, complet=True)

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

print("\n" + "=" * 50)
print("MULTI-START SAC À DOS")
print("=" * 50)

# ============================================================
# MULTI-START SAC À DOS (baseline glouton pur)
# ============================================================

meilleure_sac, couts_sac = multi_start_sac_a_dos(G, nb_restarts=5, m=3, k_rcl=3)

print(f"\n=== RÉSULTATS SAC À DOS ===")
print(f"Coût minimum trouvé : {min(couts_sac):.2f}")
print(f"Coût maximum trouvé : {max(couts_sac):.2f}")
print(f"Coût moyen          : {sum(couts_sac)/len(couts_sac):.2f}")
print(f"\nMeilleure solution :")
for k, tournee in enumerate(meilleure_sac, start=1):
    print(f"  Véhicule {k} : {tournee}")

# ============================================================
# MULTI-START DU TABOU
# ============================================================

print("=" * 50)
print("MULTI-START TABOU")
print("=" * 50)

meilleure, historiques, couts_finaux = multi_start_tabou(
    G,
    nb_restarts=5,
    taille_tabou=20,
    iter_max=50,
    m=3,
    k_rcl=3
)

print(f"\n=== RÉSULTATS TABOU ===")
print(f"Coût minimum trouvé : {min(couts_finaux):.2f}")
print(f"Coût maximum trouvé : {max(couts_finaux):.2f}")
print(f"Coût moyen          : {sum(couts_finaux)/len(couts_finaux):.2f}")
print(f"\nMeilleure solution :")
for k, tournee in enumerate(meilleure, start=1):
    print(f"  Véhicule {k} : {tournee}")

plt.figure(figsize=(12, 6))
for i, hist in enumerate(historiques):
    plt.plot(hist, alpha=0.5, label=f'Restart {i+1}')
plt.xlabel("Itération")
plt.ylabel("Meilleur coût")
plt.title("Convergence du multi-start tabou")
plt.legend()
plt.grid(True)
plt.show()

# ============================================================
# COMPARAISON (les deux variables sont maintenant définies)
# ============================================================

plt.figure(figsize=(10, 5))
plt.bar(
    [f"T{i+1}" for i in range(len(couts_finaux))] +
    [f"S{i+1}" for i in range(len(couts_sac))],
    couts_finaux + couts_sac,
    color=['steelblue'] * len(couts_finaux) + ['coral'] * len(couts_sac)
)
plt.axhline(min(couts_finaux), color='steelblue', linestyle='--', linewidth=1, label=f'Tabou min = {min(couts_finaux):.1f}')
plt.axhline(min(couts_sac), color='coral', linestyle='--', linewidth=1, label=f'Sac à dos min = {min(couts_sac):.1f}')
plt.ylabel("Coût de la solution")
plt.title("Comparaison multi-start tabou vs multi-start sac à dos")
plt.legend()
plt.show()