"""Simulated annealing and its multi-start wrapper.

Worse neighbours are accepted with probability ``exp(-delta / T)`` to escape
local minima; the temperature decreases geometrically (``T *= alpha``).
"""

import copy
import math
import random

from .core import cout_solution, voisinage
from .greedy import glouton


def recuit_simule(G, solution_initiale, T_initial=100.0, T_final=0.01, alpha=0.99, iter_par_palier=50):
    """Simulated annealing for the VRPR problem."""
    solution_courante = copy.deepcopy(solution_initiale)
    meilleure_globale = copy.deepcopy(solution_initiale)

    cout_courant = cout_solution(G, solution_courante)
    valeur_meilleure_globale = cout_courant

    T = T_initial
    historique = [valeur_meilleure_globale]

    while T > T_final:
        for _ in range(iter_par_palier):
            voisins = voisinage(G, solution_courante)
            if not voisins:
                continue

            voisin = random.choice(voisins)
            val_voisin = cout_solution(G, voisin)

            delta = val_voisin - cout_courant

            if delta < 0 or random.random() < math.exp(-delta / T):
                solution_courante = voisin
                cout_courant = val_voisin

                if cout_courant < valeur_meilleure_globale:
                    meilleure_globale = copy.deepcopy(solution_courante)
                    valeur_meilleure_globale = cout_courant

        T *= alpha  # Refroidissement géométrique
        historique.append(valeur_meilleure_globale)

    return meilleure_globale, historique


def multi_start_recuit(G, nb_restarts, m=3, k_rcl=3):
    meilleure_globale = None
    cout_meilleure_globale = float('inf')
    historiques = []
    couts_initiaux = []
    couts_finaux = []

    print("\n" + "=" * 50)
    print("MULTI-START RECUIT SIMULÉ")
    print("=" * 50)

    for restart in range(nb_restarts):
        sol_init = glouton(G, m, k_rcl=k_rcl)
        cout_initial = cout_solution(G, sol_init)

        if cout_initial == float('inf'):
            continue

        meilleure, historique = recuit_simule(G, sol_init)
        cout_final = cout_solution(G, meilleure)

        historiques.append(historique)
        couts_initiaux.append(cout_initial)
        couts_finaux.append(cout_final)

        print(f"Restart {restart + 1}/{nb_restarts} : coût initial = {cout_initial:.2f} → coût final = {cout_final:.2f}")

        if cout_final < cout_meilleure_globale:
            meilleure_globale = meilleure
            cout_meilleure_globale = cout_final

    return meilleure_globale, historiques, couts_initiaux, couts_finaux
