"""Demo entry point for the VRPR package.

Generates one instance and runs the four approaches once.

    python main.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from vrpr import (
    random_graph,
    multi_start_glouton,
    multi_start_tabou,
    multi_start_recuit,
    genetic_algorithm_vrp_advanced,
)


def main():
    G = random_graph(40, k_voisins=3, taux_fermeture=0.1, taux_surcout=0.08, complet=True)

    print("\n=== MULTI-START GLOUTON ===")
    _, couts = multi_start_glouton(G, nb_restarts=5, m=3, k_rcl=1)
    print(f"Meilleur coût : {min(couts):.2f}")

    print("\n=== MULTI-START TABOU ===")
    _, _, couts = multi_start_tabou(G, nb_restarts=3, taille_tabou=20, iter_max=50, vehicule=3, k_rcl=5)
    print(f"Meilleur coût : {min(couts):.2f}")

    print("\n=== MULTI-START RECUIT SIMULÉ ===")
    _, _, _, couts = multi_start_recuit(G, nb_restarts=3, m=3)
    print(f"Meilleur coût : {min(couts):.2f}")

    print("\n=== ALGORITHME GÉNÉTIQUE ===")
    _, cout, initial = genetic_algorithm_vrp_advanced(G, num_vehicles=3, pop_size=100, generations=300, taux_mutation=0.4)
    print(f"Coût initial : {initial:.2f} → coût final : {cout:.2f}")


if __name__ == "__main__":
    main()
