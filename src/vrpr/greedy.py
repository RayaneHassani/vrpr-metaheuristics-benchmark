"""Greedy initial-solution generator (GRASP-style) and its multi-start wrapper.

Round-robin construction: each vehicle adds the cheapest reachable client in
turn. Randomisation comes from a restricted candidate list of size ``k_rcl``.
"""

import random

from .core import cout_solution


def glouton(G, nb_vehicules, k_rcl=1):
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


def multi_start_glouton(G, nb_restarts, m=3, k_rcl=3):
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
