"""Tabu search and its multi-start wrapper.

Short-term memory (the tabu list) forbids revisiting recent solutions, with an
aspiration criterion that overrides the ban when a tabu move beats the global
best. Multi-start restarts from different GRASP greedy solutions.
"""

from collections import deque

from .core import cout_solution, voisinage
from .greedy import glouton


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

        for voisin in voisinage(G, solution_courante):
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


def multi_start_tabou(G, nb_restarts, taille_tabou, iter_max, vehicule=3, k_rcl=3):
    meilleure_globale = None
    cout_meilleure_globale = float('inf')
    historiques = []
    couts_finaux = []

    for restart in range(nb_restarts):
        solution_initiale = glouton(G, vehicule, k_rcl=k_rcl)
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
