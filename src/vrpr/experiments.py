"""Experimental design (OFAT) and cross-algorithm comparison.

Runs the four approaches on randomly generated instances of increasing size
and reports cost / runtime, plus the quality gain of each metaheuristic over
the greedy baseline.
"""

import io
import time
import contextlib

import numpy as np
import matplotlib.pyplot as plt

from .graph import random_graph
from .greedy import multi_start_glouton
from .tabu import multi_start_tabou
from .annealing import multi_start_recuit
from .genetic import genetic_algorithm_vrp_advanced

PARAMS = {
    "Glouton": {
        "nb_restarts": 5,
        "k_rcl":       1,
    },
    "Tabou": {
        "nb_restarts":  2,
        "taille_tabou": 20,
        "iter_max":     20,
        "k_rcl":        5,
        "vehicule":     3,
    },
    "Recuit": {
        "nb_restarts":     2,
        "T_initial":       100.0,
        "T_final":         1.0,
        "alpha":           0.90,
        "iter_par_palier": 20,
        "k_rcl":           3,
        "m":               3,
    },
    "Génétique": {
        "pop_size":      30,
        "generations":   50,
        "taux_mutation": 0.4,
        "num_vehicles":  3,
    },
}

TAILLES = [10, 20, 30]
N_INSTANCES = 3
COULEURS = {
    "Glouton":   "#e67e22",
    "Tabou":     "#2980b9",
    "Recuit":    "#27ae60",
    "Génétique": "#8e44ad",
}


def run_glouton(G, params):
    debut = time.perf_counter()
    _, couts = multi_start_glouton(G, nb_restarts=params["nb_restarts"], k_rcl=params["k_rcl"], m=3)
    duree = time.perf_counter() - debut
    valides = [c for c in couts if c != float('inf')]
    return (min(valides) if valides else float('inf')), duree


def run_tabou(G, params):
    debut = time.perf_counter()
    _, _, couts = multi_start_tabou(
        G, nb_restarts=params["nb_restarts"], taille_tabou=params["taille_tabou"],
        iter_max=params["iter_max"], vehicule=params["vehicule"], k_rcl=params["k_rcl"],
    )
    duree = time.perf_counter() - debut
    valides = [c for c in couts if c != float('inf')]
    return (min(valides) if valides else float('inf')), duree


def run_recuit(G, params):
    debut = time.perf_counter()
    _, _, _, couts = multi_start_recuit(G, nb_restarts=params["nb_restarts"], m=params["m"], k_rcl=params["k_rcl"])
    duree = time.perf_counter() - debut
    valides = [c for c in couts if c != float('inf')]
    return (min(valides) if valides else float('inf')), duree


def run_genetique(G, params):
    debut = time.perf_counter()
    _, cout, _ = genetic_algorithm_vrp_advanced(
        G, num_vehicles=params["num_vehicles"], pop_size=params["pop_size"],
        generations=params["generations"], taux_mutation=params["taux_mutation"],
    )
    duree = time.perf_counter() - debut
    return cout, duree


RUNNERS = {
    "Glouton":   run_glouton,
    "Tabou":     run_tabou,
    "Recuit":    run_recuit,
    "Génétique": run_genetique,
}


def run_comparaison():
    resultats = {algo: {t: {"couts": [], "temps": []} for t in TAILLES} for algo in PARAMS}

    for taille in TAILLES:
        print(f"{taille} villes...", end=" ", flush=True)
        for inst in range(N_INSTANCES):
            G = random_graph(vertice_count=taille, k_voisins=4, taux_fermeture=0.1, taux_surcout=0.08, complet=True)
            for algo, params in PARAMS.items():
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        cout, duree = RUNNERS[algo](G, params)
                    resultats[algo][taille]["couts"].append(cout)
                    resultats[algo][taille]["temps"].append(duree)
                except Exception:
                    resultats[algo][taille]["couts"].append(float('inf'))
                    resultats[algo][taille]["temps"].append(0)
    return resultats


def tracer_resultats(resultats):
    fig2, ax3 = plt.subplots(figsize=(10, 5))
    fig2.suptitle("Gain de qualité par rapport au glouton (baseline)", fontsize=12, fontweight='bold')

    algos_compare = ["Tabou", "Recuit", "Génétique"]
    largeur = 0.22
    x = np.arange(len(TAILLES))

    for idx, algo in enumerate(algos_compare):
        gains = []
        for t in TAILLES:
            cg = [c for c in resultats["Glouton"][t]["couts"] if c != float('inf')]
            ca = [c for c in resultats[algo][t]["couts"] if c != float('inf')]
            gains.append((np.mean(cg) - np.mean(ca)) / np.mean(cg) * 100 if cg and ca else 0)

        offset = (idx - 1) * largeur
        bars = ax3.bar(x + offset, gains, width=largeur, color=COULEURS[algo], alpha=0.85, edgecolor='white', label=algo)

        for bar, val in zip(bars, gains):
            va = 'bottom' if val >= 0 else 'top'
            ypos = bar.get_height() + 0.3 if val >= 0 else bar.get_height() - 0.3
            color = 'black' if val >= 0 else 'crimson'
            ax3.text(bar.get_x() + bar.get_width() / 2, ypos, f'{val:+.1f}%',
                     ha='center', va=va, fontsize=9, fontweight='bold', color=color)

    ax3.axhline(0, color='black', linewidth=1.2)
    ax3.axhspan(-100, 0, alpha=0.05, color='red')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"{t} villes" for t in TAILLES], fontsize=11)
    ax3.set_ylabel("Gain par rapport au glouton (%)")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()


def resumer_resultats(resultats):
    print("\n" + "=" * 65)
    print(f"  {'Algo':>10}  {'Taille':>6}  {'Min':>8}  {'Moy':>8}  {'Std':>8}  {'Temps':>8}")
    print("=" * 65)
    for taille in TAILLES:
        for algo in PARAMS:
            couts = [c for c in resultats[algo][taille]["couts"] if c != float('inf')]
            tps = resultats[algo][taille]["temps"]
            if couts:
                print(f"  {algo:>10}  {taille:>6}  {min(couts):>8.1f}  "
                      f"{np.mean(couts):>8.1f}  {np.std(couts):>8.1f}  {np.mean(tps):>7.1f}s")
        print()

    print("=" * 65)
    print("  GAIN PAR RAPPORT AU GLOUTON")
    print("=" * 65)
    for taille in TAILLES:
        cg = [c for c in resultats["Glouton"][taille]["couts"] if c != float('inf')]
        if not cg:
            continue
        moy_g = np.mean(cg)
        print(f"\n  {taille} villes (glouton = {moy_g:.1f}) :")
        for algo in ["Tabou", "Recuit", "Génétique"]:
            ca = [c for c in resultats[algo][taille]["couts"] if c != float('inf')]
            if ca:
                gain = (moy_g - np.mean(ca)) / moy_g * 100
                print(f"    {algo:>10} → moy={np.mean(ca):.1f}  gain={gain:+.1f}%")


if __name__ == "__main__":
    resumer_resultats(run_comparaison())
